from django.contrib import admin
from django.utils.html import format_html
from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0
    raw_id_fields = ['product', 'variant']
    fields = ['product', 'variant', 'quantity', 'unit_price', 'received_quantity', 'total_price']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        if obj.unit_price and obj.quantity:
            return f"{obj.unit_price * obj.quantity:,.2f} VND"
        return "0 VND"
    total_price.short_description = "Thành tiền"


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_person', 'phone', 'email', 'display_rating', 'is_active']
    list_filter = ['is_active', 'rating', 'created_at']
    search_fields = ['name', 'code', 'contact_person', 'phone', 'email', 'address']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ('name', 'code', 'contact_person', 'phone', 'email')
        }),
        ('Thông tin chi tiết', {
            'fields': ('address', 'tax_code', 'website', 'description', 'rating', 'is_active')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    def display_rating(self, obj):
        if obj.rating:
            stars = '★' * obj.rating + '☆' * (5 - obj.rating)
            return format_html('<span style="color: #FFD700;">{}</span>', stars)
        return "Chưa đánh giá"
    display_rating.short_description = "Đánh giá"


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'supplier', 'branch', 'status', 'order_date', 'total_amount', 'created_by']
    list_filter = ['status', 'branch', 'order_date', 'created_at']
    search_fields = ['order_number', 'supplier__name', 'notes']
    readonly_fields = ['order_number', 'created_by', 'created_at', 'updated_at', 'total_amount']
    inlines = [PurchaseOrderItemInline]
    fieldsets = [
        ('Thông tin cơ bản', {
            'fields': ('order_number', 'supplier', 'branch', 'status')
        }),
        ('Thông tin ngày tháng', {
            'fields': ('order_date', 'expected_date', 'received_date')
        }),
        ('Thông tin tài chính', {
            'fields': ('total_amount', 'notes')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    def save_model(self, request, obj, form, change):
        # Tự động gán người tạo là người dùng hiện tại
        if not change:
            obj.created_by = request.user
            
            # Tạo mã đơn hàng tự động nếu chưa có
            if not obj.order_number:
                prefix = "PO"
                last_order = PurchaseOrder.objects.order_by('-created_at').first()
                if last_order and last_order.order_number and last_order.order_number.startswith(prefix):
                    try:
                        last_number = int(last_order.order_number[len(prefix):])
                        obj.order_number = f"{prefix}{last_number + 1:06d}"
                    except ValueError:
                        obj.order_number = f"{prefix}000001"
                else:
                    obj.order_number = f"{prefix}000001"
                    
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
                instance.save()
        
        # Xóa các item đã đánh dấu delete
        for obj in formset.deleted_objects:
            obj.delete()


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'product', 'variant', 'quantity', 'unit_price', 'received_quantity', 'display_total']
    list_filter = ['purchase_order__status', 'purchase_order__supplier']
    search_fields = ['purchase_order__order_number', 'product__name', 'product__code']
    raw_id_fields = ['purchase_order', 'product', 'variant']
    
    def display_total(self, obj):
        return f"{obj.quantity * obj.unit_price:,.2f} VND"
    display_total.short_description = "Thành tiền" 