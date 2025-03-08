from django.contrib import admin
from .models import FileMetadata  # Import your model
from .models import FileChunk

# Register the model
admin.site.register(FileMetadata)
admin.site.register(FileChunk)