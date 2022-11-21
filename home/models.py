from statistics import mode

from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models

# Create your models here.
from django.template.loader import render_to_string
from django_ckeditor_5.fields import CKEditor5Field

from django.conf import settings

from customer.models import Invoice, Contest


class InformationPage(models.Model):
    name = models.CharField(max_length=20,null=False,blank=False,verbose_name="Unique Name")
    page= RichTextField(config_name="awesome_ckeditor")


class Contact(models.Model):
    ROLE = ((None, "Role"), ('designer', 'Designer'), ('client', 'Client'))

    user = models.ForeignKey(User,verbose_name="User",related_name="contacts",on_delete=models.CASCADE,null=True,blank=True)
    role = models.CharField(choices=ROLE,blank=True,null=False,max_length=10, verbose_name='Role')
    email = models.EmailField(verbose_name="Email",blank=True,null=False)
    subject = models.CharField(max_length=100,verbose_name="Subject",blank=False,null=False)
    description = models.TextField(verbose_name="Description",blank=False,null=False)
    file = models.FileField(verbose_name="Attachment",upload_to="requests",blank=True,null=True)

    created_date=models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name="Request"
        verbose_name_plural="Requests"


class PayoutRequest(models.Model):
    user = models.ForeignKey(User,verbose_name="User",related_name="payout_requests",on_delete=models.CASCADE,null=True,blank=True)
    amount = models.PositiveIntegerField(default=200)
    created_date = models.DateTimeField(auto_now_add=True)

class Invite(models.Model):
    client = models.ForeignKey(User,related_name="invites",on_delete=models.CASCADE)
    designer = models.ForeignKey(User,related_name="invitations",on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest,related_name="invites",on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
class Notification(models.Model):
    DECLINE = 'D'
    ROUND = 'R'
    FEEDBACK = 'F'
    REPLY = 'FR'
    RATE = 'RT'
    ANNOUNCEMENT="A"
    LOCKED = "L"
    INVOICE = "I"
    INVITE = "IV"

    ACTIVITY_TYPES = (
        (DECLINE, 'Declined'),
        (ROUND, 'Round Change'),
        (FEEDBACK, 'Feedback'),
        (REPLY, 'Feedback Reply'),
        (RATE, 'Entry Rate'),
        (ANNOUNCEMENT, 'Announcement'),
        (LOCKED, 'Contest Locked'),
        (INVOICE, 'Invoice'),
        (INVITE, 'Invite'),
    )

    user = models.ForeignKey(User,related_name="notifications",on_delete=models.CASCADE)
    notify_type = models.CharField(max_length=2, choices=ACTIVITY_TYPES)
    created_date = models.DateTimeField(auto_now_add=True)
    is_unread = models.BooleanField(default=True)

    entry = models.ForeignKey("designer.Work",related_name="notifications", on_delete=models.CASCADE,blank=True,null=True)
    feedback = models.ForeignKey("customer.Feedback",related_name="notifications", on_delete=models.CASCADE,blank=True,null=True)
    contest = models.ForeignKey("customer.Contest",related_name="notifications", on_delete=models.CASCADE,blank=True,null=True)
    contest_round=models.CharField(blank=True,null=True, max_length=30, verbose_name='contest round')
    invo = models.ForeignKey(Invoice,related_name="notifications",on_delete=models.CASCADE,blank=True,null=True)
    invite = models.ForeignKey(Invite,related_name="notifications",on_delete=models.CASCADE,blank=True,null=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def save(self, *args, **kwargs):
        domain=settings.DOMAIN

        if self.notify_type == "I":
            invoice = Invoice.objects.get(id=self.invo.id)

            total = invoice.contest.get_price().price

            try:
                if invoice.contest.form_fields["is_private"]: total += 50
            except KeyError:
                pass

            try:
                if invoice.contest.form_fields["is_hidden"]: total += 59
            except KeyError:
                pass

            message_html = render_to_string("customer/invoice.html",{"jsonfield": invoice.json, "total": total, "invoice": invoice})
            message = render_to_string("email/verify.txt", {"verify_link": "verify_link"})
            send_mail(subject=f"Zignative Crowsourcing Invoice #{invoice.id}", message=message, html_message=message_html,
                      from_email='testmest5398@gmail.com',
                      recipient_list=[self.user.email], fail_silently=False)
        else:
            message_html = render_to_string("email/notification.html", {"noti": self, "domain": domain})
            message = render_to_string("email/verify.txt", {"verify_link": "verify_link"})
            send_mail(subject="Zignative Crowsourcing", message=message, html_message=message_html,
                      from_email='testmest5398@gmail.com',
                      recipient_list=[self.user.email], fail_silently=False)
        super(Notification, self).save(*args, **kwargs)



