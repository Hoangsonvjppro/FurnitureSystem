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
    
    # Mức độ xác thực: 0=cơ bản, 1=email, 2=2FA
    authentication_level = models.PositiveSmallIntegerField(_("Mức độ xác thực"), default=0)
    
    # Thiết lập cho nhân viên
    require_password_change = models.BooleanField(_("Yêu cầu đổi mật khẩu"), default=False)
    last_dashboard_visit = models.DateTimeField(_("Lần truy cập dashboard cuối"), null=True, blank=True)
    
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
    
    @property
    def is_customer(self):
        """Kiểm tra user có phải là khách hàng thông thường hay không"""
        return not (self.is_staff or self.is_branch_manager or self.is_sales_staff or self.is_inventory_staff)
    
    @property
    def is_staff_member(self):
        """Kiểm tra user có phải là nhân viên bất kỳ hay không"""
        return self.is_branch_manager or self.is_sales_staff or self.is_inventory_staff or self.is_staff
    
    @property
    def role_name(self):
        """Trả về tên role của user để hiển thị"""
        if self.is_superuser:
            return _("Quản trị viên")
        if self.is_branch_manager:
            return _("Quản lý chi nhánh")
        if self.is_sales_staff:
            return _("Nhân viên bán hàng")
        if self.is_inventory_staff:
            return _("Nhân viên kho")
        if self.is_staff:
            return _("Nhân viên hệ thống")
        return _("Khách hàng")
    
    @property
    def debug_roles(self):
        """Hiển thị thông tin về các role của user để debug"""
        return {
            'username': self.username,
            'is_superuser': self.is_superuser,
            'is_staff': self.is_staff,
            'is_branch_manager': self.is_branch_manager,
            'is_sales_staff': self.is_sales_staff,
            'is_inventory_staff': self.is_inventory_staff,
        }
    
    def get_dashboard_url(self):
        """Trả về URL dashboard tương ứng với vai trò của user"""
        if self.is_superuser or self.is_staff:
            return '/admin/'
        if self.is_branch_manager:
            return '/branch-manager/'
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