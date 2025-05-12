from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.branches.models import Branch


class Report(models.Model):
    REPORT_TYPES = (
        ('sales', 'Báo cáo doanh số'),
        ('inventory', 'Báo cáo tồn kho'),
        ('finance', 'Báo cáo tài chính'),
        ('customer', 'Báo cáo khách hàng'),
        ('supplier', 'Báo cáo nhà cung cấp'),
    )
    
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="Loại báo cáo")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    parameters = models.JSONField(default=dict, verbose_name="Tham số báo cáo")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Người tạo")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Lần chạy cuối")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Chi nhánh")
    
    class Meta:
        verbose_name = "Báo cáo"
        verbose_name_plural = "Báo cáo"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ScheduledReport(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', 'Hàng ngày'),
        ('weekly', 'Hàng tuần'),
        ('monthly', 'Hàng tháng'),
        ('quarterly', 'Hàng quý'),
    )
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name="Báo cáo")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name="Tần suất")
    recipients = models.JSONField(default=list, verbose_name="Người nhận")
    active = models.BooleanField(default=True, verbose_name="Đang hoạt động")
    next_run = models.DateTimeField(verbose_name="Lần chạy tiếp theo")
    
    class Meta:
        verbose_name = "Báo cáo định kỳ"
        verbose_name_plural = "Báo cáo định kỳ"
    
    def __str__(self):
        return f"{self.report.title} - {self.get_frequency_display()}"


class ReportExecution(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Đang chờ'),
        ('running', 'Đang chạy'),
        ('completed', 'Hoàn thành'),
        ('failed', 'Thất bại'),
    )
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name="Báo cáo")
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Người thực hiện")
    executed_at = models.DateTimeField(default=timezone.now, verbose_name="Thời gian thực hiện")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Trạng thái")
    result_data = models.JSONField(null=True, blank=True, verbose_name="Dữ liệu kết quả")
    error_message = models.TextField(null=True, blank=True, verbose_name="Thông báo lỗi")
    
    class Meta:
        verbose_name = "Lần chạy báo cáo"
        verbose_name_plural = "Lần chạy báo cáo"
        ordering = ['-executed_at']
    
    def __str__(self):
        return f"{self.report.title} - {self.executed_at.strftime('%d/%m/%Y %H:%M')}" 