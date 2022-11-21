from django.utils.timesince import timesince
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from customer.models import Contest, SubCategory


class ContestSerializer(ModelSerializer):
    detail = serializers.SerializerMethodField(method_name="get_detail")
    currency_name = serializers.SerializerMethodField(method_name="get_currency_name")
    currency_symbol = serializers.SerializerMethodField(method_name="get_currency_symbol")
    is_guaranteed = serializers.SerializerMethodField(method_name="get_guaranteed")
    is_hidden = serializers.SerializerMethodField(method_name="get_hidden")
    is_private = serializers.SerializerMethodField(method_name="get_private")
    user = serializers.SerializerMethodField(method_name="get_username")
    category = serializers.SerializerMethodField(method_name="get_category")
    timesince = serializers.SerializerMethodField(method_name="get_timesince")
    last_feedback_timesince = serializers.SerializerMethodField(method_name="get_last_feedback_timesince")
    feedback_ratio = serializers.SerializerMethodField(method_name="get_feedback_ratio")
    rate_ratio = serializers.SerializerMethodField(method_name="get_rate_ratio")
    user_number_of_contests  = serializers.SerializerMethodField(method_name="get_user_number_of_contests")
    contest_image = serializers.SerializerMethodField(method_name="get_contest_image")
    remaining_time = serializers.SerializerMethodField(method_name="get_remaining_time")
    entry_count = serializers.SerializerMethodField(method_name="get_entry_count")



    class Meta:
        model=Contest
        fields=('title','detail','prize','currency_name','currency_symbol','slug','user','category','status','round'
                ,'created_date','finish_date','is_locked','is_guaranteed','is_hidden','is_private','timesince',
                'last_feedback_timesince','feedback_ratio','rate_ratio','user_number_of_contests','contest_image',
                'remaining_time','entry_count')

    def get_detail(self,obj):
        return obj.form_fields["contest_detail"]



    def get_currency_name(self,obj):
        return str(obj.get_price().currency.name)

    def get_currency_symbol(self,obj):
        return str(obj.get_price().currency.symbol)

    def get_guaranteed(self,obj):
        return obj.is_guaranteed()

    def get_hidden(self,obj):
        return obj.is_hidden()

    def get_private(self,obj):
        return obj.is_private()

    def get_username(self,obj):
        return obj.user.username

    def get_category(self,obj):
        return obj.category.title

    def get_timesince(self,obj):
        return timesince(obj.created_date)

    def get_last_feedback_timesince(self,obj):
        if obj.get_last_feedback():return timesince(obj.get_last_feedback().created_date)
        else: return None


    def get_feedback_ratio(self,obj):
        return obj.get_feedbacks()["percentage"]

    def get_rate_ratio(self,obj):
        return obj.rating_percentage()

    def get_user_number_of_contests(self,obj):
        return obj.user.contests.count()

    def get_contest_image(self,obj):
        return obj.get_image_api()

    def get_remaining_time(self,obj):
        return timesince(obj.get_timezone(),obj.finish_date)

    def get_entry_count(self,obj):
        return obj.get_entry_count()


class AllCategorySerializer(ModelSerializer):
    parent = serializers.SerializerMethodField(method_name="get_parent")

    class Meta:
        model = SubCategory
        fields = ('id','title', 'parent',)

    def get_parent(self,obj):
        return obj.parent.title


