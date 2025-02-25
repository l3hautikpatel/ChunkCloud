# storage_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),       # The home page
    path('about/', views.about, name='about'), # About page
    path('contact/', views.contact, name='contact'), # Contact page
    path('upload/', views.upload, name='upload'),
]
