from .base import *

MODE="development"
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DOMAIN="http://127.0.0.1:8000"
ALLOWED_HOSTS = []

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
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, 'build/static'),
    os.path.join(BASE_DIR, 'build')
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

CRISPY_TEMPLATE_PACK = 'bootstrap4'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STRIPE_WEBHOOK_SECRET = "whsec_7Q20mmJJg0H5VvSofWi3ngXJdn9vbpSt"
STRIPE_PUBLIC_KEY = "pk_test_51IRxBwHQWC3Ao30UoYDoFxfYd4OPInaKaPb5M2eQPSN21M9csIWuxxLDP8QUR7ylBrNhFpcC2ig8oe9yySjOsBuj00W5QAkLn5"
STRIPE_SECRET_KEY = "sk_test_51IRxBwHQWC3Ao30Uui7fbWZZvZ28VeB0viNW7tPaCGRs7c1xHdfEvu5eIgKdRkGLIFgPSTZ3wSQVVwvA0QZ6KS2q00lWdZTukl"