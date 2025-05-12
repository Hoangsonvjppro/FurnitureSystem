from django.contrib import admin
from .models import StaffProfile, StaffSchedule, Performance


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('staff_id', 'get_name', 'role', 'branch', 'phone', 'status')
    list_filter = ('role', 'branch', 'status', 'date_hired')
    search_fields = ('staff_id', 'user__first_name', 'user__last_name', 'user__email', 'phone')
    raw_id_fields = ('user', 'branch')
    
    def get_name(self, obj):
        return obj.user.get_full_name() if obj.user else ''
    get_name.short_description = 'Họ tên'
    get_name.admin_order_field = 'user__last_name'


@admin.register(StaffSchedule)
class StaffScheduleAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'start_time', 'end_time')
    list_filter = ('date', 'staff__branch')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'staff__staff_id')
    raw_id_fields = ('staff',)
    date_hierarchy = 'date'


@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'period', 'sales_target', 'sales_achieved', 'achievement_percentage', 'orders_processed')
    list_filter = ('period', 'staff__branch', 'staff__role')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'staff__staff_id')
    raw_id_fields = ('staff',)
    
    def achievement_percentage(self, obj):
        return f"{obj.achievement_percentage:.1f}%" if obj.achievement_percentage else "0.0%"
    achievement_percentage.short_description = '% Hoàn thành' 