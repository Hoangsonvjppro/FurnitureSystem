from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class User(AbstractUser):
    """Custom User model với thông tin mở rộng"""
    ROLE_CHOICES = (
        ('ADMIN', _('Admin')),
        ('CUSTOMER', _('Khách hàng')),
        ('INVENTORY_STAFF', _('Nhân viên quản lý kho')),
        ('SALES_STAFF', _('Nhân viên bán hàng')),
        ('MANAGER', _('Quản lý cửa hàng')),
    )
    
    phone_number = models.CharField(_("Số điện thoại"), max_length=15, blank=True)
    address = models.TextField(_("Địa chỉ"), blank=True)
    role = models.CharField(_("Vai trò"), max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    date_of_birth = models.DateField(_("Ngày sinh"), null=True, blank=True)
    avatar = models.ImageField(_("Ảnh đại diện"), upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    
    class Meta:
        verbose_name = _("Người dùng")
        verbose_name_plural = _("Người dùng")
    
    def get_full_name(self):
        """Trả về họ tên đầy đủ."""
        full_name = f"{self.last_name} {self.first_name}"
        return full_name.strip() or self.username
    
    def __str__(self):
        return self.get_full_name()
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
    
    @property
    def is_inventory_staff(self):
        return self.role == 'INVENTORY_STAFF'
    
    @property
    def is_sales_staff(self):
        return self.role == 'SALES_STAFF'
    
    @property
    def is_manager(self):
        return self.role == 'MANAGER'
    
    @property
    def is_customer(self):
        return self.role == 'CUSTOMER'
    
    def get_dashboard_url(self):
        """Trả về URL dashboard tương ứng với vai trò của user"""
        if self.is_admin:
            return '/admin/'
        if self.is_manager:
            return '/manager/'
        if self.is_sales_staff:
            return '/sales/'
        if self.is_inventory_staff:
            return '/inventory/'
        return '/profile/'


class CustomerProfile(models.Model):
    """Thông tin profile của khách hàng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    tax_code = models.CharField(_("Mã số thuế"), max_length=20, blank=True)
    company_name = models.CharField(_("Tên công ty"), max_length=200, blank=True)
    loyalty_points = models.PositiveIntegerField(_("Điểm tích lũy"), default=0)
    is_vip = models.BooleanField(_("Khách hàng VIP"), default=False)
    
    class Meta:
        verbose_name = _("Thông tin khách hàng")
        verbose_name_plural = _("Thông tin khách hàng")
    
    def __str__(self):
        return f"Hồ sơ của {self.user.get_full_name()}"


class ShippingAddress(models.Model):
    """Địa chỉ giao hàng của khách hàng"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    recipient_name = models.CharField(_("Tên người nhận"), max_length=100)
    phone = models.CharField(_("Số điện thoại"), max_length=20)
    address = models.TextField(_("Địa chỉ"))
    city = models.CharField(_("Thành phố"), max_length=100)
    district = models.CharField(_("Quận/Huyện"), max_length=100)
    ward = models.CharField(_("Phường/Xã"), max_length=100)
    is_default = models.BooleanField(_("Địa chỉ mặc định"), default=False)
    
    class Meta:
        verbose_name = _("Địa chỉ giao hàng")
        verbose_name_plural = _("Địa chỉ giao hàng")
    
    def __str__(self):
        return f"{self.recipient_name}, {self.address}, {self.district}, {self.city}" 