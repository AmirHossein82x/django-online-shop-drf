from rest_framework_nested import routers

from .views import ProductViewSet

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = router.urls