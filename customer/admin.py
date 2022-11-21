from django.contrib import admin
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_json_widget.widgets import JSONEditorWidget

from designer.models import Work, FinalWork
from .models import SubCategory, MainCategory, Contest, ExampleLogo, Prices, Currencies, Finalist, Feedback, \
    Announcement, Invoice, Attachment, Discount, DiscountEmail, DiscountEvent, Poll, PollObject, PollComment
import jsonfield

# Register your models here.

@admin.register(ExampleLogo)
class ExampleLogoAdmin(admin.ModelAdmin):
    list_display = ["service","image"]

    class Meta:
        model=ExampleLogo

class PriceInline(admin.StackedInline):
    readonly_fields = ('contest_price',)

    fields = (
        "title",
        "detail",

        ("contest_price","price", "fee"),
        "currency",


    )

    def contest_price(self, obj):
        return obj.contest_price()
    model = Prices

    class Media:
        js = (

            'admintemplate/price.js',  # project static folder
        )

class FinalistInline(admin.StackedInline):
    model = Finalist

class FinalWorkInline(admin.StackedInline):
    model = FinalWork

class DiscountEmailInline(admin.StackedInline):
    model = DiscountEmail

class DiscountEventInline(admin.StackedInline):
    model = DiscountEvent

class PollCommentInline(admin.StackedInline):
    model = PollComment


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["id","title",'template_name',"parent"]
    inlines = [PriceInline]

    class Meta:
        model=SubCategory


@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ["title"]
    class Meta:
        model=MainCategory

@admin.register(Currencies)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["name"]
    class Meta:
        model=Currencies

@admin.register(Attachment)
class AttachAdmin(admin.ModelAdmin):
    list_display = ["contest","content"]
    class Meta:
        model=Attachment

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ["title","code"]
    radio_fields = {"modify_fee": admin.HORIZONTAL}
    inlines = [DiscountEmailInline]
    class Meta:
        model=Discount


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["id","user","contest","created_date"]
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }
    class Meta:
        model=Invoice


@admin.register(Contest)
class ContestAdmin(admin.ModelAdmin):
    
    list_display = ["title","user","category","created_date","status","is_temp","my_button_field"]

    inlines=[FinalWorkInline,FinalistInline,DiscountEventInline]
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }
    class Meta:
        model=Contest

    def my_button_field(self, obj):

        return render_to_string("includes/admin_button.html",{"contest":obj})


@admin.register(Announcement)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["contest","content","is_general","created_date"]
    class Meta:
        model=Announcement




@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ["uid","contest","title","content","created_date"]
    class Meta:
        model=Poll

@admin.register(PollObject)
class PollObjectAdmin(admin.ModelAdmin):
    list_display = ["poll","entry","created_date"]
    inlines = [PollCommentInline]
    class Meta:
        model=PollObject

