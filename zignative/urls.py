"""zignative URL Configuration"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

import home.views as home_view
from customer.views import stripe_webhook, check_out_session, payment_succesful, payment_canceled

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("home.urls")),
    path('members/', include("user.urls")),
    path('customer/', include("customer.urls")),
    path('designer/', include("designer.urls")),
    path('webhooks/stripe/', stripe_webhook, name='stripe-webhook'),
    path('create-checkout-session/<pk>/', check_out_session, name='create-checkout-session'),
    path('payment/success/',payment_succesful,name="payment_succesful"),
    path('payment/cancel/<int:contest>',payment_canceled,name="payment_canceled"),
    path('media/requests/<file>', home_view.serve_protected_document, name='serve_protected_document'),
    path('media/works/<file>', home_view.serve_protected_entry, name='serve_protected_entry'),
    path('media/works/display/<file>', home_view.serve_protected_entry_display, name='serve_protected_entry_display'),

    ## API DEFINITION
    path('api/', include('zignative.api_urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)