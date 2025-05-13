from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from django.http import HttpResponse

def sales_staff_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho nhân viên bán hàng"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Kiểm tra role trong database
            if request.user.role == 'SALES_STAFF' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                # Thông báo lỗi chi tiết
                error_msg = f"Bạn không có quyền truy cập khu vực này. Vai trò: {request.user.role}"
                messages.error(request, error_msg)
                
                # Chuyển hướng dựa trên vai trò
                if request.user.role == 'MANAGER':
                    return redirect('/branch-manager/')
                elif request.user.role == 'INVENTORY_STAFF':
                    return redirect('/inventory/')
                elif request.user.is_staff or request.user.is_superuser:
                    return redirect('/admin-panel/')
                else:
                    return redirect('products:home')
        else:
            return redirect('account_login')
    return _wrapped_view

def inventory_staff_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho nhân viên kho"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 'INVENTORY_STAFF' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                error_msg = f"Bạn không có quyền truy cập khu vực này. Vai trò: {request.user.role}"
                messages.error(request, error_msg)
                return redirect('products:home')
        else:
            return redirect('account_login')
    return _wrapped_view

def branch_manager_required(view_func):
    """Decorator để giới hạn quyền truy cập chỉ cho quản lý chi nhánh"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 'MANAGER' or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                error_msg = f"Bạn không có quyền truy cập khu vực này. Vai trò: {request.user.role}"
                messages.error(request, error_msg)
                return redirect('products:home')
        else:
            return redirect('account_login')
    return _wrapped_view 