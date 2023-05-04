from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter


from .models import Product
from .serializer import ProductSerializer
from .permission import IsAdminOrReadOnly
from .filter import ProductFilter

# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.available().select_related('promotion').select_related('category')
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = ('category',)
    filterset_class = ProductFilter
    search_fields = ('^title', )
