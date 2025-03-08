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


# tack the files and to chiucking in the user define size and pass it to the checksumFunction
size = 100  #mb
def chunk_file(file_path, chunk_size):
    # Implement the logic to split the file into smaller chunks here

    # return a list of chunk file paths(ex :8)
    return


# tacking the continues input this function will return the file
def merge_chunks(files):
    # Implement the logic to reassemble the chunks into the original file

    # return the file it self
    return 