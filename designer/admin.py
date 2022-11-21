from django.contrib import admin

# Register your models here.
from designer.models import Work, NDASigners, Review


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ["id","user","contest","image"]
    class Meta:
        model=Work

@admin.register(NDASigners)
class NDASignersAdmin(admin.ModelAdmin):
    list_display = ["user","contest","created_date"]
    class Meta:
        model=NDASigners


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["user","entry","writer"]
    class Meta:
        model=Review