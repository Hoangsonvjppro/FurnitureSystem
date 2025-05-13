from django.urls import path
from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('checkout/', views.create_order_from_cart, name='checkout'),
    path('<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
    path('<int:order_id>/payment/add/', views.PaymentCreateView.as_view(), name='add_payment'),
    path('<int:order_id>/delivery/update/', views.DeliveryUpdateView.as_view(), name='update_delivery'),
    path('<int:pk>/invoice/', views.generate_invoice_pdf, name='generate_invoice'),
]