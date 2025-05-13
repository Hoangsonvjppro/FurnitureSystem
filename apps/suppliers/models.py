from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Supplier(models.Model):
    """Nhà cung cấp sản phẩm"""
    name = models.CharField(_("Tên nhà cung cấp"), max_length=100)
    contact_person = models.CharField(_("Người liên hệ"), max_length=100)
    phone = models.CharField(_("Số điện thoại"), max_length=20)
    email = models.EmailField(_("Email"), max_length=100)
    address = models.TextField(_("Địa chỉ"))
    tax_code = models.CharField(_("Mã số thuế"), max_length=20, blank=True)
    website = models.URLField(_("Website"), blank=True)
    is_active = models.BooleanField(_("Đang hoạt động"), default=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    notes = models.TextField(_("Ghi chú"), blank=True)
    
    class Meta:
        verbose_name = _("Nhà cung cấp")
        verbose_name_plural = _("Nhà cung cấp")
        ordering = ['name']
    
    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    """Đơn đặt hàng từ nhà cung cấp"""
    STATUS_CHOICES = (
        ('PENDING', _('Chờ xác nhận')),
        ('CONFIRMED', _('Đã xác nhận')),
        ('RECEIVED', _('Đã nhận hàng')),
        ('CANCELLED', _('Đã hủy')),
    )
    
    order_number = models.CharField(_("Mã đơn hàng"), max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, verbose_name=_("Nhà cung cấp"), 
                               on_delete=models.CASCADE, related_name='purchase_orders')
    staff = models.ForeignKey('accounts.User', verbose_name=_("Nhân viên tạo đơn"), 
                             on_delete=models.SET_NULL, null=True)
    status = models.CharField(_("Trạng thái"), max_length=20, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(_("Tổng tiền"), max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    confirmed_at = models.DateTimeField(_("Ngày xác nhận"), null=True, blank=True)
    received_at = models.DateTimeField(_("Ngày nhận hàng"), null=True, blank=True)
    notes = models.TextField(_("Ghi chú"), blank=True)
    
    class Meta:
        verbose_name = _("Đơn đặt hàng")
        verbose_name_plural = _("Đơn đặt hàng")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Đơn hàng #{self.order_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a unique order number
            last_order = PurchaseOrder.objects.order_by('-id').first()
            last_id = last_order.id if last_order else 0
            self.order_number = f"PO{timezone.now().strftime('%Y%m%d')}{last_id + 1:04d}"
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    """Chi tiết đơn đặt hàng"""
    purchase_order = models.ForeignKey(PurchaseOrder, verbose_name=_("Đơn đặt hàng"), 
                                     on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', verbose_name=_("Sản phẩm"), 
                              on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Số lượng"))
    unit_price = models.DecimalField(_("Đơn giá"), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_("Thành tiền"), max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = _("Chi tiết đơn đặt hàng")
        verbose_name_plural = _("Chi tiết đơn đặt hàng")
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs) 