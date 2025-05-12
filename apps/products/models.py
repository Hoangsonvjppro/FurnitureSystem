from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator
from ckeditor.fields import RichTextField


class Category(models.Model):
    name = models.CharField("Tên danh mục", max_length=100)
    slug = models.SlugField("Slug", max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name="Danh mục cha")
    image = models.ImageField("Hình ảnh", upload_to='categories/', null=True, blank=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Kích hoạt", default=True)
    order = models.PositiveIntegerField("Thứ tự", default=0)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])
    
    @property
    def get_products(self):
        return self.products.filter(is_active=True)


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
    name = models.CharField("Tên sản phẩm", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True)
    sku = models.CharField("Mã sản phẩm", max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, 
                                related_name='products', verbose_name="Danh mục")
    description = RichTextField("Mô tả", blank=True)
    specifications = RichTextField("Thông số kỹ thuật", blank=True)
    price = models.DecimalField("Giá", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sale_price = models.DecimalField("Giá khuyến mãi", max_digits=10, decimal_places=2, 
                                    validators=[MinValueValidator(0)], null=True, blank=True)
    image = models.ImageField("Hình ảnh chính", upload_to='products/')
    is_active = models.BooleanField("Kích hoạt", default=True)
    is_featured = models.BooleanField("Nổi bật", default=False)
    in_stock = models.BooleanField("Còn hàng", default=True)
    tags = models.ManyToManyField(ProductTag, blank=True, related_name='products', verbose_name="Tags")
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Sản phẩm"
        verbose_name_plural = "Sản phẩm"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])
    
    @property
    def current_price(self):
        if self.sale_price:
            return self.sale_price
        return self.price
    
    @property
    def discount_percentage(self):
        if self.sale_price and self.price > 0:
            return int(100 - (self.sale_price * 100 / self.price))
        return 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='images', verbose_name="Sản phẩm")
    image = models.ImageField("Hình ảnh", upload_to='products/')
    alt_text = models.CharField("Mô tả hình ảnh", max_length=255, blank=True)
    is_primary = models.BooleanField("Hình ảnh chính", default=False)
    order = models.PositiveIntegerField("Thứ tự", default=0)
    
    class Meta:
        verbose_name = "Hình ảnh sản phẩm"
        verbose_name_plural = "Hình ảnh sản phẩm"
        ordering = ['order']
    
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
        if self.product.sale_price:
            return self.product.sale_price + self.price_adjustment
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