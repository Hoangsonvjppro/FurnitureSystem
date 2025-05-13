from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Quản lý nhân viên (dành cho quản lý)
    path('', views.StaffListView.as_view(), name='list'),
    
    # Chi tiết nhân viên
    path('<int:pk>/', views.StaffDetailView.as_view(), name='detail'),
    
    # Thêm nhân viên mới
    path('add/', views.StaffCreateView.as_view(), name='create'),
    
    # Chỉnh sửa thông tin nhân viên
    path('<int:pk>/edit/', views.StaffUpdateView.as_view(), name='update'),
    
    # Thêm lịch làm việc cho nhân viên
    path('<int:staff_id>/schedule/add/', views.StaffScheduleCreateView.as_view(), name='add_schedule'),
    
    # Thêm hiệu suất cho nhân viên
    path('<int:staff_id>/performance/add/', views.PerformanceCreateView.as_view(), name='add_performance'),
    
    # API lấy dữ liệu hiệu suất
    path('api/performance/<int:staff_id>/', views.staff_performance_api, name='performance_api'),
    
    # Nhân viên bán hàng
    path('sales/', views.sales_dashboard, name='sales_dashboard'),
    path('sales/orders/', views.sales_order_list, name='sales_order_list'),
    path('sales/orders/<int:order_id>/', views.sales_order_detail, name='sales_order_detail'),
    path('sales/orders/<int:order_id>/edit/', views.sales_order_update, name='sales_order_update'),
    path('sales/orders/create/', views.sales_order_create, name='sales_order_create'),
    path('sales/customers/', views.sales_customer_list, name='sales_customer_list'),
    path('sales/customers/<int:customer_id>/', views.sales_customer_detail, name='sales_customer_detail'),
    path('sales/products/', views.sales_product_list, name='sales_product_list'),
    path('sales/products/<int:product_id>/', views.sales_product_detail, name='sales_product_detail'),
    path('sales/reports/', views.sales_reports, name='sales_reports'),
    path('sales/reports/daily/', views.sales_daily_report, name='sales_daily_report'),
    path('sales/reports/monthly/', views.sales_monthly_report, name='sales_monthly_report'),
    path('sales/profile/', views.sales_profile, name='sales_profile'),
    path('sales/profile/edit/', views.sales_profile_update, name='sales_profile_update'),
] 