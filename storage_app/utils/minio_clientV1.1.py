# # # """
# # # minio_client.py

# # # Provides functions for connecting to and interacting with MinIO.
# # # Includes operations like creating buckets, uploading, and retrieving objects.
# # # """

# # # # VERSION 2.1.2

# # # """
# # # minio_client.py

# # # Provides functions for connecting to and interacting with MinIO.
# # # Includes operations like creating buckets, uploading, and retrieving objects.
# # # """

# # # import logging, time
# # # from minio import Minio
# # # from minio.error import S3Error
# # # from django.conf import settings

# # # logger = logging.getLogger(__name__)

# # # # Convert endpoints to a list if they're comma-separated in settings
# # # if isinstance(settings.MINIO_ENDPOINTS, str):
# # #     MINIO_ENDPOINTS = [ep.strip() for ep in settings.MINIO_ENDPOINTS.split(',')]
# # # else:
# # #     MINIO_ENDPOINTS = settings.MINIO_ENDPOINTS

# # # print(f"Available MinIO endpoints: {MINIO_ENDPOINTS}")

# # # def get_minio_client(endpoint=None):
# # #     """
# # #     Returns a MinIO client instance for the given endpoint.
# # #     If no endpoint is specified, tries all available endpoints.
# # #     """

# # #     for ep in MINIO_ENDPOINTS:
# # #         try:
# # #             ep = ep.replace("http://", "").replace("https://", "")
# # #             print(f"Attempting to connect to MinIO endpoint: {ep}")
            
# # #             client = Minio(
# # #                 ep,
# # #                 access_key=settings.MINIO_ACCESS_KEY,
# # #                 secret_key=settings.MINIO_SECRET_KEY,
# # #                 secure=False
# # #             )
            
# # #             # Test connection
# # #             client.list_buckets()
# # #             print(f"Successfully connected to MinIO endpoint: {ep}")
# # #             return client
# # #         except Exception as e:
# # #             print(f"Failed to connect to endpoint {ep}: {e}")
# # #             continue
    
# # #     raise Exception("All MinIO endpoints are unreachable!")


# # # def download_object_with_fallback(bucket_name, object_name, target_file, retries=1, delay=1):
# # #     """
# # #     Downloads an object using multiple endpoints with retry logic.
# # #     """
# # #     for ep in MINIO_ENDPOINTS:
# # #         print(f"Attempting download from endpoint: {ep}")
        
# # #         for attempt in range(retries):
# # #             try:
# # #                 client = get_minio_client(ep)
# # #                 print(f"Attempt {attempt + 1}: Downloading {object_name} from {ep}")
                
# # #                 client.fget_object(bucket_name, object_name, target_file)
# # #                 print(f"Successfully downloaded {object_name} using endpoint: {ep}")
# # #                 return target_file
                
# # #             except Exception as e:
# # #                 print(f"Download attempt {attempt + 1} failed on {ep}: {e}")
# # #                 if attempt < retries - 1:  # Don't sleep on the last attempt
# # #                     # time.sleep(delay)
# # #                     print(f"Sleeping for {delay} seconds before retrying...")
# # #                 continue
        
# # #         print(f"All attempts failed for endpoint {ep}, trying next endpoint...")
    
# # #     print("Failed to download file from all endpoints")
# # #     return None


# # # def upload_object(bucket_name, object_name, file_path):
# # #     """
# # #     Uploads an object with automatic fallback on failure.
# # #     """
# # #     for ep in MINIO_ENDPOINTS:
# # #         print(f"Attempting upload to endpoint: {ep}")
# # #         try:
# # #             client = get_minio_client(ep)
            
# # #             # Ensure bucket exists
# # #             if not client.bucket_exists(bucket_name):
# # #                 print(f"Creating bucket {bucket_name} on endpoint {ep}")
# # #                 client.make_bucket(bucket_name)
            
# # #             result = client.fput_object(bucket_name, object_name, file_path)
# # #             print(f"Successfully uploaded {object_name} to {bucket_name} via {ep}")
# # #             return result
            
# # #         except Exception as e:
# # #             print(f"Upload failed on {ep}: {e}")
# # #             continue
    
# # #     print("Failed to upload file to any endpoint")
# # #     return None









# # # VERSION 2.1.3

# # """
# # minio_client.py
# # Version 2.1.4
# # Simplified version with last successful node tracking
# # """

# # import logging, json, os
# # from minio import Minio
# # from minio.error import S3Error
# # from django.conf import settings

# # logger = logging.getLogger(__name__)

