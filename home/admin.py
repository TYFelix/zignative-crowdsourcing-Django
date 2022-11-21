from django.contrib import admin

# Register your models here.
from home.models import InformationPage, Contact, Notification, PayoutRequest, Invite

admin.site.site_header = 'Zignative Administration'



@admin.register(InformationPage)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["name"]
    class Meta:
        model=InformationPage


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["id","email","subject","created_date"]
    class Meta:
        model=Contact

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ["client","designer","contest","created_date"]
    class Meta:
        model=Invite

@admin.register(Notification)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ["user","created_date","is_unread",'notify_type']
    class Meta:
        model=Notification

@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ["user","amount","created_date"]
    class Meta:
        model=PayoutRequest