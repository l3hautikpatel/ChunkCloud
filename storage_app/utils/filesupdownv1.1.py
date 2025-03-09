# filesupdown.py

# from minio import Minio
# from django.conf import settings


# # Create a MinIO client
# minio_client = Minio(
#     settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
#     access_key=settings.MINIO_ACCESS_KEY,
#     secret_key=settings.MINIO_SECRET_KEY,
#     secure=False  # Set to True if using HTTPS
# )

# def upload_file(file, file_id):
#     try:
#         # Make sure bucket exists
#         if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
#             minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            
#         # Upload the file
#         minio_client.put_object(
#             settings.MINIO_BUCKET_NAME,
#             file_id,
#             file,
#             file.size
#         )


#         # chuncker.chuck_file(file,file_id)
        
#         return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{file_id}"
#     except Exception as e:
#         raise Exception(f"Error uploading file to MinIO: {e}")

# def download_file(file_id):
#     try:
#         return minio_client.get_object(settings.MINIO_BUCKET_NAME, file_id)
#     except Exception as e:
#         raise Exception(f"Error downloading file: {e}")





# VERSION 2.0.1

import logging
from django.conf import settings
from minio.error import S3Error
from .minio_client import get_minio_client

logger = logging.getLogger(__name__)

def upload_file(file, file_id):
    """
    Uploads a file to MinIO using the primary and fallback endpoints.
    """
    for ep in settings.MINIO_ENDPOINTS:
        try:
            client = get_minio_client(endpoint=ep)

            # Ensure bucket exists
            if not client.bucket_exists(settings.MINIO_BUCKET_NAME):
                client.make_bucket(settings.MINIO_BUCKET_NAME)

            # Upload file
            client.put_object(
                settings.MINIO_BUCKET_NAME,
                file_id,
                file,
                file.size
            )

            logger.info(f"File uploaded successfully: {file_id} via {ep}")
            return f"{ep}/{settings.MINIO_BUCKET_NAME}/{file_id}"
        except S3Error as e:
            logger.warning(f"Upload failed on {ep}: {e}")
    
    raise Exception("Error: File upload failed on all endpoints.")

def download_file(file_id):
    """
    Downloads a file from MinIO using fallback endpoints.
    """
    for ep in settings.MINIO_ENDPOINTS:
        try:
            client = get_minio_client(endpoint=ep)
            return client.get_object(settings.MINIO_BUCKET_NAME, file_id)
        except S3Error as e:
            logger.warning(f"Download failed on {ep}: {e}")

    raise Exception("Error: File download failed on all endpoints.")
