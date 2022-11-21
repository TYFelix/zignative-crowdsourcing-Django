from django.utils import timezone

from django.conf import settings
from django.contrib.auth.models import User
from django.core import signals
from django.db import models

# Create your models here.
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django_countries.fields import CountryField
from multiselectfield import MultiSelectField
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

from customer.models import SubCategory


class Profile(models.Model):
    ROLE = ((None, "Role"), ('designer', 'Designer'), ('client', 'Client'),('developer','Developer'),('init','Init'))
    user = models.OneToOneField(User, related_name="profile", verbose_name="User", on_delete=models.CASCADE)
    role = models.CharField(choices=ROLE, blank=False, max_length=10, verbose_name='Role')
    photo = models.FileField(verbose_name="Profile Photo",upload_to="user_photos",blank=True, null=True)
    cover_photo = models.FileField(verbose_name="Cover Photo",upload_to="user_covers",blank=True,null=True)
    bio = models.TextField(verbose_name="Bio", blank=True, null=True)
    country = CountryField(blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now())
    languages = MultiSelectField(choices=settings.LANGUAGES,blank=True, null=True)

    is_available = models.BooleanField(verbose_name="Available for new work", default=True)
    is_verified = models.BooleanField(default=False)

    @classmethod
    def create_user(cls, username, email, role, password):
        user = User.objects.create_user(username, email, password)
        cls.objects.create(user=user, role=role)

        return user

    def get_photo(self):
        if self.photo: return self.photo.url
        else: return "/static/dashboard/images/avatar.png"

    def get_cover_photo(self):
        if self.cover_photo: return self.cover_photo.url
        else: return "/static/dashboard/images/default-cover.png"


    def get_unread_noti_count(self):
        return self.user.notifications.filter(is_unread=True).count()

    def get_last_3_noti(self):
        return self.user.notifications.all().order_by("-created_date")[:3]

    def has_any_contest(self):
        if self.user.contests.exists():
            return True
        else:
            return False

    def is_see_alert(self):
        if self.role == "customer":
            return self.has_any_contest()
        else:
            return False

    def get_contest_count(self):
        return self.user.contests.filter(is_paid=True).exclude(status="canceled").count()

    def get_refferal_code(self):
        return urlsafe_base64_encode(force_bytes(self.user.username))

    def get_last_entry(self):
        print("alo")
        return self.user.works.filter(contest__round="winner_selected").last()

class Verification(models.Model):
    user         = models.OneToOneField(User, related_name="verification", verbose_name="User", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username


class Referral(models.Model):
    referrer     = models.ForeignKey(User, related_name = "referrers", verbose_name = "Referrer User", on_delete=models.CASCADE)
    referred     = models.OneToOneField(User, related_name = "referal", verbose_name = "Referred User", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.referred) + ' < ' + str(self.referrer)

class Wallet(models.Model):
    user = models.OneToOneField(User,verbose_name="User",related_name="wallet",on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)

class Earning(models.Model):
    user = models.ForeignKey(User,verbose_name="User",related_name="earnings",on_delete=models.CASCADE)
    contest = models.ForeignKey("customer.Contest",related_name="earnings", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def get_earning(self):
        return int(self.contest.get_prize()) * (5/100)

class PortfolioObject(models.Model):
    user = models.ForeignKey(User, verbose_name="User",related_name="portfolio_objects",on_delete=models.CASCADE)
    entry = models.ForeignKey("designer.Work", verbose_name="Entry",on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

class ProfileTag(models.Model):
    user = models.ForeignKey(User,verbose_name="User", related_name="tags",on_delete=models.CASCADE)
    service = models.ForeignKey(SubCategory, verbose_name="Service",on_delete=models.CASCADE)

@receiver(pre_save, sender=User)
def revoke_tokens(sender, instance, update_fields, **kwargs):
    if not instance._state.adding:  # instance._state.adding gives true if object is being created for the first time
        existing_user = User.objects.get(pk=instance.pk)
        if instance.password != existing_user.password or instance.email != existing_user.email or instance.username != existing_user.username:
            # If any of these params have changed, blacklist the tokens
            outstanding_tokens = OutstandingToken.objects.filter(user__pk=instance.pk)
            # Not checking for expiry date as cron is supposed to flush the expired tokens
            # using manage.py flushexpiredtokens. But if You are not using cron,
            # then you can add another filter that expiry_date__gt=datetime.datetime.now()

            for out_token in outstanding_tokens:
                if hasattr(out_token, 'blacklistedtoken'):
                    # Token already blacklisted. Skip
                    continue

                BlacklistedToken.objects.create(token=out_token)
