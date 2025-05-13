from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Order(models.Model):
    """Đơn hàng của khách hàng"""
    STATUS_CHOICES = (
        ('PENDING', _('Chờ xác nhận')),
        ('CONFIRMED', _('Đã xác nhận')),
        ('SHIPPING', _('Đang giao hàng')),
        ('DELIVERED', _('Đã giao hàng')),
        ('CANCELLED', _('Đã hủy')),
    )
    
    PAYMENT_METHODS = (
        ('CASH', _('Tiền mặt')),
        ('BANK_TRANSFER', _('Chuyển khoản')),
        ('CREDIT_CARD', _('Thẻ tín dụng')),
        ('MOMO', _('Ví MoMo')),
        ('ZALOPAY', _('ZaloPay')),
    )
    
    order_number = models.CharField(_("Mã đơn hàng"), max_length=50, unique=True)
    customer = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Khách hàng")
    )
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Chi nhánh")
    )
    status = models.CharField(_("Trạng thái"), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Thông tin giao hàng
    recipient_name = models.CharField(_("Tên người nhận"), max_length=100)
    recipient_phone = models.CharField(_("Số điện thoại"), max_length=20)
    shipping_address = models.TextField(_("Địa chỉ giao hàng"))
    city = models.CharField(_("Thành phố"), max_length=100)
    district = models.CharField(_("Quận/Huyện"), max_length=100)
    ward = models.CharField(_("Phường/Xã"), max_length=100)
    
    # Thông tin thanh toán
    payment_method = models.CharField(_("Phương thức thanh toán"), max_length=20, choices=PAYMENT_METHODS)
    is_paid = models.BooleanField(_("Đã thanh toán"), default=False)
    
    # Thông tin giá
    subtotal = models.DecimalField(_("Tạm tính"), max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField(_("Phí vận chuyển"), max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(_("Thuế"), max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(_("Giảm giá"), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_("Tổng tiền"), max_digits=12, decimal_places=2)
    
    # Thông tin thời gian
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    confirmed_at = models.DateTimeField(_("Ngày xác nhận"), null=True, blank=True)
    shipped_at = models.DateTimeField(_("Ngày giao hàng"), null=True, blank=True)
    delivered_at = models.DateTimeField(_("Ngày nhận hàng"), null=True, blank=True)
    cancelled_at = models.DateTimeField(_("Ngày hủy"), null=True, blank=True)
    
    # Thông tin khác
    notes = models.TextField(_("Ghi chú"), blank=True)
    sales_staff = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='processed_orders',
        verbose_name=_("Nhân viên xử lý"),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _("Đơn hàng")
        verbose_name_plural = _("Đơn hàng")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn hàng #{self.order_number} - {self.customer.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            last_order = Order.objects.order_by('-id').first()
            last_id = last_order.id if last_order else 0
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d')}{last_id + 1:04d}"
        
        # Calculate total
        self.subtotal = sum(item.subtotal for item in self.items.all()) if self.id else Decimal('0')
        self.total = self.subtotal + self.shipping_fee + self.tax - self.discount
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Chi tiết đơn hàng"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Đơn hàng")
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name=_("Sản phẩm")
    )
    quantity = models.PositiveIntegerField(_("Số lượng"))
    price = models.DecimalField(_("Giá bán"), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_("Thành tiền"), max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = _("Chi tiết đơn hàng")
        verbose_name_plural = _("Chi tiết đơn hàng")
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)
        
        # Update order subtotal
        if self.order.id:
            self.order.save()


class Payment(models.Model):
    """Thanh toán đơn hàng"""
    PAYMENT_STATUS = (
        ('PENDING', _('Chờ thanh toán')),
        ('COMPLETED', _('Đã thanh toán')),
        ('FAILED', _('Thanh toán thất bại')),
        ('REFUNDED', _('Đã hoàn tiền')),
    )
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_("Đơn hàng")
    )
    amount = models.DecimalField(_("Số tiền"), max_digits=12, decimal_places=2)
    payment_method = models.CharField(_("Phương thức thanh toán"), max_length=20, choices=Order.PAYMENT_METHODS)
    status = models.CharField(_("Trạng thái"), max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    transaction_id = models.CharField(_("Mã giao dịch"), max_length=100, blank=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    completed_at = models.DateTimeField(_("Ngày hoàn thành"), null=True, blank=True)
    notes = models.TextField(_("Ghi chú"), blank=True)
    
    class Meta:
        verbose_name = _("Thanh toán")
        verbose_name_plural = _("Thanh toán")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Thanh toán {self.amount} cho đơn hàng #{self.order.order_number} - {self.get_status_display()}"


class Delivery(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='delivery',
        verbose_name="Đơn hàng"
    )
    tracking_number = models.CharField("Mã vận đơn", max_length=100, blank=True)
    carrier = models.CharField("Đơn vị vận chuyển", max_length=100, blank=True)
    delivery_date = models.DateField("Ngày giao hàng dự kiến", null=True, blank=True)
    delivered_date = models.DateTimeField("Ngày giao hàng thực tế", null=True, blank=True)
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=(
            ('pending', 'Chờ lấy hàng'),
            ('shipping', 'Đang giao hàng'),
            ('delivered', 'Đã giao hàng'),
            ('failed', 'Giao hàng thất bại'),
            ('returned', 'Đã trả hàng'),
        ),
        default='pending'
    )
    notes = models.TextField("Ghi chú", blank=True)
    
    class Meta:
        verbose_name = "Giao hàng"
        verbose_name_plural = "Giao hàng"
    
    def __str__(self):
        return f"Giao hàng cho đơn hàng {self.order.order_number}" 