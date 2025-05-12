from django.urls import path
from apps.suppliers import views

app_name = 'suppliers'

urlpatterns = [
    # Supplier URLs
    path('', views.SupplierListView.as_view(), name='supplier_list'),
    path('create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    
    # Purchase Order URLs
    path('purchase-orders/', views.PurchaseOrderListView.as_view(), name='purchase_order_list'),
    path('purchase-orders/create/', views.PurchaseOrderCreateView.as_view(), name='purchase_order_create'),
    path('purchase-orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='purchase_order_detail'),
    path('purchase-orders/<int:pk>/update/', views.PurchaseOrderUpdateView.as_view(), name='purchase_order_update'),
    path('purchase-orders/<int:pk>/status-update/', views.update_purchase_order_status, name='purchase_order_status_update'),
] 