from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout 
from django.contrib.auth.models import User
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
import socket
import concurrent.futures

from minio import Minio
import urllib3

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







# @login_required(login_url='login')
# def files_view(request):
#     """
#     Displays the user's uploaded files and handles file uploads.
#     """
#     user_files = FileMetadata.objects.filter(user=request.user).order_by("-uploaded_at")

#     if request.method == 'POST':
#         form = FileUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             file = request.FILES['file']
            
#             # Chunk file and create metadata
#             file_metadata = chunk_file(
#                 file, 
#                 request.user, 
#                 description=form.cleaned_data.get('description')
#             )
            
#             if file_metadata:
#                 messages.success(request, "File uploaded successfully")
#                 return redirect('files')
#             else:
#                 messages.error(request, "File upload failed")
#     else:
#         form = FileUploadForm()
    
#     return render(request, "files.html", {
#         "files": user_files, 
#         "form": form
#     })










# @login_required
# def download_file_view(request, file_id):
#     """
#     Download a file by its file_id
#     """
#     try:
#         # Retrieve the file metadata
#         file_metadata = FileMetadata.objects.get(
#             file_id=file_id, 
#             user=request.user
#         )
        
#         # Merge chunks
#         merged_file_path = merge_chunks(file_metadata)
        
#         if not merged_file_path:
#             raise Http404("File could not be reconstructed")
        
#         # Prepare file response
#         response = FileResponse(
#             open(merged_file_path, 'rb'), 
#             as_attachment=True, 
#             filename=file_metadata.file_name
#         )
        
#         # Optional: Update last downloaded timestamp
#         file_metadata.last_downloaded_at = timezone.now()
#         file_metadata.save()
        
#         return response
    
#     except FileMetadata.DoesNotExist:
#         raise Http404("File not found")
#     except Exception as e:
#         # logger.error(f"Download failed: {e}")
#         print(f"Download failed: {e}")
#         raise Http404("Download failed")







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
                    
                    raise Http404("File upload failed")
            
            except Exception as e:
                # Update log with unexpected error
                operation_log.status = FileOperationStatus.UPLOAD_FAILED
                operation_log.error_message = str(e)
                operation_log.save()
                
                raise Http404("File upload failed")
    else:
        form = FileUploadForm()
    
    return render(request, "files.html", {
        "files": user_files, 
        "form": form
    })



from .utils.file_operation_tracker import FileOperationLog, FileOperationStatus

@login_required
def download_file_view(request, file_id):
    """
    Download a file by its file_id with tracking
    """
    try:
        # Retrieve the file metadata
        file_metadata = FileMetadata.objects.get(
            file_id=file_id, 
            user=request.user
        )
        
        # Log the start of download
        operation_log = FileOperationLog.log_operation(
            user=request.user,
            file_name=file_metadata.file_name,
            operation_type='download',
            status=FileOperationStatus.DOWNLOADING,
            file_id=file_id
        )
        
        # Merge chunks
        merged_file_path = merge_chunks(file_metadata)
        
        if not merged_file_path:
            # Update log with failure
            operation_log.status = FileOperationStatus.DOWNLOAD_FAILED
            operation_log.error_message = "File reconstruction failed"
            operation_log.save()
            
            raise Http404("File could not be reconstructed")
        
        # Prepare file response
        response = FileResponse(
            open(merged_file_path, 'rb'), 
            as_attachment=True, 
            filename=file_metadata.file_name
        )
        
        # Update last downloaded timestamp
        file_metadata.last_downloaded_at = timezone.now()
        file_metadata.save()
        
        # Update log with success
        operation_log.status = FileOperationStatus.DOWNLOAD_COMPLETE
        operation_log.save()
        
        return response
    
    except FileMetadata.DoesNotExist:
        raise Http404("File not found")
    except Exception as e:
        # Log unexpected errors
        if 'operation_log' in locals():
            operation_log.status = FileOperationStatus.DOWNLOAD_FAILED
            operation_log.error_message = str(e)
            operation_log.save()
        
        raise Http404("Download failed")
    
    












