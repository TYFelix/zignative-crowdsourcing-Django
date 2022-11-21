import random
from datetime import timedelta

import django_filters
from django.db.models import Value, CharField, IntegerField, Count, Max, QuerySet
from django.http import HttpResponse
# from rest_framework.filters import OrderingFilter
from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_tricks.filters import OrderingFilter

from customer.api.paginations import ContestPagination
from customer.api.serializers import ContestSerializer, AllCategorySerializer
from customer.models import Contest, SubCategory
from user.api.permissions import IsAuthorized, IsCompleted


class ContestListAPIView(ListAPIView):
    serializer_class = ContestSerializer

    filter_backends = [OrderingFilter,django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ('category','status','round','is_locked')
    pagination_class = ContestPagination

    def get_queryset(self):
        qs=Contest.objects.filter(is_paid=True,is_draft=False,is_temp=False)

        try :
            if self.request.GET["is_private"] == "true": qs = qs.filter(form_fields__is_private=True)
        except KeyError:
            pass
        try :
            if self.request.GET["is_hidden"] == "true": qs = qs.filter(form_fields__is_hidden=True)
        except KeyError:
            pass
        try :
            if self.request.GET["is_guaranteed"] == "true": qs = qs.filter(form_fields__is_guaranteed=True)
        except KeyError:
            pass

        try:
            min=self.request.GET["prize_min"]
            qs=qs.filter(prize__gt=min)
        except KeyError:
            pass

        try:
            max=self.request.GET["prize_max"]
            qs=qs.filter(prize__lt=max)
        except KeyError:
            pass

        try:
            if self.request.GET["ordering"] == "entry_count":
                qs = qs.annotate(entry_count=Count('entries')) \
                                .order_by('-entry_count')
            elif self.request.GET["ordering"] == "-entry_count":
                qs = qs.annotate(entry_count=Count('entries')) \
                                .order_by('entry_count')
        except KeyError:
            pass

        try:
            df=self.request.GET["days_left"]
            if df == "1":

                qs = qs.filter(finish_date__range=[timezone.now(),timezone.now() + timedelta(days=1)])
            if df == "2":

                qs = qs.filter(finish_date__range=[timezone.now() + timedelta(days=1),timezone.now() + timedelta(days=2)])

            if df == "3":

                qs = qs.filter(finish_date__range=[timezone.now() + timedelta(days=2),timezone.now() + timedelta(days=3)])

            if df == "4":

                qs = qs.filter(finish_date__gt=timezone.now() + timedelta(days=3))


        except KeyError:
            pass

        return qs



class ContestDetailAPIView(RetrieveAPIView):
    queryset = Contest.objects.all()
    serializer_class = ContestSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthorized,IsCompleted]

class AllCategoryListAPIView(ListAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = AllCategorySerializer

