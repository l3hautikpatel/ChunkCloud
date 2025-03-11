# # import os
# # import io
# # import logging
# # import random
# # import urllib3
# # from typing import List, Dict, Tuple, Optional
# # from minio import Minio
# # from minio.error import S3Error

# # class MinIOClusterManager:
# #     def __init__(self, 
# #                  access_key: str = 'admin', 
# #                  secret_key: str = 'adminadmin', 
# #                  secure: bool = False):
# #         """
# #         Initialize MinIO Cluster Manager
# #         """
# #         # Setup logging
# #         logging.basicConfig(level=logging.INFO)
# #         self.logger = logging.getLogger(__name__)

# #         # Credentials and security
# #         self.access_key = access_key
# #         self.secret_key = secret_key
# #         self.secure = secure

# #         # Predefined nodes in your cluster
# #         self.nodes = [
# #             {'host': 'localhost:9000', 'alias': 'minio1', 'status': 'active'},
# #             {'host': 'localhost:9002', 'alias': 'minio2', 'status': 'active'},
# #             {'host': 'localhost:9004', 'alias': 'minio3', 'status': 'active'},
# #             {'host': 'localhost:9006', 'alias': 'minio4', 'status': 'active'},
# #             {'host': 'localhost:9008', 'alias': 'minio5', 'status': 'active'}
# #         ]
        
# #         # Disable SSL warnings if not using secure connection
# #         if not secure:
# #             urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# #     def _create_client(self, node: Dict) -> Minio:
# #         """
# #         Create a MinIO client for a specific node
# #         """
# #         return Minio(
# #             node['host'], 
# #             access_key=self.access_key, 
# #             secret_key=self.secret_key, 
# #             secure=self.secure
# #         )

# #     def get_available_nodes(self) -> List[str]:
# #         """
# #         Get list of currently available nodes
# #         """
# #         available_nodes = []
# #         for node in self.nodes:
# #             try:
# #                 client = self._create_client(node)
# #                 # Try to list buckets to verify connection
# #                 client.list_buckets()
# #                 available_nodes.append(node['alias'])
# #             except Exception as e:
# #                 self.logger.error(f"Node {node['alias']} not available: {e}")
        
# #         return available_nodes

# #     def upload_chunk(self, 
# #                      bucket_name: str, 
# #                      object_name: str, 
# #                      data: io.BytesIO, 
# #                      length: int) -> str:
# #         """
# #         Upload a chunk to an available node
# #         """
# #         # Get available nodes
# #         available_nodes = self.get_available_nodes()
        
# #         if not available_nodes:
# #             raise ValueError("No MinIO nodes available for upload")
        
# #         # Select a random available node
# #         selected_node_alias = random.choice(available_nodes)
# #         selected_node = next(node for node in self.nodes if node['alias'] == selected_node_alias)
        
# #         # Create client for selected node
# #         client = self._create_client(selected_node)
        
# #         # Ensure bucket exists
# #         if not client.bucket_exists(bucket_name):
# #             client.make_bucket(bucket_name)
        
# #         # Reset data stream position
# #         data.seek(0)
        
# #         # Upload chunk
# #         client.put_object(
# #             bucket_name, 
# #             object_name, 
# #             data, 
# #             length
# #         )
        
# #         return selected_node_alias

# #     def download_chunk(self, 
# #                         bucket_name: str,
# #                         object_name: str) -> Tuple[io.BytesIO, str]:
# #         """
# #         Download a chunk from available nodes
# #         """
# #         available_nodes = self.get_available_nodes()
        
# #         for node_alias in available_nodes:
# #             try:
# #                 # Find the node
# #                 node = next(node for node in self.nodes if node['alias'] == node_alias)
                
# #                 # Create client
# #                 client = self._create_client(node)
                
# #                 # Attempt to download
# #                 data = client.get_object(bucket_name, object_name)
                
# #                 return data, node_alias
            
# #             except Exception as e:
# #                 self.logger.error(f"Failed to download from node {node_alias}: {e}")
# #                 continue
        
# #         raise ValueError(f"Chunk {object_name} not found in any available node")

# # # Singleton instance
# # minio_cluster = MinIOClusterManager()















