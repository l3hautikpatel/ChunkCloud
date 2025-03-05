# filesupdown.py

from minio import Minio
from django.conf import settings


# Create a MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False  # Set to True if using HTTPS
)

def upload_file(file, file_id):
    try:
        # Make sure bucket exists
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            
        # Upload the file
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            file_id,
            file,
            file.size
        )
        
        return f"{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{file_id}"
    except Exception as e:
        raise Exception(f"Error uploading file to MinIO: {e}")

def download_file(file_id):
    try:
        return minio_client.get_object(settings.MINIO_BUCKET_NAME, file_id)
    except Exception as e:
        raise Exception(f"Error downloading file: {e}")