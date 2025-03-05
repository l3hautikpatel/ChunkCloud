"""
minio_client.py

Provides functions for connecting to and interacting with MinIO.
Includes operations like creating buckets, uploading, and retrieving objects.
"""

# myapp/minio_client.py

from minio import Minio
from django.conf import settings

# Create a MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False  # Set to True if using HTTPS
)

# Ensure the bucket exists
if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
    minio_client.make_bucket(settings.MINIO_BUCKET_NAME)


