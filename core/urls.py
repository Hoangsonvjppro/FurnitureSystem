"""
FurnitureSystem URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import views as auth_views
from django.db import OperationalError

# Fix admin login issues
admin.autodiscover()
admin.site.login = auth_views.LoginView.as_view(template_name='account/admin_login.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('allauth.urls')),
    
    # API
    path('api/', include('apps.api.urls')),
    
    # App URLs
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('inventory/', include('apps.inventory.urls')),
    path('suppliers/', include('apps.suppliers.urls')),
    path('branches/', include('apps.branches.urls')),
    path('reports/', include('apps.reports.urls')),
    path('staff/', include('apps.staff.urls')),
    
    # Home page - Redirect to products list
    path('', RedirectView.as_view(pattern_name='products:product_list'), name='home'),
]

# Debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
