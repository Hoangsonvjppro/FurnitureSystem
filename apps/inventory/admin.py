from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F

from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem


class StockAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'variant_name', 'branch_name', 'quantity', 'min_quantity', 'max_quantity', 'stock_status', 'updated_at']
    list_filter = ['branch', 'product__category']
    search_fields = ['product__name', 'product__sku', 'variant__name', 'variant__sku']
    readonly_fields = ['updated_at']
    autocomplete_fields = ['product', 'variant', 'branch']
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Sản phẩm"
    product_name.admin_order_field = 'product__name'
    
    def variant_name(self, obj):
        return obj.variant.name if obj.variant else "-"
    variant_name.short_description = "Biến thể"
    
    def branch_name(self, obj):
        return obj.branch.name
    branch_name.short_description = "Chi nhánh"
    branch_name.admin_order_field = 'branch__name'
    
    def stock_status(self, obj):
        if obj.quantity <= obj.min_quantity:
            return format_html('<span style="color: red; font-weight: bold;">Thấp</span>')
        elif obj.quantity >= obj.max_quantity:
            return format_html('<span style="color: orange; font-weight: bold;">Cao</span>')
        else:
            return format_html('<span style="color: green;">Bình thường</span>')
    stock_status.short_description = "Trạng thái"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'variant', 'branch')


class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'variant_name', 'branch_name', 'movement_type_display', 
                   'quantity', 'performed_by_name', 'performed_at']
    list_filter = ['movement_type', 'branch', 'performed_at']
    search_fields = ['product__name', 'product__sku', 'reference', 'notes']
    readonly_fields = ['performed_at', 'performed_by']
    autocomplete_fields = ['product', 'variant', 'branch', 'destination_branch']
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = "Sản phẩm"
    product_name.admin_order_field = 'product__name'
    
    def variant_name(self, obj):
        return obj.variant.name if obj.variant else "-"
    variant_name.short_description = "Biến thể"
    
    def branch_name(self, obj):
        return obj.branch.name
    branch_name.short_description = "Chi nhánh"
    branch_name.admin_order_field = 'branch__name'
    
    def movement_type_display(self, obj):
        movement_types = {
            'in': 'Nhập kho',
            'out': 'Xuất kho',
            'transfer': 'Chuyển kho',
            'adjustment': 'Điều chỉnh',
            'return': 'Trả hàng',
        }
        return movement_types.get(obj.movement_type, obj.movement_type)
    movement_type_display.short_description = "Loại chuyển động"
    
    def performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.get_full_name() or obj.performed_by.username
        return "-"
    performed_by_name.short_description = "Người thực hiện"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'variant', 'branch', 'performed_by')


class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0
    readonly_fields = ['product', 'variant', 'expected_quantity', 'difference']
    fields = ['product', 'variant', 'expected_quantity', 'actual_quantity', 'difference', 'notes']
    
    def difference(self, obj):
        if obj.pk:  # Only compute if the object has been saved
            diff = obj.actual_quantity - obj.expected_quantity
            if diff > 0:
                return format_html('<span style="color: green;">+{}</span>', diff)
            elif diff < 0:
                return format_html('<span style="color: red;">{}</span>', diff)
            return "0"
        return "-"
    difference.short_description = "Chênh lệch"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class InventoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'branch_name', 'inventory_date', 'status', 'created_by_name', 'created_at']
    list_filter = ['status', 'inventory_date', 'branch']
    search_fields = ['branch__name', 'notes']
    readonly_fields = ['created_at', 'created_by', 'completed_at']
    inlines = [InventoryItemInline]
    
    fieldsets = (
        ('Thông tin kiểm kê', {
            'fields': ('branch', 'inventory_date', 'status')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'completed_at')
        }),
        ('Người thực hiện', {
            'fields': ('created_by',)
        }),
        ('Ghi chú', {
            'fields': ('notes',)
        }),
    )
    
    def branch_name(self, obj):
        return obj.branch.name
    branch_name.short_description = "Chi nhánh"
    branch_name.admin_order_field = 'branch__name'
    
    def created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return "-"
    created_by_name.short_description = "Người tạo"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('branch', 'created_by')


# Register your models here.
admin.site.register(Stock, StockAdmin)
admin.site.register(StockMovement, StockMovementAdmin)
admin.site.register(Inventory, InventoryAdmin) 