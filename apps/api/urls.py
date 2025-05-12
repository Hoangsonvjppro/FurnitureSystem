from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.api.views import (
    ProductViewSet, 
    ProductVariantViewSet,
    CategoryViewSet,
    BranchViewSet,
    OrderViewSet,
    StockViewSet,
    SupplierViewSet,
    UserViewSet
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'product-variants', ProductVariantViewSet, basename='product-variant')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'branches', BranchViewSet, basename='branch')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
] 