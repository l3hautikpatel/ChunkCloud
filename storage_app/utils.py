# storage_app/utils.py

from minio import Minio

def get_minio_data():
    client = Minio(
        "localhost:9000",
        access_key="admin",
        secret_key="adminadmin",
        secure=False
    )
    # Example: List all buckets
    buckets = client.list_buckets()
    return buckets