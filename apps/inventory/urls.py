from django.urls import path
from apps.inventory import views

app_name = 'inventory'

urlpatterns = [
    # Stock URLs
    path('stock/', views.StockListView.as_view(), name='stock_list'),
    path('stock/<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    path('stock/<int:pk>/update/', views.StockUpdateView.as_view(), name='stock_update'),
    
    # Stock Movement URLs
    path('movements/', views.StockMovementListView.as_view(), name='movement_list'),
    path('movements/create/', views.StockMovementCreateView.as_view(), name='movement_create'),
    
    # Inventory URLs
    path('inventories/', views.InventoryListView.as_view(), name='inventory_list'),
    path('inventories/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('inventories/create/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('inventories/<int:inventory_id>/items/<int:item_id>/update/', 
         views.update_inventory_item, name='update_inventory_item'),
    path('inventories/<int:pk>/complete/', views.complete_inventory, name='complete_inventory'),
] 