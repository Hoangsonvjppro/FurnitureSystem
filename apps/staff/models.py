from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.branches.models import Branch


class StaffProfile(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Quản lý'),
        ('sales', 'Nhân viên bán hàng'),
        ('warehouse', 'Nhân viên kho'),
        ('support', 'Nhân viên hỗ trợ'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', verbose_name="Người dùng")
    staff_id = models.CharField(max_length=20, unique=True, verbose_name="Mã nhân viên")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name="Vai trò")
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Chi nhánh")
    date_hired = models.DateField(default=timezone.now, verbose_name="Ngày vào làm")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name="Liên hệ khẩn cấp")
    profile_image = models.ImageField(upload_to='staff/profile/', blank=True, null=True, verbose_name="Ảnh đại diện")
    status = models.BooleanField(default=True, verbose_name="Hoạt động")
    
    class Meta:
        verbose_name = "Hồ sơ nhân viên"
        verbose_name_plural = "Hồ sơ nhân viên"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()}"
    
    @property
    def is_manager(self):
        return self.role == 'manager'
    
    @property
    def is_sales_staff(self):
        return self.role == 'sales'
    
    @property
    def is_warehouse_staff(self):
        return self.role == 'warehouse'


class StaffSchedule(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='schedules', verbose_name="Nhân viên")
    date = models.DateField(verbose_name="Ngày")
    start_time = models.TimeField(verbose_name="Giờ bắt đầu")
    end_time = models.TimeField(verbose_name="Giờ kết thúc")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    
    class Meta:
        verbose_name = "Lịch làm việc"
        verbose_name_plural = "Lịch làm việc"
        unique_together = ('staff', 'date', 'start_time')
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.date.strftime('%d/%m/%Y')}"


class Performance(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='performances', verbose_name="Nhân viên")
    period = models.CharField(max_length=7, verbose_name="Kỳ đánh giá")  # Format: MM/YYYY
    sales_target = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Mục tiêu doanh số")
    sales_achieved = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Doanh số đạt được")
    orders_processed = models.IntegerField(default=0, verbose_name="Đơn hàng đã xử lý")
    customer_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Đánh giá khách hàng")
    notes = models.TextField(blank=True, null=True, verbose_name="Nhận xét")
    
    class Meta:
        verbose_name = "Hiệu suất nhân viên"
        verbose_name_plural = "Hiệu suất nhân viên"
        unique_together = ('staff', 'period')
    
    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.period}"
    
    @property
    def achievement_percentage(self):
        if self.sales_target > 0:
            return (self.sales_achieved / self.sales_target) * 100
        return 0 