import logging
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger(__name__)

class FileOperationStatus:
    """
    Standardized status codes for file operations
    """
    PENDING = 'pending'
    UPLOADING = 'uploading'
    DOWNLOADING = 'downloading'
    CHUNKING = 'chunking'
    
    # Success Statuses
    UPLOAD_COMPLETE = 'upload_complete'
    DOWNLOAD_COMPLETE = 'download_complete'
    
    # Error Statuses
    UPLOAD_FAILED = 'upload_failed'
    DOWNLOAD_FAILED = 'download_failed'
    CHUNK_FAILED = 'chunk_failed'
    CHECKSUM_FAILED = 'checksum_failed'

class FileOperationLog(models.Model):
    """
    Model to log file operations
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    operation_type = models.CharField(max_length=20)  # upload/download
    status = models.CharField(max_length=50)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_id = models.CharField(max_length=255, null=True, blank=True)

    @classmethod
    def log_operation(cls, user, file_name, operation_type, status, file_id=None, error_message=None):
        """
        Create a log entry for a file operation
        """
        try:
            return cls.objects.create(
                user=user,
                file_name=file_name,
                operation_type=operation_type,
                status=status,
                file_id=file_id,
                error_message=error_message
            )
        except Exception as e:
            logger.error(f"Failed to create operation log: {e}")
            return None