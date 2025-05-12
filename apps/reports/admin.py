from django.contrib import admin
from .models import Report, ScheduledReport, ReportExecution


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'created_by', 'created_at', 'last_run')
    list_filter = ('report_type', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'last_run')
    fieldsets = (
        ('Thông tin báo cáo', {
            'fields': ('title', 'report_type', 'description', 'branch')
        }),
        ('Tham số', {
            'fields': ('parameters',),
        }),
        ('Thông tin khác', {
            'fields': ('created_by', 'created_at', 'last_run'),
        }),
    )


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ('report', 'frequency', 'active', 'next_run')
    list_filter = ('frequency', 'active')
    search_fields = ('report__title',)
    readonly_fields = ('next_run',)
    fieldsets = (
        ('Báo cáo', {
            'fields': ('report', 'frequency')
        }),
        ('Cấu hình', {
            'fields': ('recipients', 'active', 'next_run'),
        }),
    )


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    list_display = ('report', 'executed_by', 'executed_at', 'status')
    list_filter = ('status', 'executed_at')
    search_fields = ('report__title',)
    readonly_fields = ('executed_at',)
    fieldsets = (
        ('Báo cáo', {
            'fields': ('report', 'executed_by', 'executed_at')
        }),
        ('Kết quả', {
            'fields': ('status', 'result_data', 'error_message'),
        }),
    ) 