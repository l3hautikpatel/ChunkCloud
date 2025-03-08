import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

def generate_file_id():
    """
    Generate a unique file ID using a combination of a UUID and timestamp.
    """
    return f"{uuid.uuid4().hex}_{int(now().timestamp())}"


class FileMetadata(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files")  
    file_id = models.CharField(max_length=100, unique=True, default=generate_file_id)  
    file_name = models.CharField(max_length=255)  # This will store filename with extension
    file_url = models.URLField(max_length=500, null=True)    # Add this field
    description = models.TextField(blank=True, null=True)  
    file_size = models.PositiveBigIntegerField()  
    uploaded_at = models.DateTimeField(auto_now_add=True)  
    last_downloaded_at = models.DateTimeField(blank=True, null=True)  

    def __str__(self):
        return f"{self.file_name} ({self.file_size} bytes) by {self.user.username}"
    

class FileChunk(models.Model):
    file = models.ForeignKey(FileMetadata, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField(help_text="Sequence number of this chunk")
    chunk_size = models.PositiveBigIntegerField(help_text="Size of this chunk in bytes")
    checksum = models.CharField(max_length=64, help_text="Checksum (e.g. MD5 or SHA256) to verify integrity")
    storage_node = models.CharField(max_length=50, help_text="Name of the MinIO server node e.g., minio-node1")
    object_key = models.CharField(max_length=255, help_text="Object key in MinIO where the chunk is stored")
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Meta:
    unique_together = ('file', 'chunk_index')  # ensures no duplicate chunks for a file

def __str__(self):
    return f"{self.file.file_name}_chunk_{self.chunk_index}"