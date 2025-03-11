# VERSION 2.1.1
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
    # User and File Identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="files")
    file_id = models.CharField(max_length=100, unique=True, default=generate_file_id)
    file_name = models.CharField(max_length=255)  # filename with extension
    
    # File Details
    file_url = models.URLField(max_length=500, null=True)
    description = models.TextField(blank=True, null=True)
    file_size = models.PositiveBigIntegerField()
    original_checksum = models.CharField(
        max_length=64, 
        null=True, 
        help_text="Checksum of the complete original file and updated in the checksum function"
    )
    
    # Chunking Information
    is_chunked = models.BooleanField(
        default=False,
        help_text="Indicates if the file has been split into chunks"
    )
    total_chunks = models.PositiveIntegerField(
        default=1,
        help_text="Total number of chunks for this file"
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_downloaded_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']  # Most recent files first
        verbose_name = "File Metadata"
        verbose_name_plural = "File Metadata"

    def __str__(self):
        return f"{self.file_name} ({self.file_size} bytes) by {self.user.username}"
    
    def get_chunks_count(self):
        """Returns the number of chunks associated with this file"""
        return self.chunks.count()
    
    def is_complete(self):
        """Check if all chunks are present"""
        return self.get_chunks_count() == self.total_chunks

class FileChunk(models.Model):
    # Relationship to parent file
    file = models.ForeignKey(
        FileMetadata, 
        on_delete=models.CASCADE, 
        related_name="chunks"
    )
    
    # Chunk Details
    chunk_index = models.PositiveIntegerField(
        help_text="Sequence number of this chunk"
    )
    chunk_size = models.PositiveBigIntegerField(
        help_text="Size of this chunk in bytes"
    )
    checksum = models.CharField(
        max_length=64, 
        help_text="Checksum (e.g. MD5 or SHA256) to verify integrity"
    )
    
    # Storage Information
    storage_node = models.CharField(
        max_length=50, 
        help_text="Name of the MinIO server node e.g., minio-node1"
    )
    object_key = models.CharField(
        max_length=255, 
        help_text="Object key in MinIO where the chunk is stored"
    )
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Indicates if the chunk's checksum has been verified"
    )

    class Meta:
        unique_together = ('file', 'chunk_index')  # ensures no duplicate chunks for a file
        ordering = ['chunk_index']  # Always retrieve chunks in correct order
        verbose_name = "File Chunk"
        verbose_name_plural = "File Chunks"

    def __str__(self):
        return f"{self.file.file_name}_chunk_{self.chunk_index}"
    
    def verify_checksum(self, computed_checksum):
        """
        Verify the integrity of the chunk
        Returns True if checksum matches, False otherwise
        """
        matches = self.checksum == computed_checksum
        self.is_verified = matches
        self.save(update_fields=['is_verified'])
        return matches
    





class Node(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=10)  # e.g., 'running', 'stopped'
    capacity = models.IntegerField()
    used_space = models.IntegerField()

    def __str__(self):
        return self.name
    




class DataObject(models.Model):
    file_metadata = models.ForeignKey(FileMetadata, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    size = models.IntegerField()

    def __str__(self):
        return f"{self.file_metadata.file_name} on {self.node.name}"