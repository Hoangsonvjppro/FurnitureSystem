from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F

from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem


class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'branch', 'quantity', 'min_quantity', 'max_quantity', 'stock_status', 'updated_at']
    list_filter = ['branch', 'product__category']
    search_fields = ['product__name', 'product__sku']
    readonly_fields = ['updated_at']
    autocomplete_fields = ['product', 'branch']
    
    def stock_status(self, obj):
        if obj.quantity <= obj.min_quantity:
            return format_html('<span style="color: red; font-weight: bold;">Thấp</span>')
        elif obj.quantity >= obj.max_quantity:
            return format_html('<span style="color: orange; font-weight: bold;">Cao</span>')
        else:
            return format_html('<span style="color: green;">Bình thường</span>')
    stock_status.short_description = "Trạng thái"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'branch')


class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'from_branch', 'to_branch', 'staff', 'created_at']
    list_filter = ['movement_type', 'from_branch', 'to_branch', 'created_at']
    search_fields = ['product__name', 'product__sku', 'reference', 'notes']
    readonly_fields = ['created_at']
    autocomplete_fields = ['product', 'from_branch', 'to_branch', 'staff']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'from_branch', 'to_branch', 'staff')


class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 0
    readonly_fields = ['product', 'expected_quantity', 'discrepancy']
    fields = ['product', 'expected_quantity', 'actual_quantity', 'discrepancy', 'notes']
    
    def discrepancy(self, obj):
        if obj.pk:  # Only compute if the object has been saved
            diff = obj.actual_quantity - obj.expected_quantity
            if diff > 0:
                return format_html('<span style="color: green;">+{}</span>', diff)
            elif diff < 0:
                return format_html('<span style="color: red;">{}</span>', diff)
            return "0"
        return "-"
    discrepancy.short_description = "Chênh lệch"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class InventoryAdmin(admin.ModelAdmin):
    list_display = ['inventory_number', 'branch', 'status', 'created_by', 'created_at', 'completed_at']
    list_filter = ['status', 'branch', 'created_at']
    search_fields = ['branch__name', 'inventory_number', 'notes']
    readonly_fields = ['created_at', 'created_by', 'completed_at']
    inlines = [InventoryItemInline]
    
    fieldsets = (
        ('Thông tin kiểm kê', {
            'fields': ('branch', 'inventory_number', 'status')
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
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('branch', 'created_by')


# Register your models here.
admin.site.register(Stock, StockAdmin)
admin.site.register(StockMovement, StockMovementAdmin)
admin.site.register(Inventory, InventoryAdmin) 