# # # Path for storing last successful node information
# # LAST_NODE_FILE = os.path.join(settings.BASE_DIR, 'storage_app', 'utils', 'last_successful_node.json')

# # # Convert endpoints to a list if they're comma-separated in settings
# # if isinstance(settings.MINIO_ENDPOINTS, str):
# #     MINIO_ENDPOINTS = [ep.strip() for ep in settings.MINIO_ENDPOINTS.split(',')]
# # else:
# #     MINIO_ENDPOINTS = settings.MINIO_ENDPOINTS

# # def save_last_successful_node(endpoint):
# #     """Save the last successful node to a local file"""
# #     try:
# #         with open(LAST_NODE_FILE, 'w') as f:
# #             json.dump({'last_node': endpoint}, f)
# #         print(f"Saved last successful node: {endpoint}")
# #     except Exception as e:
# #         print(f"Failed to save last successful node: {e}")

# # def get_last_successful_node():
# #     """Retrieve the last successful node from local storage"""
# #     try:
# #         if os.path.exists(LAST_NODE_FILE):
# #             with open(LAST_NODE_FILE, 'r') as f:
# #                 data = json.load(f)
# #                 return data.get('last_node')
# #     except Exception as e:
# #         print(f"Failed to read last successful node: {e}")
# #     return None

# # def get_ordered_endpoints():
# #     """Returns endpoints list with last successful node first"""
# #     endpoints = MINIO_ENDPOINTS.copy()
# #     last_node = get_last_successful_node()
    
# #     if last_node and last_node in endpoints:
# #         # Move last successful node to the front of the list
# #         endpoints.remove(last_node)
# #         endpoints.insert(0, last_node)
# #         print(f"Prioritizing last successful node: {last_node}")
    
# #     return endpoints

# # def get_minio_client(endpoint=None):
# #     """
# #     Returns a MinIO client instance for the given endpoint.
# #     If no endpoint is specified, tries all available endpoints.
# #     """
# #     endpoints_to_try = [endpoint] if endpoint else get_ordered_endpoints()

# #     for ep in endpoints_to_try:
# #         try:
# #             ep = ep.replace("http://", "").replace("https://", "")
# #             print(f"Attempting to connect to MinIO endpoint: {ep}")
            
# #             client = Minio(
# #                 ep,
# #                 access_key=settings.MINIO_ACCESS_KEY,
# #                 secret_key=settings.MINIO_SECRET_KEY,
# #                 secure=False
# #             )
            
# #             # Test connection
# #             client.list_buckets()
# #             print(f"Successfully connected to MinIO endpoint: {ep}")
# #             save_last_successful_node(ep)
# #             return client
# #         except Exception as e:
# #             print(f"Failed to connect to endpoint {ep}: {e}")
# #             continue
    
# #     raise Exception("All MinIO endpoints are unreachable!")

# # def upload_object(bucket_name, object_name, file_path):
# #     """
# #     Uploads an object with automatic fallback.
# #     """
# #     for ep in get_ordered_endpoints():
# #         print(f"Attempting upload to endpoint: {ep}")
# #         try:
# #             client = get_minio_client(ep)
            
# #             # Ensure bucket exists
# #             if not client.bucket_exists(bucket_name):
# #                 print(f"Creating bucket {bucket_name} on endpoint {ep}")
# #                 client.make_bucket(bucket_name)
            
# #             result = client.fput_object(bucket_name, object_name, file_path)
# #             print(f"Successfully uploaded {object_name} to {bucket_name} via {ep}")
# #             save_last_successful_node(ep)
# #             return result
            
# #         except Exception as e:
# #             print(f"Upload failed on {ep}: {e}")
# #             continue
    
# #     print("Failed to upload file to any endpoint")
# #     return None

# # def download_object_with_fallback(bucket_name, object_name, target_file):
# #     """
# #     Downloads an object using multiple endpoints.
# #     """
# #     for ep in get_ordered_endpoints():
# #         print(f"Attempting download from endpoint: {ep}")
# #         try:
# #             client = get_minio_client(ep)
# #             print(f"Downloading {object_name} from {ep}")
            
# #             client.fget_object(bucket_name, object_name, target_file)
# #             print(f"Successfully downloaded {object_name} using endpoint: {ep}")
# #             save_last_successful_node(ep)
# #             return target_file
            
# #         except Exception as e:
# #             print(f"Download failed on {ep}: {e}")
# #             continue
    
# #     print("Failed to download file from all endpoints")
# #     return None









# """
# minio_client.py
# Version 2.1.6
# Optimized node selection and connection handling
# """

