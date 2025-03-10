import os
import io
import logging
import random
import urllib3
from typing import List, Dict, Tuple, Optional
from minio import Minio
from minio.error import S3Error

class MinIOClusterManager:
    def __init__(self, 
                 access_key: str = 'admin', 
                 secret_key: str = 'adminadmin', 
                 secure: bool = False):
        """
        Initialize MinIO Cluster Manager
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Credentials and security
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure

        # Predefined nodes in your cluster
        self.nodes = [
            {'host': 'localhost:9000', 'alias': 'minio1', 'status': 'active'},
            {'host': 'localhost:9002', 'alias': 'minio2', 'status': 'active'},
            {'host': 'localhost:9004', 'alias': 'minio3', 'status': 'active'},
            {'host': 'localhost:9006', 'alias': 'minio4', 'status': 'active'},
            {'host': 'localhost:9008', 'alias': 'minio5', 'status': 'active'}
        ]
        
        # Disable SSL warnings if not using secure connection
        if not secure:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _create_client(self, node: Dict) -> Minio:
        """
        Create a MinIO client for a specific node
        """
        return Minio(
            node['host'], 
            access_key=self.access_key, 
            secret_key=self.secret_key, 
            secure=self.secure
        )

    def get_available_nodes(self) -> List[str]:
        """
        Get list of currently available nodes
        """
        available_nodes = []
        for node in self.nodes:
            try:
                client = self._create_client(node)
                # Try to list buckets to verify connection
                client.list_buckets()
                available_nodes.append(node['alias'])
            except Exception as e:
                self.logger.error(f"Node {node['alias']} not available: {e}")
        
        return available_nodes

    def upload_chunk(self, 
                     bucket_name: str, 
                     object_name: str, 
                     data: io.BytesIO, 
                     length: int) -> str:
        """
        Upload a chunk to an available node
        """
        # Get available nodes
        available_nodes = self.get_available_nodes()
        
        if not available_nodes:
            raise ValueError("No MinIO nodes available for upload")
        
        # Select a random available node
        selected_node_alias = random.choice(available_nodes)
        selected_node = next(node for node in self.nodes if node['alias'] == selected_node_alias)
        
        # Create client for selected node
        client = self._create_client(selected_node)
        
        # Ensure bucket exists
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        # Reset data stream position
        data.seek(0)
        
        # Upload chunk
        client.put_object(
            bucket_name, 
            object_name, 
            data, 
            length
        )
        
        return selected_node_alias

    def download_chunk(self, 
                       bucket_name: str, 
                       object_name: str) -> Tuple[io.BytesIO, str]:
        """
        Download a chunk from available nodes
        """
        available_nodes = self.get_available_nodes()
        
        for node_alias in available_nodes:
            try:
                # Find the node
                node = next(node for node in self.nodes if node['alias'] == node_alias)
                
                # Create client
                client = self._create_client(node)
                
                # Attempt to download
                data = client.get_object(bucket_name, object_name)
                
                return data, node_alias
            
            except Exception as e:
                self.logger.error(f"Failed to download from node {node_alias}: {e}")
                continue
        
        raise ValueError(f"Chunk {object_name} not found in any available node")

# Singleton instance
minio_cluster = MinIOClusterManager()




