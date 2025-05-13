from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductTag, ProductVariant, VariantAttribute


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'order')
    list_per_page = 20


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')


class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 1
    fields = ('attribute_type', 'value')


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'sku', 'price_adjustment', 'stock_quantity', 'is_active')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'display_price', 'is_active', 'is_featured', 'in_stock', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'in_stock', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    list_editable = ('is_active', 'is_featured', 'in_stock')
    filter_horizontal = ('tags',)
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'sku', 'category', 'tags')
        }),
        ('Nội dung', {
            'fields': ('description', 'specifications')
        }),
        ('Giá và trạng thái', {
            'fields': ('price', 'sale_price', 'is_active', 'is_featured', 'in_stock')
        }),
        ('Hình ảnh', {
            'fields': ('image', 'display_image')
        }),
        ('Thông tin thêm', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    list_per_page = 20

    def display_price(self, obj):
        if obj.sale_price:
            return format_html('<span style="text-decoration: line-through;">{}</span> <span style="color: red;">{}</span>',
                             f'{int(obj.price):,}đ', f'{int(obj.sale_price):,}đ')
        return format_html('{:,}đ', int(obj.price))
    display_price.short_description = "Giá"

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "Không có hình ảnh"
    display_image.short_description = "Xem trước hình ảnh"


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'sku', 'price_adjustment', 'stock_quantity', 'is_active')
    list_filter = ('is_active', 'product')
    search_fields = ('name', 'sku', 'product__name')
    list_editable = ('price_adjustment', 'stock_quantity', 'is_active')
    inlines = [VariantAttributeInline]
    list_per_page = 20


class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_per_page = 20


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductTag, ProductTagAdmin) 