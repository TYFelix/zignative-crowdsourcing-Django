from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

# Create your models here.
from django.utils import timezone

from customer.models import Contest
from user.models import PortfolioObject


class Work(models.Model):
    user = models.ForeignKey(User, related_name="works", verbose_name="Designer", on_delete=models.CASCADE)
    image = models.FileField(upload_to="works", verbose_name="Design Image")
    display_image=models.FileField(upload_to="works/display", verbose_name="Display Image",blank=False,null=True)
    contest = models.ForeignKey(Contest, related_name="entries", verbose_name="Contest", on_delete=models.CASCADE,
                                null=True, blank=True)
    rate = models.IntegerField(default=0)
    is_declined = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(default=timezone.now())
    def __str__(self):
        return "#" + str(self.id) + " " + self.user.username + "'s entry "

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return "/static/dashboard/images/no_image.png"

    def get_display_image(self):
        if self.display_image and not self.is_deleted:
            return self.display_image.url
        else:
            return ""
    def get_display_image_api(self):
        if self.display_image:
            return self.display_image.url
        else:
            return None

    def get_hidden_image(self):
        if self.contest.round == "winner_selected":
            return self.get_display_image()
        return "/static/dashboard/images/hidden_design.png"
    def get_hidden_main(self):
        if self.contest.round == "winner_selected":
            return self.get_image()
        return "/static/dashboard/images/hidden_design.png"
    def get_main_feedbacks(self):
        return self.feedbacks.filter(parent__isnull=True)
    def in_portfolio(self):
        return PortfolioObject.objects.filter(entry_id=self.id).exists()

    @classmethod
    def get_showables(cls):
        ids = [work.id for work in cls.objects.all() if not work.contest.form_fields.get("is_hidden",False)]
        qs = cls.objects.filter(id__in=ids)
        return qs

class FinalWork(models.Model):
    contest = models.ForeignKey(Contest, verbose_name="Contest", related_name="final_works", on_delete=models.CASCADE)
    entry = models.ForeignKey(Work, verbose_name="Entry", related_name="final_works", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to="works/editable_files", verbose_name="Editable File")

    def get_file(self):
        if self.file:
            return self.file.url


class NDASigners(models.Model):
    user = models.ForeignKey(User, verbose_name="User", related_name="ndas", on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, verbose_name="Contest", related_name="ndas", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "NDA Signer"
        verbose_name_plural = "NDA Signers"

class Review(models.Model):
    user = models.ForeignKey(User, verbose_name="User", related_name="reviews", on_delete=models.CASCADE)
    entry = models.ForeignKey(Work, verbose_name="Entry",  on_delete=models.CASCADE)
    writer =  models.ForeignKey(User, verbose_name="Writer",  on_delete=models.CASCADE)

    content = models.TextField(blank=False,null=False)
    rate = models.IntegerField(blank=False,null=False)
    created_date = models.DateTimeField(auto_now_add=True)

