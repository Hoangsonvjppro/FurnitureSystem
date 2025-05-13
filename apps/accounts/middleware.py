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
            '/debug-user-roles/',  # Add our debug endpoint
        ]
        
        # Ánh xạ vai trò -> prefix URL
        self.role_url_map = {
            'SALES_STAFF': '/sales/',
            'INVENTORY_STAFF': '/inventory/',
            'MANAGER': '/branch-manager/',
            'ADMIN': '/admin/',
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
                messages.warning(
                    request, 
                    f'Bạn không có quyền truy cập vào trang này. Vai trò: {request.user.role}'
                )
                # Redirect to appropriate dashboard based on role
                return redirect(request.user.get_dashboard_url())
        
        return self.get_response(request)
    
    def update_last_dashboard_visit(self, request):
        """Cập nhật thời gian truy cập dashboard cuối cho nhân viên"""
        user = request.user
        path = request.path
        
        if user.role != 'CUSTOMER' and any(path.startswith(prefix) for prefix in self.role_url_map.values()):
            # Nếu có thuộc tính last_dashboard_visit
            if hasattr(user, 'last_dashboard_visit'):
                user.last_dashboard_visit = timezone.now()
                user.save(update_fields=['last_dashboard_visit'])
    
    def has_access_permission(self, user, path):
        """Kiểm tra xem người dùng có quyền truy cập đường dẫn cụ thể không"""
        # Admin có quyền truy cập mọi nơi
        if user.is_superuser or user.role == 'ADMIN':
            return True
            
        # Kiểm tra quyền dựa trên vai trò và đường dẫn
        if path.startswith('/admin/') and not (user.is_superuser or user.is_staff):
            return False
            
        if path.startswith('/sales/') and user.role != 'SALES_STAFF':
            return False
            
        if path.startswith('/inventory/') and user.role != 'INVENTORY_STAFF':
            return False
            
        if path.startswith('/branch-manager/') and user.role != 'MANAGER':
            return False
        
        return True


class CustomerAccessMiddleware:
    """
    Middleware đảm bảo khách hàng không truy cập vào các khu vực dành cho nhân viên.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Các URL dành riêng cho nhân viên
        self.staff_only_paths = [
            '/admin/',
            '/inventory/',
            '/branch-manager/',
            '/sales/',
        ]
        
    def __call__(self, request):
        path = request.path
        
        # Kiểm tra nếu khách hàng đang cố truy cập vào các khu vực nhân viên
        if request.user.is_authenticated and request.user.role == 'CUSTOMER':
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
            if request.user.is_superuser or request.user.role == 'ADMIN':
                return redirect('/admin-panel/')
            elif request.user.role == 'MANAGER':
                return redirect('/branch-manager/')
            elif request.user.role == 'SALES_STAFF':
                return redirect('/sales/')
            elif request.user.role == 'INVENTORY_STAFF':
                return redirect('/inventory/')
            # Nếu là khách hàng thường, không cần chuyển hướng

        response = self.get_response(request)
        return response 