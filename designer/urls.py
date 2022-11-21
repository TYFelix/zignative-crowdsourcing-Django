from django.urls import path
from designer import views

app_name="designer"

urlpatterns=[
    path("",views.index,name="index"),
    path("browse-contests",views.browse_contests,name="browse_contests"),
    path("get_by_filter",views.get_by_filter,name="get_by_filter"),
    path("submit_design/<int:contest_id>", views.submit_design, name="submit_design"),
    path("submit-final-design/<int:contest_id>", views.submit_final_design, name="submit_final_design"),
    path("submit-final-works/<int:contest_id>/<int:entry_id>", views.submit_final_works, name="submit_final_works"),
    path("delete-final-work/<int:contest_id>/<int:work_id>", views.delete_final_work, name="delete_final_work"),
    path("approve-files/<int:contest_id>", views.approve_files, name="approve_files"),
    path("submit_all_files/<int:contest_id>", views.submit_all_files, name="submit_all_files"),
    path("delete-entry/<int:entry>",views.delete_entry,name="delete_entry")
]