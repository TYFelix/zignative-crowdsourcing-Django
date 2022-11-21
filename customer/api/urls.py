from django.urls import path
from customer.api import views


urlpatterns=[
    path("",views.index),

]