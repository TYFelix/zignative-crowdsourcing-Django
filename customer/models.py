import uuid
from datetime import timedelta

import jsonfield
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import models
import jsonfield
from django.db.models import Q, Avg
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils import timezone
from jsonfield.utils import default


def in_three_days():
    return timezone.now() + timedelta(days=5)


# Create your models here.
class MainCategory(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False, verbose_name="Title")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    TEMPLATE_NAME = [('logo-design', 'logo-design'),
                     ('business-card-design', 'business-card-design'),
                     ('web-page-design', 'web-page-design'),
                     ('banner-ad-design', 'banner-ad-design'),
                     ('email-template-design', 'email-template-design'),
                     ('social-media-assets-design', 'social-media-assets-design'),
                     ('company-product-name', 'company-product-name'),
                     ('mobile-app-design', 'mobile-app-design'),
                     ('landing-page-design', 'landing-page-design'),
                     ('merchandise-design', 'merchandise-design'),
                     ('book-cover-design', 'book-cover-design'),
                     ('magazine-cover-design', 'magazine-cover-design'),
                     ('wordpress-design', 'wordpress-design'),
                     ('t-shirt-design', 't-shirt-design')]

    title = models.CharField(max_length=50, null=False, blank=False, verbose_name="Title")
    template_name = models.CharField(max_length=50, choices=TEMPLATE_NAME, verbose_name="Template Name",
                                     help_text="This field determines which template this service will work with. If you don't fill it, it will automatically have a slug version of the service title.")

    parent = models.ForeignKey(MainCategory, related_name="sub_categories", on_delete=models.CASCADE, null=False,
                               blank=False, verbose_name="Main Category")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def save(self, *args, **kwargs):
        if not self.template_name:
            self.template_name = slugify(self.title)
        # if not SubCategory.objects.filter(template_name=self.template_name).exists():

        super(SubCategory, self).save(*args, **kwargs)

    def get_min_price(self):
        if self.prices.exists():
            return self.prices.order_by("price")[0]
        return None
    def get_min_price_total(self):
        return self.get_min_price().price + self.get_min_price().fee

    def __str__(self):
        return self.title + " ({})".format(self.parent.title)


