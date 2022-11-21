from django.urls import path
from user import views

app_name = "user"

urlpatterns=[
    path("login/",views.login,name="login"),
    path("register/",views.register,name="register"),
    path("logout/",views.logout,name="logout"),
    path("forgot_password/",views.forgot_password,name="forgot_pass"),
    path("reset_password/<str:base64>/<str:token>",views.reset_password,name="reset_password"),
    path("account_verify/<str:base64>/<str:token>",views.account_verify,name="account_verify"),
    path("ndas/", views.signed_ndas, name="signed_ndas"),
    path("remove_or_add_portfolio/<int:entry>", views.remove_or_add_portfolio, name="remove_or_add_portfolio"),
    path('upload_cover',views.upload_cover,name="upload_cover"),
    path('set_portfolio',views.set_portfolio,name="set_portfolio"),
    path("profile/",views.account,name="account"),
    path("edit/profile/",views.edit_profile,name="edit_profile"),
    path("edit/password/",views.change_password,name="change_password"),
]