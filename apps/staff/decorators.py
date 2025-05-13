from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def sales_staff_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho nhân viên bán hàng"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_sales_staff:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Bạn không có quyền truy cập khu vực này")
                return redirect('products:home')
        else:
            return redirect('account_login')
    return _wrapped_view

def inventory_staff_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho nhân viên kho"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_inventory_staff:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Bạn không có quyền truy cập khu vực này")
                return redirect('products:home')
        else:
            return redirect('account_login')
    return _wrapped_view

def branch_manager_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho quản lý chi nhánh"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_branch_manager:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Bạn không có quyền truy cập khu vực này")
                return redirect('products:home')
        else:
            return redirect('account_login')
    return _wrapped_view 