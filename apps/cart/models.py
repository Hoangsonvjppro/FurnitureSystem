from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Người dùng"
    )
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Giỏ hàng"
    
    def __str__(self):
        return f"Giỏ hàng của {self.user.get_full_name() or self.user.username}"
    
    @property
    def total_items(self):
        """Tổng số lượng sản phẩm trong giỏ hàng"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def total_price(self):
        """Tổng giá trị giỏ hàng"""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Giỏ hàng"
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name="Sản phẩm"
    )
    variant = models.ForeignKey(
        'products.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cart_items',
        verbose_name="Biến thể"
    )
    quantity = models.PositiveIntegerField("Số lượng", default=1)
    added_at = models.DateTimeField("Ngày thêm", auto_now_add=True)
    
    class Meta:
        verbose_name = "Sản phẩm trong giỏ hàng"
        verbose_name_plural = "Sản phẩm trong giỏ hàng"
        unique_together = ('cart', 'product', 'variant')
    
    def __str__(self):
        variant_name = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_name} ({self.quantity})"
    
    @property
    def price(self):
        """Đơn giá sản phẩm"""
        if self.variant:
            if self.variant.price:
                return self.variant.price
        
        # Nếu không có biến thể hoặc biến thể không có giá riêng
        return self.product.sale_price or self.product.price
    
    @property
    def total_price(self):
        """Thành tiền"""
        return self.price * self.quantity 