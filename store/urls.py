from rest_framework_nested import routers
from django.urls import path

from .views import ProductViewSet,\
      ProductCoverViewSet, ReviewViewSet, CartViewSet, CartItemViewSet, CustomerViewSet

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('cart', CartViewSet, basename='cart')
router.register('customer', CustomerViewSet, basename='customer')

cover_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
cover_router.register('covers', ProductCoverViewSet, basename='cover')

review_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
review_router.register('reviews', ReviewViewSet, basename='review')

cart_item_router = routers.NestedDefaultRouter(router, 'cart', lookup='cart')
cart_item_router.register('items', CartItemViewSet, basename='cart_item')

urlpatterns = router.urls + cover_router.urls + review_router.urls + cart_item_router.urls
