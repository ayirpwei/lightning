"""
Django settings for BRCAlightning project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open('/etc/lightning_key2.txt') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ALLOWED_HOSTS = [
    '.lightning-dev3.curoverse.com',
    '.lightning-dev3.curoverse.com.',
    ]

ADMINS = (('Sarah', 'sguthrie@curoverse.com'),)
SERVER_EMAIL = 'django@lightning-dev3.curoverse.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'sallyeguthrie@gmail.com'
EMAIL_HOST_PASSWORD = 'bpuhthyzvaonsdnm'
EMAIL_USE_TLS = True

STATICFILES_DIRS = (
    BASE_DIR + "/static/",
    )
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'bootstrapform',
    'rest_framework',
    'home',
    'slippy',
    'humans',
    'tile_library',
    'genes',
    'variant_query',
    'api',
)

REST_FRAMEWORK = {
    'PAGINATE_BY': 10
}

GRAPH_MODELS = {
    'all_applications':True,
    'group_models':True,
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'BRCAlightning.urls'

WSGI_APPLICATION = 'BRCAlightning.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

with open('/etc/lightning_key.txt') as f:
    DBPW = f.read().strip()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'brca-lightning',
        'USER': 'sguthrie',
        'PASSWORD': DBPW,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    },
    'entire': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lightningdatabase',
        'USER': 'sguthrie',
        'PASSWORD': DBPW,
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = "/var/www/pylightweb/static"

MEDIA_URL = '/media/'

MEDIA_ROOT = "/home/sguthrie/pylightweb/data"
