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
    # Admin dashboard (Django default admin)
    path('django-admin/', admin.site.urls),
    
    # Custom admin panel - chuyến hướng tất cả /admin/ tới admin-panel
    path('admin-panel/', include('apps.admin_panel.urls')),
    path('admin/', RedirectView.as_view(url='/admin-panel/', permanent=True)),
    
    # Khu vực dành cho khách hàng 
    path('', RedirectView.as_view(url='/products/', permanent=True), name='home'),
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('accounts/', include('allauth.urls')),
    path('profile/', include('apps.accounts.customer_urls')),
    
    # Khu vực dành cho nhân viên bán hàng
    path('sales/', include('apps.staff.urls')),
    
    # Khu vực dành cho nhân viên kho
    path('inventory/', include('apps.inventory.staff_urls')),
    
    # Khu vực dành cho quản lý cửa hàng
    path('branch-manager/', include('apps.branches.manager_urls')),
    
    # Báo cáo
    path('reports/', include('apps.reports.urls')),
    
    # API endpoints
    path('api/', include('apps.api.urls')),
    
    # Debug toolbar
    path('__debug__/', include('debug_toolbar.urls')),
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