# import os
# import io
# import logging
# import random
# import urllib3
# from typing import List, Dict, Tuple, Optional
# from minio import Minio
# from minio.error import S3Error

# class MinIOClusterManager:
#     def __init__(self, 
#                  access_key: str = 'admin', 
#                  secret_key: str = 'adminadmin', 
#                  secure: bool = False,
#                  connect_timeout: float = 2.0,  # Reduced from default
#                  retries: int = 1):            # Reduced from default (5)
#         """
#         Initialize MinIO Cluster Manager with reduced timeout and retries
#         """
#         # Setup logging
#         logging.basicConfig(level=logging.INFO)
#         self.logger = logging.getLogger(__name__)

#         # Credentials and security
#         self.access_key = access_key
#         self.secret_key = secret_key
#         self.secure = secure
        
#         # Connection settings
#         self.connect_timeout = connect_timeout
#         self.retries = retries

#         # Predefined nodes in your cluster
#         self.nodes = [
#             {'host': 'localhost:9000', 'alias': 'minio1', 'status': 'active'},
#             {'host': 'localhost:9002', 'alias': 'minio2', 'status': 'active'},
#             {'host': 'localhost:9004', 'alias': 'minio3', 'status': 'active'},
#             {'host': 'localhost:9006', 'alias': 'minio4', 'status': 'active'},
#             {'host': 'localhost:9008', 'alias': 'minio5', 'status': 'active'}
#         ]
        
#         # Disable SSL warnings if not using secure connection
#         if not secure:
#             urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#     def _create_client(self, node: Dict) -> Minio:
#         """
#         Create a MinIO client for a specific node with custom connection settings
#         """
#         # Create a custom HTTP client with reduced retries
#         http_client = urllib3.PoolManager(
#             timeout=urllib3.Timeout(connect=self.connect_timeout),
#             retries=urllib3.Retry(
#                 total=self.retries,
#                 backoff_factor=0.2,
#                 status_forcelist=[500, 502, 503, 504]
#             )
#         )
        
#         return Minio(
#             node['host'], 
#             access_key=self.access_key, 
#             secret_key=self.secret_key, 
#             secure=self.secure,
#             http_client=http_client
#         )

#     def get_available_nodes(self) -> List[str]:
#         """
#         Get list of currently available nodes
#         """
#         available_nodes = []
#         for node in self.nodes:
#             try:
#                 client = self._create_client(node)
#                 # Try to list buckets to verify connection
#                 client.list_buckets()
#                 available_nodes.append(node['alias'])
#             except Exception as e:
#                 self.logger.error(f"Node {node['alias']} not available: {e}")
        
#         return available_nodes

#     def upload_chunk(self, 
#                      bucket_name: str, 
#                      object_name: str, 
#                      data: io.BytesIO, 
#                      length: int) -> str:
#         """
#         Upload a chunk to an available node
#         """
#         # Get available nodes
#         available_nodes = self.get_available_nodes()
        
#         if not available_nodes:
#             raise ValueError("No MinIO nodes available for upload")
        
#         # Select a random available node
#         selected_node_alias = random.choice(available_nodes)
#         selected_node = next(node for node in self.nodes if node['alias'] == selected_node_alias)
        
#         # Create client for selected node
#         client = self._create_client(selected_node)
        
#         # Ensure bucket exists
#         if not client.bucket_exists(bucket_name):
#             client.make_bucket(bucket_name)
        
#         # Reset data stream position
#         data.seek(0)
        
#         # Upload chunk
#         client.put_object(
#             bucket_name, 
#             object_name, 
#             data, 
#             length
#         )
        
#         return selected_node_alias

#     def download_chunk(self, 
#                         bucket_name: str,
#                         object_name: str) -> Tuple[io.BytesIO, str]:
#         """
#         Download a chunk from available nodes
#         """
#         available_nodes = self.get_available_nodes()
        
#         for node_alias in available_nodes:
#             try:
#                 # Find the node
#                 node = next(node for node in self.nodes if node['alias'] == node_alias)
                
#                 # Create client
#                 client = self._create_client(node)
                
#                 # Attempt to download
#                 data = client.get_object(bucket_name, object_name)
                
