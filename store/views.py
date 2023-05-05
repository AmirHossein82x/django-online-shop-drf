from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import permissions


from .models import Product, ProductCover, Review
from .serializer import ProductSerializer,\
      ProductCoverSerializer, ReviewShowSerializer,\
          ReviewCreateSerializer, ReviewShowAdminSerializer, ReviewUpdateSerializer
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
    

class ReviewViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch']

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [permissions.IsAdminUser()]
        elif self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        else:
            return [permissions.AllowAny()]

    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Review.objects.filter(product__slug=self.kwargs['product_slug'])
        return Review.objects.filter(product__slug=self.kwargs['product_slug'], is_show=True)
    
    def get_serializer_class(self):

        if self.request.method == 'POST':
            return ReviewCreateSerializer
        
        elif self.request.method == 'GET' and self.request.user.is_staff:
            return ReviewShowAdminSerializer
        
        elif self.request.method == 'GET' and not self.request.user.is_staff:
            return ReviewShowSerializer
        
        elif self.request.method == 'PATCH':
            return ReviewUpdateSerializer

    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context['product'] = get_object_or_404(Product, slug=self.kwargs['product_slug'])
        return context