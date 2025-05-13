from django.contrib import admin
from django.utils.html import format_html
from apps.orders.models import Order, OrderItem, Payment, Delivery


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']
    autocomplete_fields = ['product']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ['created_at']


class DeliveryInline(admin.StackedInline):
    model = Delivery
    can_delete = False
    max_num = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'recipient_name', 'recipient_phone', 'status', 
                   'is_paid', 'total', 'created_at']
    list_filter = ['status', 'is_paid', 'payment_method', 'branch', 'created_at']
    search_fields = ['order_number', 'recipient_name', 'recipient_phone']
    readonly_fields = ['order_number', 'created_at', 'confirmed_at', 
                      'shipped_at', 'delivered_at', 'cancelled_at', 
                      'subtotal', 'total']
    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_number', 'branch', 'status', 'payment_method', 'is_paid')
        }),
        ('Thông tin khách hàng', {
            'fields': ('customer', 'recipient_name', 'recipient_phone')
        }),
        ('Địa chỉ giao hàng', {
            'fields': ('shipping_address', 'city', 'district', 'ward')
        }),
        ('Thông tin thanh toán', {
            'fields': ('subtotal', 'shipping_fee', 'tax', 'discount', 'total')
        }),
        ('Thông tin thời gian', {
            'fields': ('created_at', 'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at')
        }),
        ('Thông tin người xử lý', {
            'fields': ('sales_staff',)
        }),
        ('Ghi chú', {
            'fields': ('notes',)
        })
    )
    inlines = [OrderItemInline, PaymentInline, DeliveryInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['created_at']
    
    def order_link(self, obj):
        url = f"/admin/orders/order/{obj.order.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = "Đơn hàng" 