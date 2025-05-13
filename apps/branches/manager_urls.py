from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    # Dashboard
    path('', views.manager_dashboard, name='manager_dashboard'),
    
    # Quản lý doanh số
    path('sales/', views.manager_sales, name='manager_sales'),
    path('sales/daily/', views.manager_daily_sales, name='manager_daily_sales'),
    path('sales/monthly/', views.manager_monthly_sales, name='manager_monthly_sales'),
    path('sales/yearly/', views.manager_yearly_sales, name='manager_yearly_sales'),
    
    # Quản lý kho hàng
    path('inventory/', views.manager_inventory, name='manager_inventory'),
    path('inventory/low-stock/', views.manager_low_stock, name='manager_low_stock'),
    path('inventory/valuation/', views.manager_inventory_valuation, name='manager_inventory_valuation'),
    
    # Quản lý đơn hàng
    path('orders/', views.manager_orders, name='manager_orders'),
    path('orders/<int:order_id>/', views.manager_order_detail, name='manager_order_detail'),
    path('orders/pending/', views.manager_pending_orders, name='manager_pending_orders'),
    path('orders/completed/', views.manager_completed_orders, name='manager_completed_orders'),
    path('orders/cancelled/', views.manager_cancelled_orders, name='manager_cancelled_orders'),
    
    # Quản lý nhân viên
    path('staff/', views.manager_staff, name='manager_staff'),
    path('staff/<int:staff_id>/', views.manager_staff_detail, name='manager_staff_detail'),
    path('staff/create/', views.manager_staff_create, name='manager_staff_create'),
    path('staff/<int:staff_id>/update/', views.manager_staff_update, name='manager_staff_update'),
    path('staff/performance/', views.manager_staff_performance, name='manager_staff_performance'),
    path('staff/schedule/', views.manager_staff_schedule, name='manager_staff_schedule'),
    
    # Quản lý khách hàng
    path('customers/', views.manager_customers, name='manager_customers'),
    path('customers/<int:customer_id>/', views.manager_customer_detail, name='manager_customer_detail'),
    path('customers/vip/', views.manager_vip_customers, name='manager_vip_customers'),
    
    # Báo cáo
    path('reports/', views.manager_reports, name='manager_reports'),
    path('reports/sales/', views.manager_sales_report, name='manager_sales_report'),
    path('reports/inventory/', views.manager_inventory_report, name='manager_inventory_report'),
    path('reports/staff/', views.manager_staff_report, name='manager_staff_report'),
    path('reports/customers/', views.manager_customer_report, name='manager_customer_report'),
    path('reports/export-pdf/<str:report_type>/', views.manager_export_report_pdf, name='manager_export_report_pdf'),
    
    # Cài đặt chi nhánh
    path('settings/', views.manager_settings, name='manager_settings'),
    path('settings/branch/', views.manager_branch_settings, name='manager_branch_settings'),
    path('settings/targets/', views.manager_targets_settings, name='manager_targets_settings'),
] 