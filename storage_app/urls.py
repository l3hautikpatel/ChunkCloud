# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [






    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('files/', views.files_view, name='files'),
    path('download/<str:file_id>/', views.download_file_view, name='download_file'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),








    # Django's built-in password reset views with custom templates.
    path('password_reset/', auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
        ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html'
        ), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ), name='password_reset_complete'),


    path('profile/', views.profile, name='profile'),



]