def is_port_open(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def calculate_storage_usage(client, buckets):
    total_size = 0
    for bucket in buckets:
        try:
            objects = client.list_objects(bucket.name, recursive=True)
            for obj in objects:
                try:
                    obj_stat = client.stat_object(bucket.name, obj.object_name)
                    total_size += obj_stat.size
                except Exception as stat_error:
                    print(f"Error getting object stat for {obj.object_name}: {stat_error}")
        except Exception as list_error:
            print(f"Error listing objects in bucket {bucket.name}: {list_error}")
    return total_size / (1024 * 1024 * 1024)


def check_server_status(server_url):
    try:
        host = server_url.split('//')[1].split(':')[0]
        port = int(server_url.split('//')[1].split(':')[1])

        if not is_port_open(host, port):
            return {
                'url': server_url,
                'status': 'Offline',
                'details': None,
                'drives': []
            }

        try:
            client = Minio(
                server_url.split('//')[1],
                access_key="admin",
                secret_key="adminadmin",
                secure=False
            )
            buckets = client.list_buckets()
            drives = [{'path': 'Unknown', 'status': 'Online'}]

            return {
                'url': server_url,
                'status': 'Online',
                'details': {
                    'buckets': len(buckets)
                },
                'drives': drives
            }
        except Exception as client_error:
            print(f"MinIO client error for {server_url}: {client_error}")
            return {
                'url': server_url,
                'status': 'Offline',
                'error': str(client_error),
                'drives': []
            }
    except Exception as e:
        print(f"General error checking {server_url}: {e}")
        return {
            'url': server_url,
            'status': 'Offline',
            'error': str(e),
            'drives': []
        }


def admin_dashboard(request):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    server_urls = [
        "http://localhost:9000",
        "http://localhost:9002",
        "http://localhost:9004",
        "http://localhost:9006",
        "http://localhost:9008"
    ]

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        server_statuses = list(executor.map(check_server_status, server_urls))

    print("Server Statuses:")
    for status in server_statuses:
        print(f"{status['url']}: {status['status']}")

    online_servers = [s for s in server_statuses if s['status'] == 'Online']
    offline_servers = [s for s in server_statuses if s['status'] == 'Offline']

    server_status_message = None
    if not online_servers:
        server_status_message = "WARNING: No MinIO servers are currently running. Data may be incomplete."

    buckets = []
    bucket_count = 0
    data_objects = []
    object_count = 0
    total_storage_usage = 0

    for server in online_servers:
        try:
            client = Minio(
                server['url'].split('//')[1],
                access_key="admin",
                secret_key="adminadmin",
                secure=False
            )
            buckets = client.list_buckets()
            bucket_count = len(buckets)

            for bucket in buckets:
                try:
                    objects = client.list_objects(bucket.name, recursive=True)
                    for obj in objects:
                        object_count += 1
                        try:
                            obj_stat = client.stat_object(bucket.name, obj.object_name)
                            data_objects.append({
                                'bucket': bucket.name,
                                'object_name': obj.object_name,
                                'size': f"{obj_stat.size} bytes",
                                'permission': 'R/W'
                            })
                        except Exception as stat_error:
                            print(f"Error getting object stat: {stat_error}")
                            data_objects.append({
                                'bucket': bucket.name,
                                'object_name': obj.object_name,
                                'size': 'Unknown',
                                'permission': 'Unknown'
                            })
                except Exception as list_error:
                    print(f"Error listing objects in bucket {bucket.name}: {list_error}")

            total_storage_usage = calculate_storage_usage(client, buckets)
            break

        except Exception as client_error:
            print(f"Error connecting to MinIO: {client_error}")

    total_servers_online = len(online_servers)
    total_servers_offline = len(offline_servers)

    drives_online = 0
    drives_offline = 0

    for server in server_statuses:
        if server['status'] == 'Online':
            server_drives = server.get('drives', [])
            drives_online += len([d for d in server_drives if d['status'].lower() == 'online'])
            drives_offline += len([d for d in server_drives if d['status'].lower() != 'online'])
        else:
            drives_offline += 1

    server_info = {
        'buckets': bucket_count,
        'objects': object_count,
        'servers_online': total_servers_online,
        'servers_offline': total_servers_offline,
        'drives_online': drives_online,
        'drives_offline': drives_offline,
        'reported_usage': f"{total_storage_usage:.2f} GiB"
    }

    users = User.objects.all()

    context = {
        'server_info': server_info,
        'buckets': buckets,
        'data_objects': data_objects,
        'users': users,
        'server_statuses': server_statuses,
        'server_status_message': server_status_message
    }
    return render(request, 'admin_dashboard.html', context)