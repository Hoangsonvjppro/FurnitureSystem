from django.urls import path
from . import views as staff_views

app_name = 'staff'

urlpatterns = [
    # Dashboard - trang chủ cho nhân viên bán hàng
    path('', staff_views.sales_dashboard, name='sales_dashboard'),
    
    # Quản lý đơn hàng
    path('orders/', staff_views.sales_order_list, name='sales_orders'),
    path('orders/<int:order_id>/', staff_views.sales_order_detail, name='sales_order_detail'),
    path('orders/create/', staff_views.sales_order_create, name='sales_order_create'),
    path('orders/<int:order_id>/update/', staff_views.sales_order_update, name='sales_order_update'),
    
    # Quản lý khách hàng
    path('customers/', staff_views.sales_customer_list, name='sales_customers'),
    path('customers/<int:customer_id>/', staff_views.sales_customer_detail, name='sales_customer_detail'),
    path('customers/create/', staff_views.sales_customer_create, name='sales_customer_create'),
    path('customers/<int:customer_id>/update/', staff_views.sales_customer_update, name='sales_customer_update'),
    
    # Danh mục sản phẩm
    path('products/', staff_views.sales_product_list, name='sales_products'),
    path('products/<int:product_id>/', staff_views.sales_product_detail, name='sales_product_detail'),
    
    # Báo cáo
    path('reports/', staff_views.sales_reports, name='sales_reports'),
    path('reports/daily/', staff_views.sales_daily_report, name='sales_daily_report'),
    path('reports/monthly/', staff_views.sales_monthly_report, name='sales_monthly_report'),
    
    # Hồ sơ cá nhân
    path('profile/', staff_views.sales_profile, name='sales_profile'),
    path('profile/update/', staff_views.sales_profile_update, name='sales_profile_update'),
] 