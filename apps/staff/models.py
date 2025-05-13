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


class EmployeeEvaluation(models.Model):
    RATING_CHOICES = (
        (1, 'Kém'),
        (2, 'Trung bình'),
        (3, 'Khá'),
        (4, 'Tốt'),
        (5, 'Xuất sắc'),
    )
    
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='evaluations', verbose_name="Nhân viên")
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations_given', verbose_name="Người đánh giá")
    evaluation_date = models.DateField(default=timezone.now, verbose_name="Ngày đánh giá")
    period = models.CharField(max_length=7, verbose_name="Kỳ đánh giá")  # Format: MM/YYYY
    
    # Các tiêu chí đánh giá
    work_quality = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Chất lượng công việc")
    work_quantity = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Số lượng công việc")
    punctuality = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Đúng giờ")
    initiative = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Sáng kiến")
    teamwork = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Làm việc nhóm")
    communication = models.PositiveSmallIntegerField(choices=RATING_CHOICES, verbose_name="Kỹ năng giao tiếp")
    
    strengths = models.TextField(blank=True, verbose_name="Điểm mạnh")
    areas_for_improvement = models.TextField(blank=True, verbose_name="Điểm cần cải thiện")
    goals_for_next_period = models.TextField(blank=True, verbose_name="Mục tiêu kỳ tới")
    additional_comments = models.TextField(blank=True, verbose_name="Nhận xét thêm")
    
    # Trạng thái phiếu đánh giá
    is_completed = models.BooleanField(default=False, verbose_name="Đã hoàn thành")
    is_acknowledged = models.BooleanField(default=False, verbose_name="Đã xác nhận")
    
    class Meta:
        verbose_name = "Đánh giá nhân viên"
        verbose_name_plural = "Đánh giá nhân viên"
        unique_together = ('staff', 'evaluator', 'evaluation_date')
    
    def __str__(self):
        return f"Đánh giá {self.staff.user.get_full_name()} - {self.period}"
    
    @property
    def overall_rating(self):
        """Tính điểm đánh giá trung bình"""
        total = (self.work_quality + self.work_quantity + self.punctuality + 
                self.initiative + self.teamwork + self.communication)
        return round(total / 6, 1)
    
    def get_overall_rating_display(self):
        """Hiển thị xếp loại dựa trên điểm trung bình"""
        rating = self.overall_rating
        if rating >= 4.5:
            return "Xuất sắc"
        elif rating >= 3.5:
            return "Tốt"
        elif rating >= 2.5:
            return "Khá"
        elif rating >= 1.5:
            return "Trung bình"
        else:
            return "Kém" 