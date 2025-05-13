from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal


class Cart(models.Model):
    """Giỏ hàng của khách hàng"""
    customer = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_("Khách hàng")
    )
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    updated_at = models.DateTimeField(_("Ngày cập nhật"), auto_now=True)
    
    class Meta:
        verbose_name = _("Giỏ hàng")
        verbose_name_plural = _("Giỏ hàng")
    
    def __str__(self):
        return f"Giỏ hàng của {self.customer.get_full_name()}"
    
    @property
    def total_items(self):
        """Tổng số sản phẩm trong giỏ hàng"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Tổng giá trị giỏ hàng"""
        return sum(item.subtotal for item in self.items.all())
    
    def clear(self):
        """Xóa tất cả sản phẩm trong giỏ hàng"""
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    """Sản phẩm trong giỏ hàng"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Giỏ hàng")
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_("Sản phẩm")
    )
    quantity = models.PositiveIntegerField(_("Số lượng"), default=1)
    added_at = models.DateTimeField(_("Ngày thêm"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Sản phẩm giỏ hàng")
        verbose_name_plural = _("Sản phẩm giỏ hàng")
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    
    @property
    def price(self):
        """Giá của sản phẩm (đã tính khuyến mãi nếu có)"""
        return self.product.get_actual_price
    
    @property
    def subtotal(self):
        """Thành tiền"""
        return self.price * self.quantity 