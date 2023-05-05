from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import permissions


from .models import Product, ProductCover
from .serializer import ProductSerializer, ProductCoverSerializer
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


class ProductCoverViewSet(ModelViewSet):
    serializer_class = ProductCoverSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return ProductCover.objects.filter(product__slug=self.kwargs['product_slug'])
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product'] = get_object_or_404(Product, slug=self.kwargs['product_slug'])
        return context