class Contest(models.Model):
    STATUS = ((None, "Status"), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('canceled', 'Canceled'))
    ROUND = ((None, "Round"), ('qualify', 'Qualify Round'), ('qualify_end', 'Qualify Ended'),
             ('final_round', 'Final Round'), ("selecting_winner", "Selecting Winner"),
             ("winner_selected", "Winner Selected"),)

    title = models.CharField(max_length=50, null=True, blank=True, verbose_name="Title")
    user = models.ForeignKey(User, related_name="contests", verbose_name="User", on_delete=models.CASCADE, null=False,
                             blank=False, default=1)
    category = models.ForeignKey(SubCategory, null=False, blank=False, verbose_name="Category",
                                 on_delete=models.CASCADE)
    is_draft = models.BooleanField(default=True)
    status = models.CharField(choices=STATUS, blank=False, max_length=15, verbose_name='Status', default="in_progress")
    round = models.CharField(choices=ROUND, blank=False, max_length=30, verbose_name='Round', default="qualify")
    form_fields = models.JSONField(default="{}")
    created_date = models.DateTimeField(auto_now_add=True)
    finish_date = models.DateTimeField(default=in_three_days)
    image = models.FileField(verbose_name="Contest Image", upload_to="contests", blank=True, null=True)
    is_temp = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    is_submitted = models.BooleanField(default=False)
    slug = models.SlugField(max_length=70, default=uuid.uuid1)

    ### IF CONTEST LOCKED
    is_locked = models.BooleanField(default=False)
    locked_date = models.DateTimeField(null=True, blank=True)
    lock_finish_date = models.DateTimeField(null=True, blank=True)

    prize = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Contests"

    def __str__(self):
        return self.title or ''

    def is_first_contest(self):
        if self == Contest.objects.filter(user=self.user).first(): return True
        return False

    def is_refferal(self):

        if self.is_first_contest():
            try:
                if self.user.referal: return True
            except:
                pass
        return False

    def define_slug(self):
        slug = slugify(self.title.replace("ı", "i"))
        unique = slug
        number = 1
        while Contest.objects.filter(slug=unique).exists():
            unique = '{}-{}'.format(slug, number)
            number += 1
        return unique

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = self.define_slug()
        if self.is_paid:
            self.prize = self.get_prize()

        return super(Contest, self).save(*args, **kwargs)

    def get_price(self):
        try:
            price_id = int(self.form_fields["price_plan"])

        except KeyError:
            return None

        try:
            price = Prices.objects.get(id=price_id)
            price.price = price.price + len(self.form_fields.get("web_pages", "")) * 100

            return price
        except Prices.DoesNotExist:
            return None

    def get_total_price(self):
        try:
            price_id = int(self.form_fields["price_plan"])

        except KeyError:
            return None

        try:
            price = self.get_price().price
            if DiscountEvent.objects.filter(contest=self).exists():
                discount = Discount.objects.get(events__contest_id=self.id)
            else:
                discount = None

            if self.form_fields.get("is_private"):
                if discount and discount.free_private:
                    pass
                else:
                    price += 50

            if self.form_fields.get("is_hidden"):
                if discount and discount.free_hidden:
                    pass
                else:
                    price += 59

            return price + self.get_transaction_fee()["last"]
        except Prices.DoesNotExist:
            return None



    def get_transaction_fee(self):
        fee = self.get_price().fee
        modified_fee = self.get_price().fee
        devent = DiscountEvent.objects.filter(contest=self)
        boolean = False
        if devent.exists() and devent.first().discount.modify_fee != 0:
            modified_fee = fee - (fee * (int(devent.first().discount.modify_fee) / 100))

            boolean = True
        if self.is_refferal():
            fee = int(int(fee) / 2)
            boolean = True

        return {"discount": boolean,
                "last": int(modified_fee),
                "first": int(fee),
                "percentage": 25}

    def discount(self):
        percentage = 25
        devent = DiscountEvent.objects.filter(contest=self)
        boolean = False
        if devent.exists() and devent.first().discount.modify_fee != 25:
            percentage = int(devent.first().discount.modify_fee)
            boolean = True
        if self.is_refferal():
            percentage = int(int(percentage) / 2)
            boolean = True

        return {"discount": boolean,
                "last": percentage / 100,
                "first": 25 / 100,
                "percentage": percentage}

    def get_prize(self):
        price = self.get_price().price
        return price

    def get_pure_prize(self):
        return self.get_price().price - len(self.form_fields.get("web_pages", "")) * 100

    def get_entry_count(self):
        return self.entries.filter(is_deleted=False).count()

    def get_users(self):
        return set([work.user for work in self.entries.all()])

    def get_image(self):
        try:
            if self.form_fields["is_hidden"]:
                return "/static/dashboard/images/hidden_design.png"
        except KeyError:
            qs = self.entries.filter(is_declined=False, is_deleted=False)
            if qs.exists():
                return qs.last().get_display_image()
            else:
                return "/static/dashboard/images/no_image.png"

    def get_image_api(self):
        try:
            if self.form_fields["is_hidden"]:
                return None
        except KeyError:
            if self.entries.exists():
                return self.entries.last().get_display_image_api()
            else:
                return None

    def get_example_logos(self):
        logos = []
        for ex in self.form_fields["selected_logos"]:
            logos.append(ExampleLogo.objects.get(id=ex))
        return logos

    def get_winner(self):
        return self.finalists.filter(is_winner=True).first().entry

    def get_timezone(self):
        date = self.finish_date - timezone.now()
        return timezone.now()

    def get_feedbacks(self):
        count = Feedback.objects.filter(entry__contest_id=self.id, user__profile__role="client").count()
        try:
            percentage = int(
                len(set(self.entries.filter(feedbacks__isnull=False, is_deleted=False))) / self.entries.filter(
                    is_deleted=False).count() * 100)
        except ZeroDivisionError:
            percentage = 0
        return {"count": count, "percentage": percentage}

    def get_last_feedback(self):
        return Feedback.objects.filter(entry__contest_id=self.id, user__profile__role="client").last()

    def rating_percentage(self):
        entries = self.entries.filter(is_deleted=False)
        dec_or_rate = entries.filter(Q(is_declined=True) | Q(rate__gt=0)).count()
        try:
            percentage = int((dec_or_rate / entries.filter(is_deleted=False).count()) * 100)
        except ZeroDivisionError:
            percentage = 0
        return percentage

    def is_splittable(self):
        if self.is_locked:
            if self.lock_finish_date < timezone.now():
                return True
            else:
                return False
        else:
            return False

    def is_hidden(self):
        try:
            if self.form_fields["is_hidden"]:
                return True
            else:
                return False
        except:
            return False

    def is_private(self):
        try:
            if self.form_fields["is_private"]:
                return True
            else:
                return False
        except:
            return False

    def is_guaranteed(self):
        try:
            if self.form_fields["is_guaranteed"]:
                return True
            else:
                return False
        except:
            return False

    def get_shared_entries(self):
        if self.is_locked and self.status == "completed":
            if self.round == "qualify_end":
                return self.entries.filter(is_declined=False, is_deleted=False)
            if self.round == "selecting_winner":
                return self.finalists.filter(entry__is_declined=False, entry__is_deleted=False)
        else:
            return False

    def get_shared_prize(self):
        try:
            total = self.get_prize()
            return total / self.get_shared_entries().count()
        except:
            return False


