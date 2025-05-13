from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Dashboard chính 
    path('', views.sales_dashboard, name='sales_dashboard'),
    
    # Quản lý nhân viên
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='detail'),
    path('staff/add/', views.StaffCreateView.as_view(), name='create'),
    path('staff/<int:pk>/edit/', views.StaffUpdateView.as_view(), name='update'),
    path('staff/<int:staff_id>/schedule/add/', views.StaffScheduleCreateView.as_view(), name='add_schedule'),
    path('staff/<int:staff_id>/performance/add/', views.PerformanceCreateView.as_view(), name='add_performance'),
    
    # API hiệu suất
    path('api/performance/<int:staff_id>/', views.staff_performance_api, name='performance_api'),
    
    # Nhân viên bán hàng - modules
    path('orders/', views.sales_order_list, name='sales_order_list'),
    path('orders/<int:order_id>/', views.sales_order_detail, name='sales_order_detail'),
    path('orders/<int:order_id>/edit/', views.sales_order_update, name='sales_order_update'),
    path('orders/create/', views.sales_order_create, name='sales_order_create'),
    path('customers/', views.sales_customer_list, name='sales_customer_list'),
    path('customers/<int:customer_id>/', views.sales_customer_detail, name='sales_customer_detail'),
    path('products/', views.sales_product_list, name='sales_product_list'),
    path('products/<int:product_id>/', views.sales_product_detail, name='sales_product_detail'),
    path('reports/', views.sales_reports, name='sales_reports'),
    path('reports/daily/', views.sales_daily_report, name='sales_daily_report'),
    path('reports/monthly/', views.sales_monthly_report, name='sales_monthly_report'),
    path('profile/', views.sales_profile, name='sales_profile'),
    path('profile/edit/', views.sales_profile_update, name='sales_profile_update'),
] 