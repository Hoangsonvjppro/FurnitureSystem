from django.contrib import admin
from django.utils.html import format_html
from apps.orders.models import Order, OrderItem, Payment, Delivery


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total']
    autocomplete_fields = ['product', 'variant']


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
    list_display = ['order_number', 'full_name', 'phone', 'status', 
                   'payment_status', 'total', 'paid_amount', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'branch', 'created_at']
    search_fields = ['order_number', 'full_name', 'phone', 'email']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at', 
                      'shipped_at', 'delivered_at', 'cancelled_at', 'created_by', 
                      'processed_by', 'subtotal', 'total', 'paid_amount', 'balance_due']
    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_number', 'branch', 'status', 'payment_status', 'payment_method')
        }),
        ('Thông tin khách hàng', {
            'fields': ('customer', 'full_name', 'email', 'phone')
        }),
        ('Địa chỉ giao hàng', {
            'fields': ('shipping_address', 'city', 'district', 'ward')
        }),
        ('Thông tin thanh toán', {
            'fields': ('subtotal', 'shipping_fee', 'tax', 'discount', 'total', 'paid_amount', 'balance_due')
        }),
        ('Thông tin thời gian', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at', 'cancelled_at')
        }),
        ('Thông tin người xử lý', {
            'fields': ('created_by', 'processed_by')
        }),
        ('Ghi chú', {
            'fields': ('note',)
        })
    )
    inlines = [OrderItemInline, PaymentInline, DeliveryInline]
    
    def balance_due(self, obj):
        return obj.balance_due
    balance_due.short_description = "Số tiền còn lại"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'amount', 'payment_method', 'status', 'payment_date']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['created_at', 'created_by']
    
    def order_link(self, obj):
        url = f"/admin/orders/order/{obj.order.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
    order_link.short_description = "Đơn hàng" 