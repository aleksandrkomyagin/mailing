from django.core.paginator import Paginator

from rest_framework.pagination import PageNumberPagination

from mailing.settings import PAGE_SIZE


class LimitPagePagination(PageNumberPagination):
    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
    page_query_param = 'page'
    django_paginator_class = Paginator
