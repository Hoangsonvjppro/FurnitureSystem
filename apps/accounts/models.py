from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model với thông tin mở rộng"""
    phone_number = models.CharField(_("Số điện thoại"), max_length=15, blank=True)
    address = models.TextField(_("Địa chỉ"), blank=True)
    is_branch_manager = models.BooleanField(_("Quản lý chi nhánh"), default=False)
    is_sales_staff = models.BooleanField(_("Nhân viên bán hàng"), default=False)
    is_inventory_staff = models.BooleanField(_("Nhân viên kho"), default=False)
    branch = models.ForeignKey(
        'branches.Branch', 
        verbose_name=_("Chi nhánh"),
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='staff'
    )
    date_of_birth = models.DateField(_("Ngày sinh"), null=True, blank=True)
    avatar = models.ImageField(_("Ảnh đại diện"), upload_to='avatars/', null=True, blank=True)
    
    class Meta:
        verbose_name = _("Người dùng")
        verbose_name_plural = _("Người dùng")
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f"{self.last_name} {self.first_name}"
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def __str__(self):
        return self.get_full_name() or self.username


class CustomerProfile(models.Model):
    """Thông tin profile của khách hàng"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    tax_code = models.CharField(_("Mã số thuế"), max_length=20, blank=True)
    company_name = models.CharField(_("Tên công ty"), max_length=200, blank=True)
    shipping_addresses = models.ManyToManyField('ShippingAddress', blank=True, related_name='customers')
    points = models.PositiveIntegerField(_("Điểm tích lũy"), default=0)
    is_vip = models.BooleanField(_("Khách hàng VIP"), default=False)
    
    class Meta:
        verbose_name = _("Thông tin khách hàng")
        verbose_name_plural = _("Thông tin khách hàng")
    
    def __str__(self):
        return f"Hồ sơ của {self.user.get_full_name() or self.user.username}"


class ShippingAddress(models.Model):
    """Địa chỉ giao hàng của khách hàng"""
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