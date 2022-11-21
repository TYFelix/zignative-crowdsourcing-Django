# from django.contrib import admin
#
# # Register your models here.
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
#
# from user.models import Profile
#
# class TeacherUserInline(admin.StackedInline):
#     model = User
#
#
#
# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ["user","role",]
#
#     class Meta:
#         model=Profile
#

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile, Verification, Referral, Wallet, Earning, PortfolioObject, ProfileTag

admin.site.register(Verification)

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class ProfileTagInline(admin.StackedInline):
    model = ProfileTag
    can_delete = False
    verbose_name_plural = 'Skills'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,ProfileTagInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role','date_joined')

    def get_role(self, instance):
        return instance.profile.role
    get_role.short_description = 'Role'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["id","user","balance"]

    class Meta:
        model=Wallet


@admin.register(PortfolioObject)
class PortfolioObjectAdmin(admin.ModelAdmin):
    list_display = ["id","user","entry"]

    class Meta:
        model=PortfolioObject

@admin.register(Earning)
class EarningAdmin(admin.ModelAdmin):
    list_display = ["id", "contest", "created_date"]

    class Meta:
        model = Earning



admin.site.unregister(User)

admin.site.register(Referral)


admin.site.register(User, CustomUserAdmin)