#                 return data, node_alias
            
#             except Exception as e:
#                 self.logger.error(f"Failed to download from node {node_alias}: {e}")
#                 continue
        
#         raise ValueError(f"Chunk {object_name} not found in any available node")

# # Singleton instance
# minio_cluster = MinIOClusterManager()





















# # import os
# # import io
# # import logging
# # import random
# # import urllib3
# # from typing import List, Dict, Tuple, Optional
# # from minio import Minio
# # from minio.error import S3Error

# # class MinIOClusterManager:
# #     def __init__(self, 
# #                  access_key: str = 'admin', 
# #                  secret_key: str = 'adminadmin', 
# #                  secure: bool = False,
# #                  connect_timeout: float = 1.0,  # Even faster timeout
# #                  retries: int = 0,              # No retries
# #                  min_healthy_nodes: int = 1):   # Minimum nodes required
# #         """
# #         Initialize MinIO Cluster Manager with customizable resilience
# #         """
# #         # Setup logging
# #         logging.basicConfig(level=logging.INFO)
# #         self.logger = logging.getLogger(__name__)

# #         # Credentials and security
# #         self.access_key = access_key
# #         self.secret_key = secret_key
# #         self.secure = secure
        
# #         # Connection settings
# #         self.connect_timeout = connect_timeout
# #         self.retries = retries
# #         self.min_healthy_nodes = min_healthy_nodes

# #         # Predefined nodes in your cluster
# #         self.nodes = [
# #             {'host': 'localhost:9000', 'alias': 'minio1', 'status': 'unknown'},
# #             {'host': 'localhost:9002', 'alias': 'minio2', 'status': 'unknown'},
# #             {'host': 'localhost:9004', 'alias': 'minio3', 'status': 'unknown'},
# #             {'host': 'localhost:9006', 'alias': 'minio4', 'status': 'unknown'},
# #             {'host': 'localhost:9008', 'alias': 'minio5', 'status': 'unknown'}
# #         ]
        
# #         # Initialize node health cache with empty values
# #         self.node_health_cache = {}
        
# #         # Disable SSL warnings if not using secure connection
# #         if not secure:
# #             urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# #     def _create_client(self, node: Dict) -> Minio:
# #         """
# #         Create a MinIO client for a specific node with custom connection settings
# #         """
# #         # Create a custom HTTP client with minimal retries and fast timeout
# #         http_client = urllib3.PoolManager(
# #             timeout=urllib3.Timeout(connect=self.connect_timeout),
# #             retries=urllib3.Retry(
# #                 total=self.retries,
# #                 backoff_factor=0.1,
# #                 status_forcelist=[500, 502, 503, 504]
# #             )
# #         )
        
# #         return Minio(
# #             node['host'], 
# #             access_key=self.access_key, 
# #             secret_key=self.secret_key, 
# #             secure=self.secure,
# #             http_client=http_client
# #         )

# #     def get_available_nodes(self, force_check=False) -> List[str]:
# #         """
# #         Get list of currently available nodes, with optional caching
# #         """
# #         available_nodes = []
# #         healthy_nodes_count = 0
# #         warning_logged = False
        
# #         for node in self.nodes:
# #             # Skip checking already known unhealthy nodes unless force_check is True
# #             if not force_check and node['alias'] in self.node_health_cache:
# #                 if self.node_health_cache[node['alias']] == 'healthy':
# #                     available_nodes.append(node['alias'])
# #                     healthy_nodes_count += 1
# #                 continue
                
# #             try:
# #                 client = self._create_client(node)
# #                 # Try to list buckets to verify connection
# #                 client.list_buckets()
# #                 available_nodes.append(node['alias'])
# #                 node['status'] = 'active'
# #                 self.node_health_cache[node['alias']] = 'healthy'
# #                 healthy_nodes_count += 1
# #             except Exception as e:
# #                 # Log warning only once per function call to reduce log spam
# #                 if not warning_logged:
# #                     self.logger.warning(f"Node {node['alias']} not available: Connection refused")
# #                     warning_logged = True
# #                 node['status'] = 'inactive'
# #                 self.node_health_cache[node['alias']] = 'unhealthy'
        
