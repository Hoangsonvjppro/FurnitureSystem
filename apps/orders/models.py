from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Chờ xác nhận'),
        ('processing', 'Đang xử lý'),
        ('shipped', 'Đang giao hàng'),
        ('delivered', 'Đã giao hàng'),
        ('cancelled', 'Đã hủy'),
        ('refunded', 'Đã hoàn tiền'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Chờ thanh toán'),
        ('partial', 'Thanh toán một phần'),
        ('paid', 'Đã thanh toán'),
        ('refunded', 'Đã hoàn tiền'),
        ('failed', 'Thanh toán thất bại'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Tiền mặt'),
        ('credit_card', 'Thẻ tín dụng'),
        ('bank_transfer', 'Chuyển khoản'),
        ('paypal', 'PayPal'),
        ('momo', 'MoMo'),
        ('vnpay', 'VNPay'),
        ('zalopay', 'ZaloPay'),
    )
    
    order_number = models.CharField("Mã đơn hàng", max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="Khách hàng"
    )
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Chi nhánh"
    )
    status = models.CharField("Trạng thái đơn hàng", max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField("Trạng thái thanh toán", max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField("Phương thức thanh toán", max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    
    # Thông tin khách hàng
    full_name = models.CharField("Họ tên", max_length=100)
    email = models.EmailField("Email")
    phone = models.CharField("Số điện thoại", max_length=20)
    
    # Địa chỉ giao hàng
    shipping_address = models.TextField("Địa chỉ giao hàng")
    city = models.CharField("Thành phố", max_length=100)
    district = models.CharField("Quận/Huyện", max_length=100)
    ward = models.CharField("Phường/Xã", max_length=100)
    note = models.TextField("Ghi chú", blank=True)
    
    # Thông tin đơn hàng
    subtotal = models.DecimalField("Tạm tính", max_digits=12, decimal_places=2)
    shipping_fee = models.DecimalField("Phí vận chuyển", max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField("Thuế", max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField("Giảm giá", max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField("Tổng tiền", max_digits=12, decimal_places=2)
    paid_amount = models.DecimalField("Số tiền đã thanh toán", max_digits=12, decimal_places=2, default=0)
    
    # Thông tin thời gian
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    paid_at = models.DateTimeField("Ngày thanh toán", null=True, blank=True)
    shipped_at = models.DateTimeField("Ngày giao hàng", null=True, blank=True)
    delivered_at = models.DateTimeField("Ngày nhận hàng", null=True, blank=True)
    cancelled_at = models.DateTimeField("Ngày hủy", null=True, blank=True)
    
    # Thông tin người xử lý
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_orders',
        verbose_name="Người tạo"
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_orders',
        verbose_name="Người xử lý"
    )
    
    class Meta:
        verbose_name = "Đơn hàng"
        verbose_name_plural = "Đơn hàng"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn hàng #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Tạo mã đơn hàng"""
        now = timezone.now()
        year = now.strftime('%y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        random_str = str(uuid.uuid4().int)[:6]
        return f"OR{year}{month}{day}{random_str}"
    
    @property
    def is_paid(self):
        """Kiểm tra đơn hàng đã thanh toán chưa"""
        return self.payment_status == 'paid'
    
    @property
    def balance_due(self):
        """Số tiền còn lại cần thanh toán"""
        return self.total - self.paid_amount
    
    @property
    def can_cancel(self):
        """Kiểm tra đơn hàng có thể hủy không"""
        return self.status in ['pending', 'processing']


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Đơn hàng"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Sản phẩm"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name="Biến thể"
    )
    price = models.DecimalField("Đơn giá", max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField("Số lượng", default=1)
    discount = models.DecimalField("Giảm giá", max_digits=10, decimal_places=2, default=0)
    note = models.CharField("Ghi chú", max_length=255, blank=True)
    
    class Meta:
        verbose_name = "Chi tiết đơn hàng"
        verbose_name_plural = "Chi tiết đơn hàng"
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total(self):
        """Thành tiền"""
        return (self.price * self.quantity) - self.discount


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Đơn hàng"
    )
    amount = models.DecimalField("Số tiền", max_digits=12, decimal_places=2)
    payment_method = models.CharField("Phương thức thanh toán", max_length=20, choices=Order.PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField("Mã giao dịch", max_length=100, blank=True)
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=(
            ('pending', 'Đang xử lý'),
            ('completed', 'Hoàn thành'),
            ('failed', 'Thất bại'),
            ('refunded', 'Hoàn tiền'),
        ),
        default='pending'
    )
    payment_date = models.DateTimeField("Ngày thanh toán", default=timezone.now)
    note = models.TextField("Ghi chú", blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments',
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    
    class Meta:
        verbose_name = "Thanh toán"
        verbose_name_plural = "Thanh toán"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Thanh toán {self.amount} cho đơn hàng {self.order.order_number}"


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