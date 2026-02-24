import os
import environ
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# YENİ: Environ Ayarları Başlangıcı
env = environ.Env(
    DEBUG=(bool, False),
    SITE_NAME=(str, 'AnyPlace') # Varsayılan isim
)
# Varsa .env dosyasını oku
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# YENİ: Değişkenler artık env'den çekiliyor
SECRET_KEY = env('DJANGO_SECRET_KEY', default='kurulum-icin-gecici-gizli-anahtar')
DEBUG = env('DEBUG')
SITE_NAME = env('SITE_NAME')

# YENİ: İzin verilen hostlar da dinamik (Vercel dahil)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '.vercel.app'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_recaptcha',
    'places',  # YENİ: toilets yerine places
    'simple_history',
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
    'simple_history.middleware.HistoryRequestMiddleware',
]

# YENİ: freetoilet_project yerine core
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'places' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',  # BU SATIR ŞART!
                'django.contrib.messages.context_processors.messages',
                'places.context_processors.site_settings',
            ],
        },
    },
]

# YENİ: freetoilet_project yerine core
WSGI_APPLICATION = 'core.wsgi.application'

# Database
# Database
# Vercel'de DATABASE_URL çevresel değişken (Environment Variable) olarak tanımlanmalıdır.
DATABASES = {
    'default': dj_database_url.config(
        # Eğer DATABASE_URL yoksa yerelde sqlite kullanır
        default=env('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
        conn_max_age=600,
        ssl_require=True if not DEBUG else False  # Neon/Postgres için Vercel'de SSL gerekebilir
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# YENİ: Dil ve Saat Dilimi genel kullanıma uygun ayarlandı
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
WHITENOISE_KEEP_ONLY_HASHED_FILES = True
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Recaptcha - Env'den çekiliyor
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='default_public_key')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default='default_private_key')