from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, FileUploadForm 
from .models import FileMetadata
import uuid, os
from django.utils.timezone import now
# from .utils.filesupdown import upload_file , download_file
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .utils.chuncker import chunk_file
# from .utils.minio_client import upload_file_to_minio 


def index(request): 
    # return HttpResponse("hello Home")
    return render(request,'index.html')


def register(request):
    """
    Handles user registration using the custom registration form.
    Extra fields (full_name, date_of_birth, gender) are collected.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Example: Save full_name in the first_name field.
            user.first_name = form.cleaned_data.get('full_name')
            user.email = form.cleaned_data.get('email')
            user.save()
            # Here you might also create a UserProfile to store date_of_birth and gender.
            login(request, user)
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    """
    Handles user login using the custom authentication form.
    """
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('files')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    """
    Logs out the current user.
    """
    logout(request)
    return redirect('login')



def profile(request):
    return render(request, 'profile.html')


# For forgot password functionality, we can use Django’s built-in views.
# You can also customize these in your URL patterns with custom templates.

def generate_file_id():
    """
    Generate a unique file ID using a combination of a UUID and timestamp.
    """
    return f"{uuid.uuid4().hex}_{int(now().timestamp())}"







@login_required(login_url='login')
def files_view(request):
    """
    Displays the user's uploaded files and handles file uploads.
    """
    user_files = FileMetadata.objects.filter(user=request.user).order_by("-uploaded_at")

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            
            # Chunk file and create metadata
            file_metadata = chunk_file(
                file, 
                request.user, 
                description=form.cleaned_data.get('description')
            )
            
            if file_metadata:
                messages.success(request, "File uploaded successfully")
                return redirect('files')
            else:
                messages.error(request, "File upload failed")
    else:
        form = FileUploadForm()
    
    return render(request, "files.html", {
        "files": user_files, 
        "form": form
    })





@login_required
def download_file_view(request, file_id):
    # Get the file metadata
    file_metadata = get_object_or_404(FileMetadata, file_id=file_id)

    # Download the file from MinIO    print the name of the file
    response = HttpResponse(file_metadata.file, content_type=file_metadata.file_type)
    response['Content-Disposition'] = f'attachment; filename="{file_metadata.file_name}"'
    return response












# @login_required(login_url='login')
# def files_view(request):
#     """
#     Displays the user's uploaded files and handles file uploads.
#     """
#     user_files = FileMetadata.objects.filter(user=request.user).order_by("-uploaded_at")
    

#     if request.method == 'POST':
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             try:
#                 # Get the uploaded file and its details
#                 uploaded_file = request.FILES['file']
#                 file_size = uploaded_file.size
#                 original_filename = uploaded_file.name
#                 file_extension = os.path.splitext(original_filename)[1]
                
#                 # Generate unique file ID
#                 file_id = generate_file_id()
                
#                 # Upload to MinIO
#                 file_url = upload_file(uploaded_file, file_id)
                
#                 # Create metadata instance but don't save yet
#                 metadata = form.save(commit=False)
#                 metadata.user = request.user
#                 metadata.file_id = file_id
#                 metadata.file_size = file_size
#                 metadata.file_url = file_url
#                 # Add extension to the user-provided filename
#                 # metadata.file_name = f"{original_filename}{file_extension}"
#                 metadata.file_name = f"{original_filename}"
#                 # Now save to database
#                 metadata.save()
                
#                 messages.success(request, "File uploaded successfully!")
#                 return redirect('files')
                
#             except Exception as e:
#                 messages.error(request, f"Error uploading file: {str(e)}")
#         else:
#             messages.error(request, "Form validation failed")
#     else:
#         form = FileUploadForm()

#     return render(request, "files.html", {
#         "files": user_files, 
#         "form": form
#     })




# @login_required
# def download_file_view(request, file_id):
#     # Get the file metadata
#     file_metadata = get_object_or_404(FileMetadata, file_id=file_id, user=request.user)
    
#     try:
#         # Get the file from MinIO
#         file_data = download_file(file_id)
        
#         # Create the response
#         response = HttpResponse(file_data.read())
        
#         # Set the content disposition and filename
#         response['Content-Disposition'] = f'attachment; filename="{file_metadata.file_name}"'
        
#         # Update last downloaded timestamp
#         file_metadata.last_downloaded_at = now()
#         file_metadata.save()
        
#         return response
        
#     except Exception as e:
#         messages.error(request, f"Error downloading file: {str(e)}")
#         return redirect('files')