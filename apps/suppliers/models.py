from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Supplier(models.Model):
    name = models.CharField("Tên nhà cung cấp", max_length=200)
    code = models.CharField("Mã nhà cung cấp", max_length=50, unique=True)
    contact_person = models.CharField("Người liên hệ", max_length=100, blank=True)
    phone = models.CharField("Số điện thoại", max_length=20)
    email = models.EmailField("Email", blank=True)
    address = models.TextField("Địa chỉ")
    tax_code = models.CharField("Mã số thuế", max_length=50, blank=True)
    website = models.URLField("Website", blank=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Kích hoạt", default=True)
    rating = models.PositiveSmallIntegerField(
        "Đánh giá", 
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Nhà cung cấp"
        verbose_name_plural = "Nhà cung cấp"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Nháp'),
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('received', 'Đã nhận hàng'),
        ('cancelled', 'Đã hủy'),
    )
    
    supplier = models.ForeignKey(
        Supplier, 
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name="Nhà cung cấp"
    )
    order_number = models.CharField("Mã đơn hàng", max_length=50, unique=True)
    branch = models.ForeignKey(
        'branches.Branch', 
        on_delete=models.CASCADE,
        related_name='purchase_orders',
        verbose_name="Chi nhánh"
    )
    status = models.CharField("Trạng thái", max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField("Ngày đặt hàng")
    expected_date = models.DateField("Ngày dự kiến nhận", null=True, blank=True)
    received_date = models.DateField("Ngày nhận hàng", null=True, blank=True)
    total_amount = models.DecimalField("Tổng tiền", max_digits=12, decimal_places=2, default=0)
    notes = models.TextField("Ghi chú", blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_purchase_orders',
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Đơn hàng nhập"
        verbose_name_plural = "Đơn hàng nhập"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn nhập hàng {self.order_number} - {self.supplier.name}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Đơn nhập hàng"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='purchase_items',
        verbose_name="Sản phẩm"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_items',
        verbose_name="Biến thể"
    )
    quantity = models.PositiveIntegerField("Số lượng")
    unit_price = models.DecimalField("Đơn giá", max_digits=10, decimal_places=2)
    received_quantity = models.PositiveIntegerField("Số lượng đã nhận", default=0)
    
    class Meta:
        verbose_name = "Chi tiết đơn nhập hàng"
        verbose_name_plural = "Chi tiết đơn nhập hàng"
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price 