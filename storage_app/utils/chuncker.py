import os
import io
import json
import hashlib
import uuid
import logging
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from ..models import FileMetadata, FileChunk

# Import MinIO cluster manager
from storage_app.utils.minio_cluster_manager import minio_cluster

# Setup logging
logger = logging.getLogger(__name__)

# Chunk size in MB
CHUNK_SIZE = 100  # 100 MB

def generate_file_id():
    """
    Generate a unique file ID using a combination of a UUID and timestamp.
    """
    return f"{uuid.uuid4().hex}_{int(now().timestamp())}"

def chunk_file(file, user, description=None, bucket_name='file-chunks'):
    """
    Chunk the uploaded file
    """
    try:
        # Validate file
        if not file:
            logger.error("No file provided for chunking")
            return None

        # Generate unique file ID
        file_id = generate_file_id()

        # Create a local directory for file chunks
        chunk_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', file_id)
        os.makedirs(chunk_dir, exist_ok=True)

        # Initialize variables
        total_file_checksum = hashlib.md5()
        chunk_files = []
        total_size = 0

        # Start a database transaction
        with transaction.atomic():
            # Create FileMetadata
            file_metadata = FileMetadata.objects.create(
                user=user,
                file_name=file.name,
                file_size=file.size,
                description=description,
                is_chunked=file.size > (CHUNK_SIZE * 1024 * 1024),
                total_chunks=0
            )

            # Process file in chunks
            chunk_index = 0
            while True:
                # Read chunk
                chunk_data = file.read(CHUNK_SIZE * 1024 * 1024)
                
                # Break if no more data
                if not chunk_data:
                    break

                # Calculate chunk checksum
                chunk_checksum = hashlib.md5(chunk_data).hexdigest()
                
                # Update total file checksum
                total_file_checksum.update(chunk_data)

                # Generate unique chunk filename
                chunk_filename = f"{file_id}_chunk_{chunk_index}.part"
                chunk_path = os.path.join(chunk_dir, chunk_filename)

                # Write chunk to local file
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)

                # Upload chunk to MinIO
                try:
                    # Prepare chunk for upload
                    chunk_stream = io.BytesIO(chunk_data)
                    object_key = f"{file_id}/chunk_{chunk_index}"
                    
                    # Upload to MinIO cluster
                    storage_node = minio_cluster.upload_chunk(
                        bucket_name, 
                        object_key, 
                        chunk_stream, 
                        len(chunk_data)
                    )

                    # Create FileChunk record
                    file_chunk = FileChunk.objects.create(
                        file=file_metadata,
                        chunk_index=chunk_index,
                        chunk_size=len(chunk_data),
                        checksum=chunk_checksum,
                        storage_node=storage_node,
                        object_key=object_key
                    )

                    # Store chunk details
                    chunk_files.append({
                        'path': chunk_path,
                        'size': len(chunk_data),
                        'checksum': chunk_checksum,
                        'storage_node': storage_node,
                        'object_key': object_key
                    })

                    total_size += len(chunk_data)
                    chunk_index += 1

                except Exception as upload_error:
                    logger.error(f"Chunk upload failed: {upload_error}")
                    transaction.set_rollback(True)
                    return None

            # Update total chunks in FileMetadata
            file_metadata.total_chunks = chunk_index
            file_metadata.original_checksum = total_file_checksum.hexdigest()
            file_metadata.file_url = chunk_files[0]['path'] if chunk_files else None
            file_metadata.save()

            # Validate total file
            if not chunk_files:
                logger.error("No chunks were created")
                transaction.set_rollback(True)
                return None

            # Create metadata file for chunks
            metadata_path = os.path.join(chunk_dir, 'metadata.json')
            with open(metadata_path, 'w') as metadata_file:
                json.dump({
                    'file_id': file_id,
                    'original_filename': file.name,
                    'total_chunks': len(chunk_files),
                    'total_size': total_size,
                    'total_checksum': total_file_checksum.hexdigest(),
                    'chunks': chunk_files
                }, metadata_file)

        return file_metadata

    except Exception as e:
        logger.error(f"Chunking failed: {e}")
        return None
    







def merge_chunks(file_metadata):
    """
    Merge chunks for a given FileMetadata
    
    Args:
        file_metadata: FileMetadata instance
    
    Returns:
        - Merged file path
        - None if merging fails
    """
    try:
        # Retrieve all chunks for the file
        chunks = FileChunk.objects.filter(file=file_metadata).order_by('chunk_index')
        
        # Prepare output file path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'merged')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, file_metadata.file_name)
        
        # Recalculate total file checksum
        total_checksum = hashlib.md5()
        
        # Open output file for writing
        with open(output_path, 'wb') as output_file:
            for chunk in chunks:
                try:
                    # Download chunk from MinIO
                    chunk_data, _ = minio_cluster.download_chunk(
                        'file-chunks',  # Use the same bucket name as in upload
                        chunk.object_key
                    )
                    
                    # Read chunk data
                    chunk_bytes = chunk_data.read()
                    
                    # Verify chunk checksum
                    calculated_chunk_checksum = hashlib.md5(chunk_bytes).hexdigest()
                    if calculated_chunk_checksum != chunk.checksum:
                        raise ValueError(f"Chunk {chunk.chunk_index} checksum mismatch")
                    
                    # Write chunk to output file
                    output_file.write(chunk_bytes)
                    
                    # Update total file checksum
                    total_checksum.update(chunk_bytes)
                
                except Exception as chunk_error:
                    logger.error(f"Error processing chunk {chunk.chunk_index}: {chunk_error}")
                    return None
        
        # Verify total file checksum
        final_checksum = total_checksum.hexdigest()
        if final_checksum != file_metadata.original_checksum:
            logger.error("File integrity check failed")
            return None
        
        return output_path

    except Exception as e:
        logger.error(f"File merging failed: {e}")
        return None