from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/permissions/', views.user_permissions, name='user_permissions'),
    
    # System configuration
    path('configuration/', views.system_configuration, name='system_configuration'),
    
    # Categories & attributes
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('attributes/', views.attribute_list, name='attribute_list'),
    path('attributes/create/', views.attribute_create, name='attribute_create'),
    path('attributes/<int:pk>/edit/', views.attribute_edit, name='attribute_edit'),
    
    # Reports
    path('reports/', views.report_dashboard, name='report_dashboard'),
    path('reports/sales/', views.sales_report, name='sales_report'),
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/branches/', views.branch_report, name='branch_report'),
    path('reports/customers/', views.customer_report, name='customer_report'),
    path('reports/export/<str:report_type>/', views.export_report, name='export_report'),
    
    # Suppliers
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/<int:pk>/edit/', views.supplier_edit, name='supplier_edit'),
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    
    # Data management
    path('backup/', views.backup_data, name='backup_data'),
    path('restore/', views.restore_data, name='restore_data'),
] 