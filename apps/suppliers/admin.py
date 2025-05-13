from django.contrib import admin
from django.utils.html import format_html
from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    raw_id_fields = ['product']
    fields = ['product', 'quantity', 'unit_price', 'subtotal']
    readonly_fields = ['subtotal']
    
    def subtotal(self, obj):
        if obj.unit_price and obj.quantity:
            return f"{obj.unit_price * obj.quantity:,.2f} VND"
        return "0 VND"
    subtotal.short_description = "Thành tiền"


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'contact_person', 'phone', 'email', 'address']
    readonly_fields = ['created_at']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ('name', 'contact_person', 'phone', 'email')
        }),
        ('Thông tin chi tiết', {
            'fields': ('address', 'tax_code', 'website', 'notes', 'is_active')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    ]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'staff', 'status', 'created_at', 'total_amount']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'supplier__name', 'notes']
    readonly_fields = ['order_number', 'created_at', 'total_amount']
    inlines = [PurchaseOrderItemInline]
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ('order_number', 'supplier', 'staff', 'status')
        }),
        ('Thông tin ngày tháng', {
            'fields': ('created_at', 'confirmed_at', 'received_at')
        }),
        ('Thông tin tài chính', {
            'fields': ('total_amount', 'notes')
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        # Tự động gán người tạo là người dùng hiện tại
        if not change:
            obj.staff = request.user
            
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        
        # Cập nhật tổng số tiền đơn hàng
        total_amount = 0
        for obj in formset.cleaned_data:
            if obj and not obj.get('DELETE', False):
                quantity = obj.get('quantity', 0)
                unit_price = obj.get('unit_price', 0)
                total_amount += quantity * unit_price
        
        # Cập nhật tổng tiền cho đơn hàng
        form.instance.total_amount = total_amount
        form.instance.save()
        
        # Lưu các item
        for instance in instances:
            if instance.quantity > 0:
                instance.subtotal = instance.quantity * instance.unit_price
                instance.save()
        
        # Xóa các item đã đánh dấu delete
        for obj in formset.deleted_objects:
            obj.delete()


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'product', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['purchase_order__status', 'purchase_order__supplier']
    search_fields = ['purchase_order__order_number', 'product__name', 'product__sku']
    raw_id_fields = ['purchase_order', 'product']
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = "Thành tiền" 