# import logging, json, os
# from minio import Minio
# from minio.error import S3Error
# from django.conf import settings

# logger = logging.getLogger(__name__)

# # Path for storing last successful node information
# LAST_NODE_FILE = os.path.join(settings.BASE_DIR, 'storage_app', 'utils', 'last_successful_node.json')

# # Initialize endpoints
# if isinstance(settings.MINIO_ENDPOINTS, str):
#     MINIO_ENDPOINTS = [ep.strip() for ep in settings.MINIO_ENDPOINTS.split(',')]
# else:
#     MINIO_ENDPOINTS = settings.MINIO_ENDPOINTS

# def test_endpoint(endpoint):
#     """Test if an endpoint is accessible"""
#     if not endpoint:
#         return None
        
#     try:
#         ep = endpoint.replace("http://", "").replace("https://", "")
#         client = Minio(
#             ep,
#             access_key=settings.MINIO_ACCESS_KEY,
#             secret_key=settings.MINIO_SECRET_KEY,
#             secure=False
#         )
#         # Verify connection works
#         client.list_buckets()
#         return client
#     except Exception as e:
#         print(f"Failed to connect to {endpoint}: {e}")
#         return None

# def get_last_working_node():
#     """Get the last known working node from storage"""
#     try:
#         if os.path.exists(LAST_NODE_FILE):
#             with open(LAST_NODE_FILE, 'r') as f:
#                 data = json.load(f)
#                 last_node = data.get('last_node')
#                 # Verify this node is still in our endpoints list
#                 if last_node in MINIO_ENDPOINTS:
#                     return last_node
#     except Exception as e:
#         print(f"Error reading last working node: {e}")
#     return None

# def save_working_node(endpoint):
#     """Save a working node to storage"""
#     try:
#         with open(LAST_NODE_FILE, 'w') as f:
#             json.dump({'last_node': endpoint}, f)
#     except Exception as e:
#         print(f"Error saving working node: {e}")

# def get_minio_client():
#     """
#     Get a working MinIO client, prioritizing the last known working node
#     """
#     # First, try the last known working node
#     last_node = get_last_working_node()
#     if last_node:
#         print(f"Attempting connection to last working node: {last_node}")
#         client = test_endpoint(last_node)
#         if client:
#             print(f"Successfully connected to last working node: {last_node}")
#             return client
#         print("Last working node is no longer accessible")

#     # If last working node failed or doesn't exist, try other endpoints
#     remaining_endpoints = [ep for ep in MINIO_ENDPOINTS if ep != last_node]
#     for endpoint in remaining_endpoints:
#         print(f"Trying alternative endpoint: {endpoint}")
#         client = test_endpoint(endpoint)
#         if client:
#             print(f"Successfully connected to: {endpoint}")
#             save_working_node(endpoint)  # Save this as our new working node
#             return client

#     raise Exception("No MinIO endpoints are accessible!")

# def upload_object(bucket_name, object_name, file_path):
#     """Upload an object to MinIO"""
#     try:
#         client = get_minio_client()
        
#         # Ensure bucket exists
#         if not client.bucket_exists(bucket_name):
#             client.make_bucket(bucket_name)
#             print(f"Created bucket: {bucket_name}")
        
#         # Upload the file
#         result = client.fput_object(bucket_name, object_name, file_path)
#         print(f"Successfully uploaded: {object_name}")
#         return result
        
#     except Exception as e:
#         print(f"Upload failed: {e}")
#         return None

# def download_object_with_fallback(bucket_name, object_name, target_file):
#     """Download an object from MinIO"""
#     try:
#         client = get_minio_client()
        
#         # Download the file
#         client.fget_object(bucket_name, object_name, target_file)
#         print(f"Successfully downloaded: {object_name}")
#         return target_file
        
#     except Exception as e:
#         print(f"Download failed: {e}")
#         return None












"""
minio_client.py
Version 2.1.5
Fixed node fallback and local storage logic
"""

import logging, json, os
from minio import Minio
from minio.error import S3Error
from django.conf import settings

logger = logging.getLogger(__name__)

# Path for storing last successful node information
LAST_NODE_FILE = os.path.join(settings.BASE_DIR, 'storage_app', 'utils', 'last_successful_node.json')

# Convert endpoints to a list if they're comma-separated in settings
if isinstance(settings.MINIO_ENDPOINTS, str):
    MINIO_ENDPOINTS = [ep.strip() for ep in settings.MINIO_ENDPOINTS.split(',')]
else:
    MINIO_ENDPOINTS = settings.MINIO_ENDPOINTS

print(f"Available MinIO endpoints: {MINIO_ENDPOINTS}")

