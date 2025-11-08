"""
Django settings for sports_api_project project.

This file is configured to read all settings from a .env file
at the root of the project.
"""

from pathlib import Path
import environ  # Import the django-environ library
# Support DATABASE_URL for Docker or individual environment variables
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- django-environ setup ---
# Initialize the library
env = environ.Env(
    # Set casting and default values
    DEBUG=(bool, False)
)

# Read the .env file
# This assumes your .env file is in the same directory as manage.py
environ.Env.read_env(BASE_DIR / '.env')
# ----------------------------

# --- Core Settings (Read from .env) ---
#
# SECURITY WARNING: keep the secret key used in production secret!
# We now read this from the .env file
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# We read 'DEBUG=True' from the .env file
DEBUG = env('DEBUG')

# Read ALLOWED_HOSTS from environment variable (comma-separated)
ALLOWED_HOSTS = env('ALLOWED_HOSTS', default='localhost').split(',')


# --- Application definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party Apps
    'rest_framework',

    # Our Apps
    'premier_league_service',
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

ROOT_URLCONF = 'sports_api_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'sports_api_project.wsgi.application'


# --- Database (Configured for PostgreSQL from .env) ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
#
# This block replaces the default SQLite settings.
# It reads all connection details securely from your .env file.

DATABASES = {
    'default': dj_database_url.config(
        default=f"postgresql://{env('POSTGRES_USER')}:{env('POSTGRES_PASSWORD')}@{env('POSTGRES_HOST')}:{env('POSTGRES_PORT')}/{env('POSTGRES_DB')}"
    )
}


# --- Password validation ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # ... (default validators) ...
]


# --- Internationalization ---
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# --- Default primary key field type ---
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Security Settings (Read from .env) ---
SECURE_SSL_REDIRECT = env('SECURE_SSL_REDIRECT', default=False)
SECURE_HSTS_SECONDS = env('SECURE_HSTS_SECONDS', default=0, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env('SECURE_HSTS_PRELOAD', default=False)
SECURE_CONTENT_TYPE_NOSNIFF = env('SECURE_CONTENT_TYPE_NOSNIFF', default=True)
SECURE_BROWSER_XSS_FILTER = env('SECURE_BROWSER_XSS_FILTER', default=True)
X_FRAME_OPTIONS = env('X_FRAME_OPTIONS', default='DENY')

# --- Session and Cookie Settings ---
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', default=False)
SESSION_COOKIE_HTTPONLY = env('SESSION_COOKIE_HTTPONLY', default=True)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', default=False)
CSRF_COOKIE_HTTPONLY = env('CSRF_COOKIE_HTTPONLY', default=True)

# --- API Settings ---
FPL_API_URL = env('FPL_API_URL', default='https://fantasy.premierleague.com/api/bootstrap-static/')

# --- Admin URL (customizable for security) ---
ADMIN_URL = env('ADMIN_URL', default='admin/')