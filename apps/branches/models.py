from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Branch(models.Model):
    """Chi nhánh cửa hàng"""
    name = models.CharField(_("Tên chi nhánh"), max_length=100)
    address = models.TextField(_("Địa chỉ"))
    phone = models.CharField(_("Số điện thoại"), max_length=20)
    email = models.EmailField(_("Email"), blank=True)
    manager = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_branches',
        verbose_name=_("Quản lý")
    )
    opening_hours = models.CharField(_("Giờ mở cửa"), max_length=100, blank=True)
    is_active = models.BooleanField(_("Đang hoạt động"), default=True)
    created_at = models.DateTimeField(_("Ngày tạo"), default=timezone.now)
    description = models.TextField(_("Mô tả"), blank=True)
    
    class Meta:
        verbose_name = _("Chi nhánh")
        verbose_name_plural = _("Chi nhánh")
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def staff_count(self):
        """Số lượng nhân viên trong chi nhánh"""
        return self.staff.count()
    
    @property
    def active_orders_count(self):
        """Số đơn hàng đang xử lý tại chi nhánh"""
        return self.orders.exclude(status__in=['delivered', 'cancelled']).count() 


class BranchStaff(models.Model):
    """Nhân viên làm việc tại chi nhánh"""
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='staff_members',
        verbose_name=_("Chi nhánh")
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='branch_assignments',
        verbose_name=_("Nhân viên")
    )
    position = models.CharField(_("Vị trí"), max_length=100, blank=True)
    assigned_date = models.DateField(_("Ngày bắt đầu"), default=timezone.now)
    is_active = models.BooleanField(_("Đang làm việc"), default=True)
    
    class Meta:
        verbose_name = _("Nhân viên chi nhánh")
        verbose_name_plural = _("Nhân viên chi nhánh")
        unique_together = ('branch', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.branch.name}" 