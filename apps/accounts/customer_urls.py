from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

app_name = 'customer'

urlpatterns = [
    # Customer profile dashboard
    path('', login_required(TemplateView.as_view(template_name='accounts/profile.html')), name='profile'),
    
    # Order history
    path('orders/', login_required(TemplateView.as_view(template_name='accounts/order_history.html')), name='order_history'),
    
    # Edit profile 
    path('edit/', login_required(TemplateView.as_view(template_name='accounts/edit_profile.html')), name='edit_profile'),
    
    # Address book
    path('addresses/', login_required(TemplateView.as_view(template_name='accounts/addresses.html')), name='addresses'),
    
    # Wishlist
    path('wishlist/', login_required(TemplateView.as_view(template_name='accounts/wishlist.html')), name='wishlist'),
] 