from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.urls import path
from django.template.loader import get_template
from .models import StaffProfile, StaffSchedule, Performance, EmployeeEvaluation


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


@admin.register(EmployeeEvaluation)
class EmployeeEvaluationAdmin(admin.ModelAdmin):
    list_display = ('staff', 'period', 'evaluation_date', 'evaluator', 'display_overall_rating', 'is_completed', 'export_pdf_link')
    list_filter = ('evaluation_date', 'period', 'is_completed', 'is_acknowledged')
    search_fields = ('staff__user__first_name', 'staff__user__last_name', 'staff__staff_id', 'evaluator__username')
    raw_id_fields = ('staff', 'evaluator')
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('staff', 'evaluator', 'evaluation_date', 'period')
        }),
        ('Đánh giá', {
            'fields': ('work_quality', 'work_quantity', 'punctuality', 'initiative', 'teamwork', 'communication')
        }),
        ('Nhận xét', {
            'fields': ('strengths', 'areas_for_improvement', 'goals_for_next_period', 'additional_comments')
        }),
        ('Trạng thái', {
            'fields': ('is_completed', 'is_acknowledged')
        }),
    )
    
    def display_overall_rating(self, obj):
        rating = obj.overall_rating
        if rating >= 4:
            color = 'green'
        elif rating >= 3:
            color = 'blue'
        elif rating >= 2:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{} - {}</span>', 
                          color, rating, obj.get_overall_rating_display())
    display_overall_rating.short_description = 'Đánh giá tổng quát'
    
    def export_pdf_link(self, obj):
        if obj.is_completed:
            return format_html('<a class="button" href="{}">Xuất PDF</a>', 
                             f'/admin/staff/employeeevaluation/{obj.id}/export-pdf/')
        return "Chưa hoàn thành"
    export_pdf_link.short_description = 'Xuất phiếu đánh giá'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:evaluation_id>/export-pdf/', self.export_evaluation_pdf, name='export_evaluation_pdf'),
        ]
        return custom_urls + urls
    
    def export_evaluation_pdf(self, request, evaluation_id):
        try:
            # Import xhtml2pdf chỉ khi cần sử dụng
            from xhtml2pdf import pisa
            
            evaluation = EmployeeEvaluation.objects.get(id=evaluation_id)
            template = get_template('staff/evaluation_pdf.html')
            context = {'evaluation': evaluation}
            html = template.render(context)
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="evaluation_{evaluation.staff.staff_id}_{evaluation.period}.pdf"'
            
            # Tạo PDF
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('Có lỗi khi tạo file PDF: %s' % pisa_status.err)
            return response
        except ImportError:
            return HttpResponse('Không thể tạo file PDF. Thư viện xhtml2pdf không khả dụng.', content_type='text/plain') 