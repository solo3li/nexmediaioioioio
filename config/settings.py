import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env', override=True)

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key')
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '*').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'http://169.58.32.179:8000,http://localhost:8000,http://127.0.0.1:8000'
    ).split(',') if origin.strip()
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Infrastructure
    'django_q',
    'storages',

    # Project Core Apps
    'apps.accounts',
    'apps.billing',
    'apps.history',

    # Independent AI Tool Apps
    'apps.tools.tts',
    'apps.tools.stt',
    'apps.tools.text_to_video',
    'apps.tools.image_to_video',
    'apps.tools.reference_to_video',
    'apps.tools.lipsync',
    'apps.tools.motion_control',
    'apps.tools.text_to_image',
    'apps.tools.avatar_video',
]

AUTH_USER_MODEL = 'accounts.ApplicationUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'nexmedia_db'),
        'USER': os.environ.get('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Redis & Django-Q2
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
Q_CLUSTER = {
    'name': 'nexmedia_queue',
    'workers': 4,
    'recycle': 500,
    'timeout': 300,
    'retry': 360,
    'redis': REDIS_URL,
}

# MinIO / S3 Storage
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'minio:9000')
AWS_ACCESS_KEY_ID = os.environ.get('MINIO_ROOT_USER', 'minioadmin')
AWS_SECRET_ACCESS_KEY = os.environ.get('MINIO_ROOT_PASSWORD', 'minioadmin')
AWS_STORAGE_BUCKET_NAME = os.environ.get('MINIO_DEFAULT_BUCKET', 'nexmedia-media')
AWS_S3_ENDPOINT_URL = f"http://{MINIO_ENDPOINT}"
AWS_S3_USE_SSL = os.environ.get('MINIO_USE_SSL', 'False').lower() == 'true'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
