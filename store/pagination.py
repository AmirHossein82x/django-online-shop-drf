from rest_framework.pagination import PageNumberPagination


class DefalutPageNumberPagination(PageNumberPagination):
    page_size = 10