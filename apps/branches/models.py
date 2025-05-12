from django.db import models


class Branch(models.Model):
    name = models.CharField("Tên chi nhánh", max_length=100)
    address = models.TextField("Địa chỉ")
    phone = models.CharField("Số điện thoại", max_length=20)
    email = models.EmailField("Email", blank=True)
    manager = models.OneToOneField(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_branch',
        verbose_name="Quản lý chi nhánh"
    )
    is_active = models.BooleanField("Kích hoạt", default=True)
    opening_date = models.DateField("Ngày khai trương", null=True, blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)
    
    class Meta:
        verbose_name = "Chi nhánh"
        verbose_name_plural = "Chi nhánh"
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