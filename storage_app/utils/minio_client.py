"""
minio_client.py

Provides functions for connecting to and interacting with MinIO.
Includes operations like creating buckets, uploading, and retrieving objects.
"""

# VERSION 2.1.2

"""
minio_client.py

Provides functions for connecting to and interacting with MinIO.
Includes operations like creating buckets, uploading, and retrieving objects.
"""

import logging, time
from minio import Minio
from minio.error import S3Error
from django.conf import settings

logger = logging.getLogger(__name__)

# Convert endpoints to a list if they're comma-separated in settings
if isinstance(settings.MINIO_ENDPOINTS, str):
    MINIO_ENDPOINTS = [ep.strip() for ep in settings.MINIO_ENDPOINTS.split(',')]
else:
    MINIO_ENDPOINTS = settings.MINIO_ENDPOINTS

print(f"Available MinIO endpoints: {MINIO_ENDPOINTS}")

def get_minio_client(endpoint=None):
    """
    Returns a MinIO client instance for the given endpoint.
    If no endpoint is specified, tries all available endpoints.
    """

    for ep in MINIO_ENDPOINTS:
        try:
            ep = ep.replace("http://", "").replace("https://", "")
            print(f"Attempting to connect to MinIO endpoint: {ep}")
            
            client = Minio(
                ep,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=False
            )
            
            # Test connection
            client.list_buckets()
            print(f"Successfully connected to MinIO endpoint: {ep}")
            return client
        except Exception as e:
            print(f"Failed to connect to endpoint {ep}: {e}")
            continue
    
    raise Exception("All MinIO endpoints are unreachable!")


def download_object_with_fallback(bucket_name, object_name, target_file, retries=1, delay=1):
    """
    Downloads an object using multiple endpoints with retry logic.
    """
    for ep in MINIO_ENDPOINTS:
        print(f"Attempting download from endpoint: {ep}")
        
        for attempt in range(retries):
            try:
                client = get_minio_client(ep)
                print(f"Attempt {attempt + 1}: Downloading {object_name} from {ep}")
                
                client.fget_object(bucket_name, object_name, target_file)
                print(f"Successfully downloaded {object_name} using endpoint: {ep}")
                return target_file
                
            except Exception as e:
                print(f"Download attempt {attempt + 1} failed on {ep}: {e}")
                if attempt < retries - 1:  # Don't sleep on the last attempt
                    # time.sleep(delay)
                    print(f"Sleeping for {delay} seconds before retrying...")
                continue
        
        print(f"All attempts failed for endpoint {ep}, trying next endpoint...")
    
    print("Failed to download file from all endpoints")
    return None


def upload_object(bucket_name, object_name, file_path):
    """
    Uploads an object with automatic fallback on failure.
    """
    for ep in MINIO_ENDPOINTS:
        print(f"Attempting upload to endpoint: {ep}")
        try:
            client = get_minio_client(ep)
            
            # Ensure bucket exists
            if not client.bucket_exists(bucket_name):
                print(f"Creating bucket {bucket_name} on endpoint {ep}")
                client.make_bucket(bucket_name)
            
            result = client.fput_object(bucket_name, object_name, file_path)
            print(f"Successfully uploaded {object_name} to {bucket_name} via {ep}")
            return result
            
        except Exception as e:
            print(f"Upload failed on {ep}: {e}")
            continue
    
    print("Failed to upload file to any endpoint")
    return None









