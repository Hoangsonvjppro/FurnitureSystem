from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages
from django.utils import timezone


class RoleBasedAccessMiddleware:
    """
    Middleware kiểm tra quyền truy cập dựa trên vai trò của người dùng
    và điều hướng họ đến dashboard thích hợp.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Danh sách các URL path không cần kiểm tra quyền
        self.public_paths = [
            '/products/', 
            '/cart/', 
            '/accounts/', 
            '/profile/',
            '/static/', 
            '/media/',
            '/__debug__/',
        ]
        
        # Ánh xạ vai trò -> prefix URL
        self.role_url_map = {
            'sales_staff': '/sales/',
            'inventory_staff': '/inventory/',
            'branch_manager': '/branch-manager/',
            'admin': '/admin/',
        }
        
    def __call__(self, request):
        path = request.path
        
        # Bỏ qua kiểm tra nếu là đường dẫn công khai
        if any(path.startswith(public_path) for public_path in self.public_paths):
            return self.get_response(request)
        
        # Nếu người dùng đã đăng nhập, kiểm tra quyền truy cập
        if request.user.is_authenticated:
            # Cập nhật thời gian truy cập dashboard cuối nếu người dùng truy cập dashboard
            self.update_last_dashboard_visit(request)
            
            # Kiểm tra quyền truy cập dựa trên vai trò
            if not self.has_access_permission(request.user, path):
                messages.warning(request, 'Bạn không có quyền truy cập vào trang này.')
                return redirect(request.user.get_dashboard_url())
            
            # Nếu nhân viên bắt buộc phải đổi mật khẩu
            if self.should_change_password(request.user, path):
                messages.warning(request, 'Vui lòng đổi mật khẩu trước khi tiếp tục.')
                return redirect('account_change_password')
        
        return self.get_response(request)
    
    def update_last_dashboard_visit(self, request):
        """Cập nhật thời gian truy cập dashboard cuối cho nhân viên"""
        user = request.user
        path = request.path
        
        if user.is_staff_member and any(path.startswith(prefix) for prefix in self.role_url_map.values()):
            user.last_dashboard_visit = timezone.now()
            user.save(update_fields=['last_dashboard_visit'])
    
    def has_access_permission(self, user, path):
        """Kiểm tra xem người dùng có quyền truy cập đường dẫn cụ thể không"""
        # Admin có quyền truy cập mọi nơi
        if user.is_superuser:
            return True
            
        # Kiểm tra quyền dựa trên vai trò và đường dẫn
        if path.startswith('/admin/') and not (user.is_superuser or user.is_staff):
            return False
            
        if path.startswith('/sales/') and not user.is_sales_staff:
            return False
            
        if path.startswith('/inventory/') and not user.is_inventory_staff:
            return False
            
        if path.startswith('/branch-manager/') and not user.is_branch_manager:
            return False
        
        return True
    
    def should_change_password(self, user, path):
        """Kiểm tra xem người dùng có bắt buộc đổi mật khẩu không"""
        change_password_paths = [
            '/accounts/password/change/',
            '/accounts/logout/'
        ]
        
        # Nếu truy cập trang đổi mật khẩu, cho phép truy cập
        if any(path.startswith(p) for p in change_password_paths):
            return False
            
        # Nhân viên bắt buộc đổi mật khẩu
        return user.is_staff_member and user.require_password_change


class CustomerAccessMiddleware:
    """
    Middleware đảm bảo khách hàng không truy cập vào các khu vực dành cho nhân viên.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Các URL dành riêng cho nhân viên
        self.staff_only_paths = [
            '/admin/',
            '/sales/',
            '/inventory/',
            '/branch-manager/',
        ]
        
    def __call__(self, request):
        path = request.path
        
        # Kiểm tra nếu khách hàng đang cố truy cập vào các khu vực nhân viên
        if request.user.is_authenticated and request.user.is_customer:
            if any(path.startswith(staff_path) for staff_path in self.staff_only_paths):
                messages.warning(request, 'Khu vực chỉ dành cho nhân viên.')
                return redirect('products:product_list')
        
        return self.get_response(request)


class RoleBasedRedirectMiddleware:
    """
    Middleware để chuyển hướng người dùng dựa trên vai trò của họ
    sau khi đăng nhập hoặc khi truy cập trang chủ
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Nếu người dùng đã đăng nhập và đang truy cập trang chủ or products
        if request.user.is_authenticated and request.path in ['/', '/products/']:
            # Kiểm tra vai trò người dùng và chuyển hướng phù hợp
            if request.user.is_superuser or request.user.is_staff:
                return redirect('/admin-panel/')
            elif request.user.is_branch_manager:
                return redirect('/branch-manager/')
            elif request.user.is_sales_staff:
                return redirect('/sales/')
            elif request.user.is_inventory_staff:
                return redirect('/inventory/')
            # Nếu là khách hàng thường, không cần chuyển hướng

        response = self.get_response(request)
        return response 