class Currencies(models.Model):
    name = models.CharField(max_length=15, null=False, blank=False, verbose_name="Currency Name")
    symbol = models.CharField(max_length=5, null=False, blank=False, verbose_name="Currency Symbol")

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"

    def __str__(self):
        return self.name + self.symbol


class Prices(models.Model):
    title = models.CharField(max_length=20, verbose_name="Price Plan Title", blank=False, null=False)
    detail = models.CharField(max_length=200, verbose_name="Price Plan Detail")
    price = models.FloatField(verbose_name="Prize")
    currency = models.ForeignKey(Currencies, related_name="prices", verbose_name="Currency", on_delete=models.CASCADE,
                                 blank=False, null=True)
    fee = models.FloatField(verbose_name="Fee",default=0)
    category = models.ForeignKey(SubCategory, related_name="prices", verbose_name="Service", on_delete=models.CASCADE)

    def contest_price(self):
        try:
            return self.price + self.fee
        except Exception as e:
            print("Error in price")
            return None


class ExampleLogo(models.Model):
    image = models.ImageField(verbose_name="Image", upload_to="example_logos", blank=False, null=False)
    service = models.ForeignKey(SubCategory, verbose_name="Service", related_name="logos", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Example Logo"
        verbose_name_plural = "Example Logos"

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return "/static/dashboard/images/no_image.png"

    def __str__(self):
        return self.service.title or ''


class Finalist(models.Model):
    contest = models.ForeignKey(Contest, verbose_name="Contest", related_name="finalists", on_delete=models.CASCADE)
    entry = models.ForeignKey("designer.Work", verbose_name="Entry", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return str(self.entry.user) + 's ' + 'entry no:' + str(self.entry.id) or ''


class Feedback(models.Model):
    user = models.ForeignKey(User, verbose_name="user", related_name="feedbacks", on_delete=models.CASCADE)
    entry = models.ForeignKey("designer.Work", verbose_name="Entry", related_name="feedbacks", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Feedback Content", blank=False, null=False)
    created_date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE,
                               null=True, blank=True,
                               related_name="replies")

    def get_childrens(self):
        return Feedback.objects.filter(parent=self)

    @property
    def any_children(self):
        return Feedback.objects.filter(parent=self).exists()

    def is_editable(self):
        last_date = self.created_date + timedelta(minutes=3)
        if timezone.now() > last_date:
            return False
        else:
            return True


class Announcement(models.Model):
    contest = models.ForeignKey(Contest, verbose_name="Contest", related_name="anouns", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    is_general = models.BooleanField(default=True)
    content = models.TextField(blank=False, null=True)


class Invoice(models.Model):
    user = models.ForeignKey(User, verbose_name="User", related_name="invoices", on_delete=models.CASCADE)
    contest = models.OneToOneField(Contest, verbose_name="Contest", related_name="invoice", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    json = models.JSONField(default='{}')
    billing_json = models.JSONField(default='{}')


class Attachment(models.Model):
    contest = models.ForeignKey(Contest, verbose_name="Contest", related_name="attachments", on_delete=models.CASCADE)
    content = models.TextField(verbose_name="Content")
    image = models.FileField(verbose_name="Attachment Image", upload_to="contests/attachments")
    created_date = models.DateTimeField(auto_now_add=True)

    def get_image(self):
        if self.image:
            return self.image.url
        else:
            return "/static/dashboard/images/no_image.png"


class Discount(models.Model):
    FEE = (('0', '0%'), ('10', '%10'), ('15', '15%'), ('20', '20%'), ('25', '25%'),
           ('30', '30%'), ('50', '50%'), ('100', '100%'))
    title = models.CharField(verbose_name="Discount Title", max_length=120)
    code = models.CharField(verbose_name="Discount Code", max_length=30, unique=True)
    free_private = models.BooleanField(verbose_name="Is Free Private Project?", default=False)
    free_hidden = models.BooleanField(verbose_name="Is Free Hidden Project?", default=False)
    modify_fee = models.CharField(choices=FEE, max_length=15, verbose_name='Modify Fee', default="25")

    start_time = models.DateTimeField(default=timezone.now())
    end_time = models.DateTimeField(blank=True, null=True)

    count = models.PositiveIntegerField(verbose_name="How many times",
                                        help_text="How many times it can be applied by one user?", default=0)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + f' ({self.code})'


class DiscountEmail(models.Model):
    discount = models.ForeignKey(Discount, verbose_name="Discount", related_name="emails", on_delete=models.CASCADE)
    email = models.EmailField(verbose_name="Email", blank=False, null=False)


class DiscountEvent(models.Model):
    contest = models.ForeignKey(Contest, verbose_name="Applied Contest", related_name="discountevents",
                                on_delete=models.CASCADE)
    discount = models.ForeignKey(Discount, verbose_name="Applied Discount", related_name="events",
                                 on_delete=models.CASCADE)


class Poll(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)

    contest = models.ForeignKey(Contest, verbose_name="Contest", related_name="polls", on_delete=models.CASCADE)
    title = models.CharField(max_length=100, verbose_name="Poll Title")
    content = models.TextField(verbose_name="Poll Detail")
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self,*args,**kwargs):
        if not self.id:
            if Poll.objects.filter(uid=self.uid).exists():
                self.uid = uuid.uuid4()

        return super(Poll,self).save(*args,**kwargs)


class PollObject(models.Model):
    poll = models.ForeignKey(Poll, verbose_name="Poll", related_name="entries", on_delete=models.CASCADE)
    entry = models.ForeignKey("designer.Work", verbose_name="Entry", on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)

    def get_rate_ratio(self):
        total = self.poll_comments.count()
        data = {}
        count = self.poll_comments.filter(rate=5).count()
        for i in range(1, 6):
            count = self.poll_comments.filter(rate=i).count()
            if count == 0:
                rate = 0
            else:
                rate = int(100 / (total / count))
            data[i] = {
                "count": count,
                "rate": rate
            }
        return data

    def get_average_rating(self):
        pc = self.poll_comments.aggregate(Avg("rate"))['rate__avg']
        if not pc: pc = 0
        return pc


class PollComment(models.Model):
    user = models.ForeignKey(User, verbose_name="User", related_name="poll_comments", on_delete=models.CASCADE)

    poll = models.ForeignKey(Poll, verbose_name="Poll", related_name="poll_comments", on_delete=models.CASCADE)
    poll_object = models.ForeignKey(PollObject, related_name="poll_comments", verbose_name="Entry",
                                    on_delete=models.CASCADE)
    content = models.TextField()
    rate = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
