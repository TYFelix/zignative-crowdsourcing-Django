from django.urls import path, include
from home import views
from user import views as user_views

app_name = "home"

urlpatterns=[
    path("",views.index,name="index"),
    path("react",views.react,name="react"),
    path("get_by_filter", views.get_by_filter, name="get_by_filter"),
    path("contest/<int:contest_id>",views.contest,name="contest"),
    path("contest/<int:contest_id>/apply_filters",views.apply_filters,name="apply_filters"),
    path("entry/<int:contest_id>/<int:entry_id>",views.entry_detail,name="entry_detail"),
    path("add_comment/<int:contest_id>/<int:entry_id>",views.add_comment,name="add_comment"),
    path("delete_comment/<int:comment_id>",views.delete_comment,name="delete_comment"),
    path("edit_comment/<int:comment_id>",views.edit_comment,name="edit_comment"),
    path("create-payout-request/<str:user>",views.create_payout_request,name="create_payout_request"),
    path("nda/<int:contest_id>",views.nda,name="nda"),
    path("notifications/",views.notifications,name="notifications"),
    path("read_notifications/",views.read_notifications,name="read_notifications"),
    path("check_notifications/",views.check_notifications,name="check_notifications"),
    path("get_nots_list/",views.get_nots_list,name="get_nots_list"),
    path("submit-a-request/",views.submit_request,name="submit_request"),
    path("terms-of-use/",views.terms,name="terms"),
    path("privacy-policy/",views.privacy,name="privacy"),
    path("wallet/",views.wallet,name="wallet"),
    path('review/delete/<int:id>',views.delete_review,name="delete_review"),

    path("profile/<str:username>",user_views.public_profile,name="public_profile"),
    path("profile/<str:username>/about",user_views.profile_about,name="profile_about"),
    path('ref/<str:link>',views.refferal_link,name="refferal_link"),
    path('discover',views.discover,name="discover"),
    path('search',views.find_a_designer,name="find_a_designer"),





]