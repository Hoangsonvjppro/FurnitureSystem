from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator


class Stock(models.Model):
    """Tồn kho sản phẩm tại chi nhánh"""
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_("Sản phẩm")
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='stocks',
        verbose_name=_("Biến thể"),
        null=True,
        blank=True
    )
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='stocks',
        verbose_name=_("Chi nhánh")
    )
    quantity = models.PositiveIntegerField(_("Số lượng"), default=0)
    min_quantity = models.PositiveIntegerField(_("Số lượng tối thiểu"), default=5)
    max_quantity = models.PositiveIntegerField(_("Số lượng tối đa"), default=100)
    updated_at = models.DateTimeField(_("Cập nhật lúc"), auto_now=True)
    
    class Meta:
        verbose_name = _("Tồn kho")
        verbose_name_plural = _("Tồn kho")
        unique_together = ('product', 'variant', 'branch')
    
    def __str__(self):
        return f"{self.product.name} - {self.branch.name}: {self.quantity}"
    
    @property
    def needs_restock(self):
        """Kiểm tra nếu cần nhập thêm hàng"""
        return self.quantity <= self.min_quantity
    
    @property
    def overstocked(self):
        """Kiểm tra nếu tồn kho vượt quá mức tối đa"""
        return self.quantity >= self.max_quantity


class StockMovement(models.Model):
    """Ghi nhận các chuyển động kho"""
    MOVEMENT_TYPES = (
        ('IN', _('Nhập kho')),
        ('OUT', _('Xuất kho')),
        ('TRANSFER', _('Chuyển kho')),
        ('ADJUSTMENT', _('Điều chỉnh')),
        ('RETURN', _('Trả hàng')),
    )
    
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name=_("Sản phẩm")
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='movements',
        verbose_name=_("Biến thể"),
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(_("Số lượng"), validators=[MinValueValidator(1)])
    movement_type = models.CharField(_("Loại chuyển động"), max_length=10, choices=MOVEMENT_TYPES)
    from_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='outgoing_movements',
        verbose_name=_("Chi nhánh nguồn"),
        null=True,
        blank=True
    )
    to_branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='incoming_movements',
        verbose_name=_("Chi nhánh đích"),
        null=True,
        blank=True
    )
    reference = models.CharField(_("Tham chiếu"), max_length=100, blank=True)
    notes = models.TextField(_("Ghi chú"), blank=True)
    staff = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements',
        verbose_name=_("Nhân viên thực hiện")
    )
    created_at = models.DateTimeField(_("Thời gian"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Chuyển động kho")
        verbose_name_plural = _("Chuyển động kho")
        ordering = ['-created_at']
    
    def __str__(self):
        if self.movement_type == 'TRANSFER':
            return f"{self.get_movement_type_display()}: {self.product.name} ({self.quantity}) từ {self.from_branch.name} đến {self.to_branch.name}"
        elif self.movement_type == 'IN':
            return f"{self.get_movement_type_display()}: {self.product.name} ({self.quantity}) vào {self.to_branch.name}"
        elif self.movement_type == 'OUT':
            return f"{self.get_movement_type_display()}: {self.product.name} ({self.quantity}) từ {self.from_branch.name}"
        else:
            return f"{self.get_movement_type_display()}: {self.product.name} ({self.quantity})"


class Inventory(models.Model):
    """Phiếu kiểm kê hàng hóa"""
    STATUS_CHOICES = (
        ('DRAFT', _('Nháp')),
        ('IN_PROGRESS', _('Đang kiểm kê')),
        ('COMPLETED', _('Hoàn thành')),
        ('CANCELLED', _('Đã hủy')),
    )
    
    branch = models.ForeignKey(
        'branches.Branch',
        on_delete=models.CASCADE,
        related_name='inventories',
        verbose_name=_("Chi nhánh")
    )
    inventory_number = models.CharField(_("Mã kiểm kê"), max_length=50, unique=True)
    status = models.CharField(_("Trạng thái"), max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    notes = models.TextField(_("Ghi chú"), blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_inventories',
        verbose_name=_("Người tạo")
    )
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    completed_at = models.DateTimeField(_("Ngày hoàn thành"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Phiếu kiểm kê")
        verbose_name_plural = _("Phiếu kiểm kê")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Kiểm kê #{self.inventory_number} - {self.branch.name}"
    
    def save(self, *args, **kwargs):
        if not self.inventory_number:
            # Generate inventory number
            last_inventory = Inventory.objects.order_by('-id').first()
            last_id = last_inventory.id if last_inventory else 0
            self.inventory_number = f"INV{timezone.now().strftime('%Y%m%d')}{last_id + 1:04d}"
        super().save(*args, **kwargs)


class InventoryItem(models.Model):
    """Chi tiết kiểm kê từng sản phẩm"""
    inventory = models.ForeignKey(
        Inventory,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Phiếu kiểm kê")
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='inventory_items',
        verbose_name=_("Sản phẩm")
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        related_name='inventory_items',
        verbose_name=_("Biến thể"),
        null=True,
        blank=True
    )
    expected_quantity = models.PositiveIntegerField(_("Số lượng hệ thống"), default=0)
    actual_quantity = models.PositiveIntegerField(_("Số lượng thực tế"), default=0)
    notes = models.TextField(_("Ghi chú"), blank=True)
    
    class Meta:
        verbose_name = _("Chi tiết kiểm kê")
        verbose_name_plural = _("Chi tiết kiểm kê")
        unique_together = ('inventory', 'product', 'variant')
    
    def __str__(self):
        return f"{self.product.name}: {self.actual_quantity}/{self.expected_quantity}"
    
    @property
    def is_discrepancy(self):
        """Check if there is a discrepancy between expected and actual quantity"""
        return self.expected_quantity != self.actual_quantity
    
    @property
    def discrepancy(self):
        """Calculate the discrepancy amount"""
        return self.actual_quantity - self.expected_quantity 