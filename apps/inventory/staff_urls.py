from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='dashboard'),
    
    # Quản lý tồn kho
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    path('stock/<int:stock_id>/update/', views.stock_update, name='stock_update'),
    path('stock/low/', views.low_stock, name='low_stock'),
    
    # Quản lý nhập kho
    path('receiving/', views.receiving_list, name='receiving_list'),
    path('receiving/create/', views.receiving_create, name='receiving_create'),
    path('receiving/<int:receiving_id>/', views.receiving_detail, name='receiving_detail'),
    path('receiving/<int:receiving_id>/update/', views.receiving_update, name='receiving_update'),
    path('receiving/<int:receiving_id>/complete/', views.receiving_complete, name='receiving_complete'),
    
    # Quản lý xuất kho
    path('shipping/', views.shipping_list, name='shipping_list'),
    path('shipping/create/', views.shipping_create, name='shipping_create'),
    path('shipping/<int:shipping_id>/', views.shipping_detail, name='shipping_detail'),
    path('shipping/<int:shipping_id>/update/', views.shipping_update, name='shipping_update'),
    path('shipping/<int:shipping_id>/complete/', views.shipping_complete, name='shipping_complete'),
    
    # Quản lý chuyển kho
    path('transfer/', views.transfer_list, name='transfer_list'),
    path('transfer/create/', views.transfer_create, name='transfer_create'),
    path('transfer/<int:transfer_id>/', views.transfer_detail, name='transfer_detail'),
    path('transfer/<int:transfer_id>/update/', views.transfer_update, name='transfer_update'),
    path('transfer/<int:transfer_id>/complete/', views.transfer_complete, name='transfer_complete'),
    
    # Kiểm kê hàng tồn
    path('audit/', views.inventory_audit, name='inventory_audit'),
    path('audit/create/', views.audit_create, name='audit_create'),
    path('audit/<int:audit_id>/', views.audit_detail, name='audit_detail'),
    path('audit/<int:audit_id>/update/', views.audit_update, name='audit_update'),
    path('audit/<int:audit_id>/complete/', views.audit_complete, name='audit_complete'),
    
    # Báo cáo
    path('reports/', views.inventory_reports, name='inventory_reports'),
    path('reports/movement/', views.movement_report, name='movement_report'),
    path('reports/turnover/', views.turnover_report, name='turnover_report'),
    
    # Cá nhân
    path('profile/', views.staff_profile, name='staff_profile'),
] 