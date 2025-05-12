from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard báo cáo
    path('', views.ReportDashboardView.as_view(), name='dashboard'),
    
    # API lấy dữ liệu cho báo cáo
    path('api/data/<str:report_type>/', views.report_data_api, name='api_data'),
    
    # Xuất báo cáo
    path('export/<str:report_type>/', views.export_report, name='export'),
] 