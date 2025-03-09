# – Implements the logic to break a large file into smaller chunks based on a defined chunk size.
# – Could have two functions:
# • chunk_file(file_path, chunk_size): splits the file into smaller parts.
# • merge_chunks(chunk_files_list, output_path): recombines the chunks into the full file.
# – This module may also assign each chunk to a particular MinIO node based on your distribution logic (e.g., round-robin, size-based, or load-based).
"""
chunker.py

Responsible for splitting files into chunks and reassembling them.
Useful for distributing file chunks across multiple storage nodes.
"""


import os
import json
import hashlib
import uuid
import random
from django.conf import settings
from ..models import FileMetadata, FileChunk
from django.db import transaction
from django.utils.timezone import now

# Chunk size in MB
CHUNK_SIZE = 100  # 100 MB

def generate_file_id():
    """
    Generate a unique file ID using a combination of a UUID and timestamp.
    """
    return f"{uuid.uuid4().hex}_{int(now().timestamp())}"


def chunk_file(file, user, description=None):
    """
    Chunk the uploaded file and create FileMetadata and FileChunk records
    
    Args:
        file: Uploaded file object
        user: User who uploaded the file
        description: Optional file description
    
    Returns:
        - FileMetadata instance if successful
        - None if chunking fails
    """
    try:
        # Validate file
        if not file:
            return None

        # Generate unique file ID
        file_id = generate_file_id()

        # Create a directory for file chunks
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
                total_chunks=0  # Will be updated later
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

                # Write chunk to file
                with open(chunk_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)

                # Select storage node (you can implement more sophisticated selection)
                storage_nodes = ['minio-node1', 'minio-node2', 'minio-node3']
                storage_node = random.choice(storage_nodes)

                # Create FileChunk record
                file_chunk = FileChunk.objects.create(
                    file=file_metadata,
                    chunk_index=chunk_index,
                    chunk_size=len(chunk_data),
                    checksum=chunk_checksum,
                    storage_node=storage_node,
                    object_key=f"{file_id}/chunk_{chunk_index}"
                )

                # Store chunk details
                chunk_files.append({
                    'path': chunk_path,
                    'size': len(chunk_data),
                    'checksum': chunk_checksum
                })

                total_size += len(chunk_data)
                chunk_index += 1

            # Update total chunks in FileMetadata
            file_metadata.total_chunks = chunk_index
            file_metadata.original_checksum = total_file_checksum.hexdigest()
            file_metadata.file_url = chunk_files[0]['path'] if chunk_files else None
            file_metadata.save()

            # Validate total file
            if not chunk_files:
                transaction.set_rollback(True)
                return None

            # Create metadata file for chunks (optional, for debugging/recovery)
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
        # Comprehensive error handling
        print(f"Chunking failed: {e}")
        return None



# Verification Function
def verify_file_integrity(file_metadata):
    """
    Verify the integrity of all chunks for a file
    """
    try:
        # Retrieve all chunks for the file
        chunks = FileChunk.objects.filter(file=file_metadata).order_by('chunk_index')
        
        # Recalculate total file checksum
        total_checksum = hashlib.md5()
        
        for chunk in chunks:
            # Read chunk data
            with open(chunk.object_key, 'rb') as chunk_file:
                chunk_data = chunk_file.read()
            
            # Verify individual chunk checksum
            calculated_chunk_checksum = hashlib.md5(chunk_data).hexdigest()
            if not chunk.verify_checksum(calculated_chunk_checksum):
                return False
            
            # Update total file checksum
            total_checksum.update(chunk_data)
        
        # Verify total file checksum
        return total_checksum.hexdigest() == file_metadata.original_checksum

    except Exception as e:
        print(f"Integrity verification failed: {e}")
        return False
# tacking the continues input this function will return the file
def merge_chunks(files):
    # Implement the logic to reassemble the chunks into the original file

    # return the file it self
    return 