from django.urls import path,include
from customer import views,contest_views

app_name="customer"

urlpatterns=[
    path("",views.index,name="index"),
    path("categories",views.categories,name="categories"),
    path("send_celery_mail",views.send_celery_mail,name="send_celery_mail"),
    path("create-contest/<int:id>",views.create_contest,name="create_contest"),
    path("browse-contests", views.browse_contests, name="browse_contests"),
    path('create-contest/<str:contest>/<str:step>/',views.contest_step,name="contest_step"),
    path('edit-contest/<str:contest>/<str:step>/',contest_views.edit_contest,name="edit_contest"),
    path('edit-bc-contest/<str:contest>/<str:step>/',contest_views.bc_edit_contest,name="bc_edit_contest"),
    path('edit-wp-contest/<str:contest>/<str:step>/',contest_views.wp_edit_contest,name="wp_edit_contest"),
    path('edit-ba-contest/<str:contest>/<str:step>/',contest_views.ba_edit_contest,name="ba_edit_contest"),
    path('edit-et-contest/<str:contest>/<str:step>/',contest_views.et_edit_contest,name="et_edit_contest"),
    path('edit-sm-contest/<str:contest>/<str:step>/',contest_views.sm_edit_contest,name="sm_edit_contest"),
    path('edit-cn-contest/<str:contest>/<str:step>/',contest_views.cn_edit_contest,name="cn_edit_contest"),
    path('edit-ma-contest/<str:contest>/<str:step>/',contest_views.ma_edit_contest,name="ma_edit_contest"),
    path('edit-lp-contest/<str:contest>/<str:step>/',contest_views.lp_edit_contest,name="lp_edit_contest"),
    path('edit-td-contest/<str:contest>/<str:step>/',contest_views.td_edit_contest,name="td_edit_contest"),
    path('edit-md-contest/<str:contest>/<str:step>/',contest_views.md_edit_contest,name="md_edit_contest"),
    path('edit-bkc-contest/<str:contest>/<str:step>/',contest_views.bkc_edit_contest,name="bkc_edit_contest"),
    path('edit-mgc-contest/<str:contest>/<str:step>/',contest_views.mgc_edit_contest,name="mgc_edit_contest"),
    path('edit-wpd-contest/<str:contest>/<str:step>/',contest_views.wpd_edit_contest,name="wpd_edit_contest"),
    path('submit-contest/<str:contest>',views.submit_contest,name="submit_contest"),
    path('add-attachment/<str:contest>',views.add_attachment,name="add_attachment"),
    path('apply-discount/<str:contest>',views.apply_discount,name="apply_discount"),
    path('delete-attachment/<str:attach_id>',views.delete_attachment,name="delete_attachment"),
    path('draft-contest/<str:contest>',views.draft_contest,name="draft_contest"),
    path('decline-entry/<int:contest>/<int:entry>',views.decline_entry,name="decline_entry"),
    path('rate-entry/<int:contest>/<int:entry>',views.rate_entry,name="rate_entry"),
    path('confirm-finalists/<int:contest_id>',views.confirm_finalists,name="confirm_finalists"),
    path('confirm-winner/<int:contest_id>',views.confirm_winner,name="confirm_winner"),
    path('delete-contest/<int:contest_id>',contest_views.delete_contest,name="delete_contest"),
    path('add-announcement/<int:contest_id>',views.add_anouncement,name="add_anouns"),
    path('delete-announcement/<int:anouns_id>',views.delete_announcement,name="delete_anouns"),
    path('split-prize/<int:contest>',views.split_prize,name="split_prize"),
    path('split-prize-to-designers/<int:contest>',views.split_prize_to_designers,name="split_prize_to_designers"),
    path('invoice/<int:invoice>',views.invoice,name="invoice"),
    path('start_poll/<int:contest>',views.start_poll,name="start_poll"),
    path('poll/<int:poll>/edit',views.edit_poll,name="edit_poll"),
    path('poll/<poll>',views.poll_detail,name="poll_detail"),
    path('poll/<int:poll>/delete',views.delete_poll,name="delete_poll"),
    path('poll_obj/<int:poll_obj>/add_comment',views.add_poll_comment,name="add_poll_comment"),
    path('poll_obj/<int:poll_comment>/delete_comment',views.delete_comment,name="delete_comment"),
    path('teams',views.teams,name="teams"),
    path('invite-designer/<str:user>/<int:contest>',views.invite_designer,name="invite_designer")

]