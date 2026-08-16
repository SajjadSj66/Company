import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================
# SECURITY
# =========================================
SECRET_KEY = 'django-insecure-o1s_m54x7e$_v^n5uv*0^p!9gge&21@muy*sewp6(1)v)#a2v#'
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
    'yazdancode.com',
    'www.yazdancode.com',
]

# =========================================
# APPLICATION DEFINITION
# =========================================
INSTALLED_APPS = [
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'educate',
    'users.apps.UsersConfig',
    'shop',
    'django_jalali',
    'chatbot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'company.urls'

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
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'company.wsgi.application'

# =========================================
# DATABASE
# =========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": os.getenv("DB_ENGINE"),
#         "NAME": os.getenv("DB_NAME"),
#         "USER": os.getenv("DB_USER"),
#         "PASSWORD": os.getenv("DB_PASSWORD"),
#         "HOST": os.getenv("DB_HOST"),
#         "PORT": os.getenv("DB_PORT"),
#         "OPTIONS": {
#             'charset': 'utf8mb4',
#         },
#     }
# }

# =========================================
# PASSWORD VALIDATION
# =========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================================
# INTERNATIONALIZATION
# =========================================
LANGUAGE_CODE = 'fa'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =========================================
# STATIC & MEDIA FILES
# =========================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise Storage (برای سرویس استاتیک در هاست)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =========================================
# DEFAULT
# =========================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =========================================
# AUTH
# =========================================
LOGIN_URL = 'users:login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'users:login'

# =========================================
# PAYMENT & OTHER
# =========================================
ZIBAL_MERCHANT_ID = 'zibal'
ZIBAL_CALLBACK_URL = 'https://yazdancode.com/payment/verify/'  # ← برای هاست تغییر بده

DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
WEBSITE_PRICE = 18800000

load_dotenv()

SMSIR_API_KEY = os.getenv("SMSIR_API_KEY")
SMSIR_TEMPLATE_ID = int(os.getenv("SMSIR_TEMPLATE_ID"))