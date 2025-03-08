"""
Django settings for ChunkCloud project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os 
from pathlib import Path
import environ  




# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


LOGIN_REDIRECT_URL = '/'


LOGOUT_REDIRECT_URL = '/login/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-qe#_(qr997lmdf0-8x^tbg5pg5a(g3pi8yzk_w_nl(5(i(u$qb'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storage_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ChunkCloud.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ChunkCloud.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'storage_app/static')
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# 





# minio setup for the project Version 0.1  settings.py

# env = environ.Env()


# DEBUG = env.bool("DEBUG", default=True)
# SECRET_KEY = env("SECRET_KEY", default="django-insecure-defaultkey")

# # MinIO settings
# MINIO_ENDPOINT = env("MINIO_ENDPOINT", default="http://localhost:9000")
# MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", default="admin")
# MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", default="adminadmin")
# MINIO_BUCKET_NAME = env("MINIO_BUCKET_NAME", default="testbucket")
# MINIO_URL = env("MINIO_URL", default="http://localhost:9000")


env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


MINIO_ENDPOINT = env("MINIO_ENDPOINT", default="http://localhost:9000")
MINIO_ENDPOINTS = [ep.strip() for ep in env("MINIO_ENDPOINTS", default="localhost:9000,localhost:9002,localhost:9004,localhost:9006,localhost:9008").split(",")]
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", default="admin")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", default="adminadmin")
MINIO_BUCKET_NAME = env("MINIO_BUCKET_NAME", default="testbucket")
MINIO_URL = env("MINIO_URL", default="http://localhost:9000")
MINIO_USE_HTTPS = env.bool("MINIO_USE_HTTPS", default=False)



