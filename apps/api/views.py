from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.products.models import Product, Category, ProductVariant
from apps.branches.models import Branch
from apps.accounts.models import User, CustomerProfile
from apps.orders.models import Order
from apps.inventory.models import Stock, StockMovement
from apps.suppliers.models import Supplier, PurchaseOrder
from apps.api.serializers import (
    ProductSerializer, 
    ProductCategorySerializer, 
    BranchSerializer,
    OrderSerializer,
    StockSerializer,
    StockMovementSerializer,
    SupplierSerializer,
    PurchaseOrderSerializer,
    UserSerializer,
    ProductVariantSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint cho sản phẩm"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Lấy danh sách biến thể cho một sản phẩm cụ thể"""
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product, is_active=True)
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """API endpoint cho biến thể sản phẩm"""
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'is_active']


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint cho danh mục sản phẩm"""
    queryset = Category.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['parent']
    search_fields = ['name']


class BranchViewSet(viewsets.ModelViewSet):
    """API endpoint cho chi nhánh"""
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'address']


class OrderViewSet(viewsets.ModelViewSet):
    """API endpoint cho đơn hàng"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'branch']
    search_fields = ['order_number', 'full_name', 'phone', 'email']
    ordering_fields = ['created_at', 'updated_at', 'total']


class StockViewSet(viewsets.ModelViewSet):
    """API endpoint cho tồn kho"""
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['branch', 'product', 'variant']


class StockMovementViewSet(viewsets.ModelViewSet):
    """API endpoint cho chuyển động kho"""
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['branch', 'product', 'movement_type']
    ordering_fields = ['performed_at']


class SupplierViewSet(viewsets.ModelViewSet):
    """API endpoint cho nhà cung cấp"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'contact_person', 'phone', 'email']


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """API endpoint cho đơn hàng nhập"""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'branch', 'status']
    search_fields = ['order_number']
    ordering_fields = ['order_date', 'created_at']


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint cho người dùng"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_branch_manager', 'is_sales_staff', 'is_inventory_staff', 'branch']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number'] 