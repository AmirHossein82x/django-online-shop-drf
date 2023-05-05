from rest_framework_nested import routers

from .views import ProductViewSet, ProductCoverViewSet, ReviewViewSet

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')

cover_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
cover_router.register('covers', ProductCoverViewSet, basename='cover')

review_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
review_router.register('reviews', ReviewViewSet, basename='review')

urlpatterns = router.urls + cover_router.urls + review_router.urls