def save_last_successful_node(endpoint):
    """Save the last successful node to a local file"""
    try:
        with open(LAST_NODE_FILE, 'w') as f:
            json.dump({'last_node': endpoint}, f)
        print(f"Saved new last successful node: {endpoint}")
    except Exception as e:
        print(f"Failed to save last successful node: {e}")

def get_last_successful_node():
    """Retrieve the last successful node from local storage"""
    try:
        if os.path.exists(LAST_NODE_FILE):
            with open(LAST_NODE_FILE, 'r') as f:
                data = json.load(f)
                last_node = data.get('last_node')
                print(f"Retrieved last successful node: {last_node}")
                return last_node
    except Exception as e:
        print(f"Failed to read last successful node: {e}")
    return None

def get_ordered_endpoints():
    """
    Returns endpoints list with last successful node first, if it's available.
    If last successful node fails, it will be moved to the end of the list.
    """
    endpoints = MINIO_ENDPOINTS.copy()
    last_node = get_last_successful_node()
    
    if last_node and last_node in endpoints:
        # Move last successful node to the front
        endpoints.remove(last_node)
        endpoints.insert(0, last_node)
        print(f"Trying last successful node first: {last_node}")
    
    return endpoints

def test_endpoint(endpoint):
    """Test if an endpoint is accessible"""
    try:
        ep = endpoint.replace("http://", "").replace("https://", "")
        client = Minio(
            ep,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )
        # Test connection by listing buckets
        client.list_buckets()
        return client
    except Exception as e:
        print(f"Endpoint {endpoint} is not accessible: {e}")
        return None

def get_minio_client(endpoint=None):
    """
    Returns a working MinIO client instance.
    Tries endpoints in order, starting with the specified endpoint or last successful one.
    """
    # Get ordered list of endpoints to try
    endpoints_to_try = [endpoint] if endpoint else get_ordered_endpoints()
    
    # Try each endpoint until one works
    for ep in endpoints_to_try:
        if not ep:
            continue
            
        print(f"Attempting to connect to MinIO endpoint: {ep}")
        client = test_endpoint(ep)
        
        if client:
            print(f"Successfully connected to MinIO endpoint: {ep}")
            return client
        
    # If we get here, try any remaining endpoints
    remaining_endpoints = [ep for ep in MINIO_ENDPOINTS if ep not in endpoints_to_try]
    for ep in remaining_endpoints:
        print(f"Trying alternative endpoint: {ep}")
        client = test_endpoint(ep)
        
        if client:
            print(f"Successfully connected to alternative endpoint: {ep}")
            return client
    
    raise Exception("All MinIO endpoints are unreachable!")

# def upload_object(bucket_name, object_name, file_path):
#     """
#     Uploads an object with automatic fallback.
#     Updates last successful node upon successful upload.
#     """
#     for ep in get_ordered_endpoints():
#         print(f"Attempting upload to endpoint: {ep}")
#         try:
#             client = get_minio_client(ep)
#             if not client:
#                 print(f"Could not connect to {ep}, trying next endpoint...")
#                 continue
                
#             # Ensure bucket exists
#             if not client.bucket_exists(bucket_name):
#                 print(f"Creating bucket {bucket_name} on endpoint {ep}")
#                 client.make_bucket(bucket_name)
            
#             # Attempt upload
#             result = client.fput_object(bucket_name, object_name, file_path)
#             print(f"Successfully uploaded {object_name} to {bucket_name} via {ep}")
            
#             # Save this as the last successful node
#             save_last_successful_node(ep)
#             return result
            
#         except Exception as e:
#             print(f"Upload failed on {ep}: {e}")
#             continue
    
#     print("Failed to upload file to any endpoint")
#     return None

# def download_object_with_fallback(bucket_name, object_name, target_file):
#     """
#     Downloads an object using multiple endpoints.
#     Updates last successful node upon successful download.
#     """
#     for ep in get_ordered_endpoints():
#         print(f"Attempting download from endpoint: {ep}")
#         try:
#             client = get_minio_client(ep)
#             if not client:
#                 print(f"Could not connect to {ep}, trying next endpoint...")
#                 continue
            
#             # Attempt download
#             client.fget_object(bucket_name, object_name, target_file)
#             print(f"Successfully downloaded {object_name} using endpoint: {ep}")
            
#             # Save this as the last successful node
#             save_last_successful_node(ep)
#             return target_file
            
#         except Exception as e:
#             print(f"Download failed on {ep}: {e}")
#             continue
    
#     print("Failed to download file from all endpoints")
#     return None


