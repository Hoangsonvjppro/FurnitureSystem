from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# This app doesn't define its own models but uses models from other apps 

class WebsiteConfig(models.Model):
    """Cấu hình website"""
    site_name = models.CharField(_("Tên trang web"), max_length=100)
    logo = models.ImageField(_("Logo"), upload_to='website/', null=True, blank=True)
    favicon = models.ImageField(_("Favicon"), upload_to='website/', null=True, blank=True)
    
    # Thông tin liên hệ
    contact_email = models.EmailField(_("Email liên hệ"))
    contact_phone = models.CharField(_("Số điện thoại liên hệ"), max_length=20)
    address = models.TextField(_("Địa chỉ"))
    
    # Nội dung
    about_us = models.TextField(_("Giới thiệu"), blank=True)
    privacy_policy = models.TextField(_("Chính sách bảo mật"), blank=True)
    terms_of_service = models.TextField(_("Điều khoản dịch vụ"), blank=True)
    
    # Mạng xã hội
    facebook_link = models.URLField(_("Facebook"), blank=True)
    instagram_link = models.URLField(_("Instagram"), blank=True)
    youtube_link = models.URLField(_("Youtube"), blank=True)
    tiktok_link = models.URLField(_("TikTok"), blank=True)
    
    # SEO
    meta_title = models.CharField(_("Meta Title"), max_length=100, blank=True)
    meta_description = models.TextField(_("Meta Description"), blank=True)
    meta_keywords = models.CharField(_("Meta Keywords"), max_length=255, blank=True)
    
    # Cập nhật
    updated_at = models.DateTimeField(_("Cập nhật lúc"), auto_now=True)
    updated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Người cập nhật"),
        related_name='website_configs'
    )
    
    class Meta:
        verbose_name = _("Cấu hình website")
        verbose_name_plural = _("Cấu hình website")
    
    def __str__(self):
        return self.site_name


class Banner(models.Model):
    """Banner quảng cáo trên website"""
    POSITION_CHOICES = (
        ('HOME_TOP', _('Trang chủ - Trên cùng')),
        ('HOME_MIDDLE', _('Trang chủ - Giữa trang')),
        ('HOME_BOTTOM', _('Trang chủ - Cuối trang')),
        ('CATEGORY', _('Trang danh mục')),
        ('PRODUCT', _('Trang sản phẩm')),
        ('SIDEBAR', _('Thanh bên')),
    )
    
    title = models.CharField(_("Tiêu đề"), max_length=100)
    image = models.ImageField(_("Hình ảnh"), upload_to='banners/')
    url = models.URLField(_("Đường dẫn"), blank=True)
    position = models.CharField(_("Vị trí"), max_length=20, choices=POSITION_CHOICES)
    is_active = models.BooleanField(_("Kích hoạt"), default=True)
    order = models.PositiveIntegerField(_("Thứ tự"), default=0)
    start_date = models.DateTimeField(_("Ngày bắt đầu"), default=timezone.now)
    end_date = models.DateTimeField(_("Ngày kết thúc"), null=True, blank=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banner")
        ordering = ['position', 'order']
    
    def __str__(self):
        return self.title
    
    @property
    def is_visible(self):
        """Kiểm tra banner có đang hiển thị không"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True 