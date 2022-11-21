from .base import *

MODE="production"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DOMAIN="https://app.zignative.com"

ALLOWED_HOSTS = ['46.101.148.167','167.99.134.59','app.zignative.com']

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'testmest5398@gmail.com'
EMAIL_HOST_PASSWORD = 'z1gnat1Ve'
EMAIL_PORT = 587

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'zignative',
        'USER': 'zignative_admin',
        'PASSWORD': 'z1gnat1Ve',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
#STATICFILES_DIRS = [
#    os.path.join(BASE_DIR, "static"),
#]
#STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

CRISPY_TEMPLATE_PACK = 'bootstrap4'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STRIPE_WEBHOOK_SECRET = "whsec_h1q6iaY9nvFtzntAoYVObUt4gYOBPjTs"
STRIPE_PUBLIC_KEY = "pk_live_51IqkdEAjprMVhdxprXrYk0DOaklSYVbTygu5kFlq37ncidw6dg3dmdjKETkfyK5uAVkXlRcdt4j1oaFCNIplraYP00VSLLChgt"
STRIPE_SECRET_KEY = "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"