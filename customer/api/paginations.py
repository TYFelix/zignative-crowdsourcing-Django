from rest_framework.pagination import PageNumberPagination

class ContestPagination(PageNumberPagination):
    page_size = 5