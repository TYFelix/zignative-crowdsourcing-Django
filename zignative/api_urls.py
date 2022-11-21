from django.urls import path, include

from user.api import views as api_views
from customer.api import views
from rest_framework_simplejwt import views as jwt_views


urlpatterns=[
    path("contest",views.ContestListAPIView.as_view()),
    path("contest/<slug>",views.ContestDetailAPIView.as_view()),
    path('token/', api_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/',include('user.api.urls')),
    path('all-categories',views.AllCategoryListAPIView.as_view())
]