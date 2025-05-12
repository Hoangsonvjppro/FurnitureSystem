from django.db import models
from django.utils import timezone


class Stock(models.Model):
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name="Chi nhánh"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name="Sản phẩm"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.CASCADE,
        related_name='stocks',
        null=True,
        blank=True,
        verbose_name="Biến thể"
    )
    quantity = models.PositiveIntegerField("Số lượng tồn kho", default=0)
    min_quantity = models.PositiveIntegerField("Số lượng tối thiểu", default=5)
    max_quantity = models.PositiveIntegerField("Số lượng tối đa", default=100)
    updated_at = models.DateTimeField("Cập nhật lần cuối", auto_now=True)
    
    class Meta:
        verbose_name = "Tồn kho"
        verbose_name_plural = "Tồn kho"
        unique_together = ('branch', 'product', 'variant')
    
    def __str__(self):
        variant_name = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_name} tại {self.branch.name}: {self.quantity}"
    
    @property
    def is_low_stock(self):
        """Kiểm tra nếu tồn kho thấp"""
        return self.quantity <= self.min_quantity
    
    @property
    def is_over_stock(self):
        """Kiểm tra nếu tồn kho vượt quá mức cho phép"""
        return self.quantity >= self.max_quantity


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Nhập kho'),
        ('out', 'Xuất kho'),
        ('transfer', 'Chuyển kho'),
        ('adjustment', 'Điều chỉnh'),
        ('return', 'Trả hàng'),
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="Sản phẩm"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='movements',
        null=True,
        blank=True,
        verbose_name="Biến thể"
    )
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="Chi nhánh"
    )
    destination_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='incoming_movements',
        null=True,
        blank=True,
        verbose_name="Chi nhánh đích"
    )
    movement_type = models.CharField("Loại chuyển động", max_length=10, choices=MOVEMENT_TYPES)
    quantity = models.PositiveIntegerField("Số lượng")
    reference = models.CharField("Tham chiếu", max_length=100, blank=True)
    notes = models.TextField("Ghi chú", blank=True)
    performed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements',
        verbose_name="Người thực hiện"
    )
    performed_at = models.DateTimeField("Thời gian thực hiện", default=timezone.now)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    
    class Meta:
        verbose_name = "Chuyển động kho"
        verbose_name_plural = "Chuyển động kho"
        ordering = ['-performed_at']
    
    def __str__(self):
        movement_type_display = dict(self.MOVEMENT_TYPES)[self.movement_type]
        return f"{movement_type_display} - {self.product.name} ({self.quantity})"


class Inventory(models.Model):
    """Kiểm kê kho"""
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name="Chi nhánh"
    )
    inventory_date = models.DateField("Ngày kiểm kê")
    status = models.CharField(
        "Trạng thái", 
        max_length=20, 
        choices=(
            ('draft', 'Nháp'),
            ('in_progress', 'Đang thực hiện'),
            ('completed', 'Hoàn thành'),
            ('cancelled', 'Đã hủy'),
        ),
        default='draft'
    )
    notes = models.TextField("Ghi chú", blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_inventories',
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    completed_at = models.DateTimeField("Ngày hoàn thành", null=True, blank=True)
    
    class Meta:
        verbose_name = "Kiểm kê kho"
        verbose_name_plural = "Kiểm kê kho"
        ordering = ['-inventory_date']
    
    def __str__(self):
        return f"Kiểm kê kho {self.branch.name} - {self.inventory_date}"


class InventoryItem(models.Model):
    """Chi tiết kiểm kê"""
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Kiểm kê"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name="Sản phẩm"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='inventory_items',
        null=True,
        blank=True,
        verbose_name="Biến thể"
    )
    expected_quantity = models.PositiveIntegerField("Số lượng dự kiến", default=0)
    actual_quantity = models.PositiveIntegerField("Số lượng thực tế", default=0)
    notes = models.TextField("Ghi chú", blank=True)
    
    class Meta:
        verbose_name = "Chi tiết kiểm kê"
        verbose_name_plural = "Chi tiết kiểm kê"
    
    def __str__(self):
        return f"{self.product.name} - Dự kiến: {self.expected_quantity}, Thực tế: {self.actual_quantity}"
    
    @property
    def difference(self):
        """Chênh lệch giữa số lượng thực tế và dự kiến"""
        return self.actual_quantity - self.expected_quantity 