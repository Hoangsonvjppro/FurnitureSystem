from django.urls import path
from apps.inventory import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard URL
    path('', views.inventory_dashboard, name='dashboard'),
    
    # Stock URLs
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stock/<int:pk>/update/', views.StockUpdateView.as_view(), name='stock_update'),
    path('stock/low/', views.low_stock, name='low_stock'),
    
    # Stock Movement URLs
    path('movements/', views.StockMovementListView.as_view(), name='movement_list'),
    path('movements/create/', views.StockMovementCreateView.as_view(), name='movement_create'),
    
    # Stock In (Receiving) URLs
    path('stock-in/', views.receiving_list, name='receiving_list'),
    path('stock-in/add/', views.receiving_create, name='receiving_create'),
    path('stock-in/<int:receiving_id>/', views.receiving_detail, name='receiving_detail'),
    path('stock-in/<int:receiving_id>/edit/', views.receiving_update, name='receiving_update'),
    path('stock-in/<int:receiving_id>/complete/', views.receiving_complete, name='receiving_complete'),
    
    # Stock Out (Shipping) URLs
    path('stock-out/', views.shipping_list, name='shipping_list'),
    path('stock-out/add/', views.shipping_create, name='shipping_create'),
    path('stock-out/<int:shipping_id>/', views.shipping_detail, name='shipping_detail'),
    path('stock-out/<int:shipping_id>/edit/', views.shipping_update, name='shipping_update'),
    path('stock-out/<int:shipping_id>/complete/', views.shipping_complete, name='shipping_complete'),
    
    # Transfer URLs
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/add/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:transfer_id>/', views.transfer_detail, name='transfer_detail'),
    path('transfers/<int:transfer_id>/edit/', views.transfer_update, name='transfer_update'),
    path('transfers/<int:transfer_id>/complete/', views.transfer_complete, name='transfer_complete'),
    
    # Inventory URLs
    path('inventories/', views.InventoryListView.as_view(), name='inventory_list'),
    path('inventories/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventories/create/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('inventories/<int:inventory_id>/items/<int:item_id>/update/', 
         views.update_inventory_item, name='update_inventory_item'),
    path('inventories/<int:pk>/complete/', views.complete_inventory, name='complete_inventory'),
    
    # Reports URLs
    path('reports/', views.inventory_reports, name='reports'),
    path('reports/movements/', views.movement_report, name='movement_report'),
    path('reports/turnover/', views.turnover_report, name='turnover_report'),
    
    # Audit URLs
    path('audit/', views.inventory_audit, name='audit_list'),
    path('audit/create/', views.audit_create, name='audit_create'),
    path('audit/<int:audit_id>/', views.audit_detail, name='audit_detail'),
    path('audit/<int:audit_id>/edit/', views.audit_update, name='audit_update'),
    path('audit/<int:audit_id>/complete/', views.audit_complete, name='audit_complete'),
    
    # Staff profile
    path('profile/', views.staff_profile, name='staff_profile'),
] 