# #         # Log cluster health status
# #         if healthy_nodes_count == 0:
# #             self.logger.error("CRITICAL: No MinIO nodes available in the cluster")
# #         elif healthy_nodes_count < 3:
# #             self.logger.warning(f"WARNING: Only {healthy_nodes_count}/5 MinIO nodes available - reduced redundancy")
        
# #         return available_nodes

# #     def upload_chunk(self, 
# #                      bucket_name: str, 
# #                      object_name: str, 
# #                      data: io.BytesIO, 
# #                      length: int) -> str:
# #         """
# #         Upload a chunk to an available node
# #         """
# #         # Get available nodes
# #         available_nodes = self.get_available_nodes()
        
# #         if not available_nodes:
# #             if self.min_healthy_nodes > 0:
# #                 raise ValueError("No MinIO nodes available for upload - check your cluster")
# #             else:
# #                 self.logger.critical("No MinIO nodes available, but continuing as min_healthy_nodes=0")
# #                 return "storage_unavailable"
        
# #         # Select a random available node
# #         selected_node_alias = random.choice(available_nodes)
# #         selected_node = next(node for node in self.nodes if node['alias'] == selected_node_alias)
        
# #         # Create client for selected node
# #         client = self._create_client(selected_node)
        
# #         # Ensure bucket exists
# #         if not client.bucket_exists(bucket_name):
# #             client.make_bucket(bucket_name)
        
# #         # Reset data stream position
# #         data.seek(0)
        
# #         # Upload chunk
# #         client.put_object(
# #             bucket_name, 
# #             object_name, 
# #             data, 
# #             length
# #         )
        
# #         return selected_node_alias

# #     def download_chunk(self, 
# #                         bucket_name: str,
# #                         object_name: str) -> Tuple[io.BytesIO, str]:
# #         """
# #         Download a chunk from available nodes
# #         """
# #         available_nodes = self.get_available_nodes()
        
# #         if not available_nodes:
# #             raise ValueError("CRITICAL: No MinIO nodes available for download - check your cluster")
        
# #         warning_logged = False
# #         for node_alias in available_nodes:
# #             try:
# #                 # Find the node
# #                 node = next(node for node in self.nodes if node['alias'] == node_alias)
                
# #                 # Create client
# #                 client = self._create_client(node)
                
# #                 # Attempt to download
# #                 data = client.get_object(bucket_name, object_name)
                
# #                 return data, node_alias
            
# #             except Exception as e:
# #                 # Log only one warning to reduce spam
# #                 if not warning_logged:
# #                     self.logger.warning(f"Failed to download from node {node_alias} - trying other nodes")
# #                     warning_logged = True
# #                 continue
        
# #         # If we have at least one node but chunk not found anywhere
# #         self.logger.error(f"Chunk {object_name} not found in any available node")
# #         raise ValueError(f"Chunk {object_name} not found in any of the {len(available_nodes)} available nodes")

# #     def refresh_node_status(self):
# #         """
# #         Force a refresh of all node statuses
# #         """
# #         self.node_health_cache = {}  # Clear cache
# #         return self.get_available_nodes(force_check=True)

# # # Singleton instance with custom settings
# # minio_cluster = MinIOClusterManager(
# #     connect_timeout=1.0,  # 1 second timeout
# #     retries=0,            # No retries
# #     min_healthy_nodes=1   # Requires at least 1 healthy node
# # )







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
                 secure: bool = False,
                 connect_timeout: float = 2.0,  # Reduced from default
                 retries: int = 1):            # Reduced from default (5)
        """
        Initialize MinIO Cluster Manager with reduced timeout and retries
        """
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Credentials and security
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        
        # Connection settings
        self.connect_timeout = connect_timeout
        self.retries = retries

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
        Create a MinIO client for a specific node with custom connection settings
        """
        # Create a custom HTTP client with reduced retries
        http_client = urllib3.PoolManager(
            timeout=urllib3.Timeout(connect=self.connect_timeout),
            retries=urllib3.Retry(
                total=self.retries,
                backoff_factor=0.2,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        
        return Minio(
            node['host'], 
            access_key=self.access_key, 
            secret_key=self.secret_key, 
            secure=self.secure,
            http_client=http_client
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