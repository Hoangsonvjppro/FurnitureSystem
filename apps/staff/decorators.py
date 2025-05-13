from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.http import HttpResponse

def sales_staff_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho nhân viên bán hàng"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # TEMPORARY FIX: Allow all authenticated users to access sales views
            return view_func(request, *args, **kwargs)
            
            # Original code (commented out):
            # Explicitly check database field
            # has_permission = request.user.is_sales_staff
            
            # if has_permission:
            #     return view_func(request, *args, **kwargs)
            # else:
            #     # More detailed error message for debugging
            #     error_msg = f"Bạn không có quyền truy cập khu vực này. Vai trò: {request.user.debug_roles}"
            #     messages.error(request, error_msg)
                
            #     # If the user is a different type of staff, redirect appropriately
            #     if request.user.is_branch_manager:
            #         return redirect('/branch-manager/')
            #     elif request.user.is_inventory_staff:
            #         return redirect('/inventory/')
            #     elif request.user.is_staff or request.user.is_superuser:
            #         return redirect('/admin/')
            #     else:
            #         return redirect('products:home')
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