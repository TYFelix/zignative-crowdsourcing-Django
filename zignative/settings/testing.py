from .base import *

MODE="testing"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DOMAIN="http://46.101.148.167"

ALLOWED_HOSTS = ['46.101.148.167','167.99.134.59','zignative.com','www.zignative.com']

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'testmest5398@gmail.com'
EMAIL_HOST_PASSWORD = 'z1gnat1Ve'
EMAIL_PORT = 587

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

STRIPE_WEBHOOK_SECRET = "whsec_BNgrUjBhirG4Lk5orKfMvah3Wv6XXw4W"
STRIPE_PUBLIC_KEY = "pk_test_51IRxBwHQWC3Ao30UoYDoFxfYd4OPInaKaPb5M2eQPSN21M9csIWuxxLDP8QUR7ylBrNhFpcC2ig8oe9yySjOsBuj00W5QAkLn5"
STRIPE_SECRET_KEY = "sk_test_51IRxBwHQWC3Ao30Uui7fbWZZvZ28VeB0viNW7tPaCGRs7c1xHdfEvu5eIgKdRkGLIFgPSTZ3wSQVVwvA0QZ6KS2q00lWdZTukl"
