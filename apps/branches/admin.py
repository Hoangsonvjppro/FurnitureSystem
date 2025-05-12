from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'manager', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address', 'phone')
    # autocomplete_fields = ('manager',)  # Tạm thời comment để tránh lỗi 