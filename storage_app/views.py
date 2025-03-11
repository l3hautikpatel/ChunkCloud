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
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import FileMetadata
from django.utils import timezone
from storage_app.utils.chuncker import merge_chunks

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
    """
    Download a file by its file_id
    """
    try:
        # Retrieve the file metadata
        file_metadata = FileMetadata.objects.get(
            file_id=file_id, 
            user=request.user
        )
        
        # Merge chunks
        merged_file_path = merge_chunks(file_metadata)
        
        if not merged_file_path:
            raise Http404("File could not be reconstructed")
        
        # Prepare file response
        response = FileResponse(
            open(merged_file_path, 'rb'), 
            as_attachment=True, 
            filename=file_metadata.file_name
        )
        
        # Optional: Update last downloaded timestamp
        file_metadata.last_downloaded_at = timezone.now()
        file_metadata.save()
        
        return response
    
    except FileMetadata.DoesNotExist:
        raise Http404("File not found")
    except Exception as e:
        # logger.error(f"Download failed: {e}")
        print(f"Download failed: {e}")
        raise Http404("Download failed")









from .utils.file_operation_tracker import FileOperationLog, FileOperationStatus

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
            
            # Log the start of upload
            operation_log = FileOperationLog.log_operation(
                user=request.user,
                file_name=file.name,
                operation_type='upload',
                status=FileOperationStatus.UPLOADING
            )
            
            try:
                # Chunk file and create metadata
                file_metadata = chunk_file(
                    file, 
                    request.user, 
                    description=form.cleaned_data.get('description')
                )
                
                if file_metadata:
                    # Update log with success
                    operation_log.status = FileOperationStatus.UPLOAD_COMPLETE
                    operation_log.file_id = file_metadata.file_id
                    operation_log.save()
                    
                    messages.success(request, "File uploaded successfully")
                    return redirect('files')
                else:
                    # Update log with failure
                    operation_log.status = FileOperationStatus.UPLOAD_FAILED
                    operation_log.error_message = "Chunking process failed"
                    operation_log.save()
                    
                    messages.error(request, "File upload failed")
            
            except Exception as e:
                # Update log with unexpected error
                operation_log.status = FileOperationStatus.UPLOAD_FAILED
                operation_log.error_message = str(e)
                operation_log.save()
                
                messages.error(request, f"File upload failed: {e}")
    else:
        form = FileUploadForm()
    
    return render(request, "files.html", {
        "files": user_files, 
        "form": form
    })