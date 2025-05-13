from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField


class Category(models.Model):
    """Danh mục sản phẩm"""
    name = models.CharField(_("Tên danh mục"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    parent = models.ForeignKey('self', verbose_name=_("Danh mục cha"), 
                              on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='children')
    description = models.TextField(_("Mô tả"), blank=True)
    image = models.ImageField(_("Hình ảnh"), upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(_("Kích hoạt"), default=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Danh mục")
        verbose_name_plural = _("Danh mục")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})
    
    @property
    def get_all_children(self):
        """Lấy tất cả danh mục con (đệ quy)"""
        children = list(self.children.all())
        for child in self.children.all():
            children.extend(child.get_all_children)
        return children


class ProductTag(models.Model):
    name = models.CharField("Tên tag", max_length=50)
    slug = models.SlugField("Slug", max_length=50, unique=True)
    
    class Meta:
        verbose_name = "Tag sản phẩm"
        verbose_name_plural = "Tags sản phẩm"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Sản phẩm"""
    name = models.CharField(_("Tên sản phẩm"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=200, unique=True)
    sku = models.CharField(_("Mã sản phẩm"), max_length=50, unique=True)
    description = models.TextField(_("Mô tả"))
    price = models.DecimalField(_("Giá"), max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(_("Giá khuyến mãi"), max_digits=10, decimal_places=2, 
                                       null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name=_("Danh mục"), 
                               on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey('suppliers.Supplier', verbose_name=_("Nhà cung cấp"), 
                               on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(_("Hình ảnh chính"), upload_to='products/')
    is_active = models.BooleanField(_("Kích hoạt"), default=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    updated_at = models.DateTimeField(_("Ngày cập nhật"), auto_now=True)
    featured = models.BooleanField(_("Sản phẩm nổi bật"), default=False)
    weight = models.FloatField(_("Trọng lượng (kg)"), null=True, blank=True)
    dimensions = models.CharField(_("Kích thước (DxRxC cm)"), max_length=50, blank=True)
    material = models.CharField(_("Chất liệu"), max_length=100, blank=True)
    color = models.CharField(_("Màu sắc"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Sản phẩm")
        verbose_name_plural = _("Sản phẩm")
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def get_discount_percentage(self):
        """Tính phần trăm giảm giá"""
        if self.discount_price:
            return round((self.price - self.discount_price) / self.price * 100)
        return 0
    
    @property
    def get_actual_price(self):
        """Lấy giá thực tế (giá sau khuyến mãi nếu có)"""
        return self.discount_price if self.discount_price else self.price


class ProductImage(models.Model):
    """Hình ảnh phụ của sản phẩm"""
    product = models.ForeignKey(Product, verbose_name=_("Sản phẩm"), 
                              on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_("Hình ảnh"), upload_to='products/')
    alt_text = models.CharField(_("Alt text"), max_length=200, blank=True)
    
    class Meta:
        verbose_name = _("Hình ảnh sản phẩm")
        verbose_name_plural = _("Hình ảnh sản phẩm")
    
    def __str__(self):
        return f"Hình ảnh của {self.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='variants', verbose_name="Sản phẩm")
    name = models.CharField("Tên biến thể", max_length=255)
    sku = models.CharField("Mã biến thể", max_length=50, unique=True)
    price_adjustment = models.DecimalField("Điều chỉnh giá", max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField("Số lượng tồn kho", default=0)
    is_active = models.BooleanField("Kích hoạt", default=True)
    
    class Meta:
        verbose_name = "Biến thể sản phẩm"
        verbose_name_plural = "Biến thể sản phẩm"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    @property
    def price(self):
        base_price = self.product.price
        return base_price + self.price_adjustment
    
    @property
    def sale_price(self):
        if self.product.discount_price:
            return self.product.discount_price + self.price_adjustment
        return None


class VariantAttribute(models.Model):
    ATTRIBUTE_TYPES = (
        ('color', 'Màu sắc'),
        ('size', 'Kích thước'),
        ('material', 'Chất liệu'),
        ('style', 'Kiểu dáng'),
        ('other', 'Khác'),
    )
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, 
                              related_name='attributes', verbose_name="Biến thể")
    attribute_type = models.CharField("Loại thuộc tính", max_length=50, choices=ATTRIBUTE_TYPES)
    value = models.CharField("Giá trị", max_length=100)
    
    class Meta:
        verbose_name = "Thuộc tính biến thể"
        verbose_name_plural = "Thuộc tính biến thể"
        unique_together = ('variant', 'attribute_type')
    
    def __str__(self):
        return f"{self.get_attribute_type_display()}: {self.value}" 