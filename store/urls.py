from rest_framework_nested import routers

from .views import ProductViewSet, ProductCoverViewSet

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')

cover_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
cover_router.register('covers', ProductCoverViewSet, basename='cover')

urlpatterns = router.urls + cover_router.urls