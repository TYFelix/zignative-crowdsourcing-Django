from django.urls import path, include


from user.api import views

urlpatterns=[

    path('change-password',views.UpdatePassword.as_view(), name="change-password"),
    path('register',views.CreateUserView.as_view()),
    path('countries',views.CountryView.as_view()),
    path('resend-verification',views.ResendView.as_view()),
    path('register/step_2',views.RegisterStep2View.as_view()),
    path('register/step_3',views.RegisterStep3View.as_view()),
    path('forgot-password',views.ForgotPasswordView().as_view(),name="forgot-password"),
    path('reset-password/<str:base64>/<str:token>',views.ResetPasswordView().as_view(),name="reset-password"),
    path('verify-account/<str:base64>/<str:token>',views.VerifyAccountView().as_view(),name="verify-account"),


]