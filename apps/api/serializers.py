from rest_framework import serializers
from apps.products.models import Product, Category, ProductVariant, ProductImage
from apps.branches.models import Branch
from apps.accounts.models import User, CustomerProfile, ShippingAddress
from apps.orders.models import Order, OrderItem, Payment, Delivery
from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem
from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 
                  'is_active', 'branch', 'is_branch_manager', 'is_sales_staff', 'is_inventory_staff']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'tax_code', 'company_name', 'points', 'is_vip']


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'recipient_name', 'phone', 'address', 'city', 'district', 'ward', 'is_default']


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address', 'phone', 'email', 'is_active']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'description', 'is_active']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer cho biến thể sản phẩm"""
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'stock_quantity', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'is_primary', 'alt_text']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer cho sản phẩm"""
    category_name = serializers.StringRelatedField(source='category', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'description', 'price', 'category', 
                  'category_name', 'stock_quantity', 'is_active', 'variants']


class StockSerializer(serializers.ModelSerializer):
    """Serializer cho tồn kho"""
    product_name = serializers.StringRelatedField(source='product', read_only=True)
    variant_name = serializers.StringRelatedField(source='variant', read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    
    class Meta:
        model = Stock
        fields = ['id', 'product', 'product_name', 'variant', 'variant_name', 
                  'branch', 'branch_name', 'quantity', 'min_quantity', 'max_quantity']


class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer cho chuyển động kho"""
    product_name = serializers.StringRelatedField(source='product', read_only=True)
    variant_name = serializers.StringRelatedField(source='variant', read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'product_name', 'variant', 'variant_name', 
                  'branch', 'branch_name', 'movement_type', 'quantity', 
                  'reference', 'performed_at', 'performed_by']


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer cho nhà cung cấp"""
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'code', 'contact_person', 'phone', 'email', 
                  'address', 'is_active', 'rating']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer cho chi tiết đơn hàng nhập"""
    product_name = serializers.StringRelatedField(source='product', read_only=True)
    variant_name = serializers.StringRelatedField(source='variant', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'product', 'product_name', 'variant', 'variant_name', 
                  'quantity', 'unit_price', 'received_quantity']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer cho đơn hàng nhập"""
    supplier_name = serializers.StringRelatedField(source='supplier', read_only=True)
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'order_number', 'supplier', 'supplier_name', 'branch', 
                  'branch_name', 'status', 'order_date', 'expected_date', 
                  'received_date', 'total_amount', 'items']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'variant', 
                 'price', 'quantity', 'discount', 'note', 'total']
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'transaction_id', 
                 'status', 'payment_date', 'note']


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'order', 'tracking_number', 'carrier', 'delivery_date', 
                 'delivered_date', 'status', 'notes']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer cho đơn hàng"""
    branch_name = serializers.StringRelatedField(source='branch', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'branch', 'branch_name', 'created_at', 
                  'status', 'payment_status', 'total', 'full_name', 'phone', 'email'] 