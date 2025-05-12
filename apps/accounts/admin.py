from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, CustomerProfile, ShippingAddress


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_branch_manager')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_branch_manager', 'is_sales_staff', 'is_inventory_staff', 'branch')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'date_of_birth', 'avatar')}),
        (_('Work info'), {'fields': ('branch', 'is_branch_manager', 'is_sales_staff', 'is_inventory_staff')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'points', 'is_vip')
    list_filter = ('is_vip',)
    search_fields = ('user__username', 'user__email', 'company_name', 'tax_code')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('recipient_name', 'phone', 'address', 'city', 'district', 'is_default')
    list_filter = ('is_default', 'city')
    search_fields = ('recipient_name', 'phone', 'address', 'city', 'district') 