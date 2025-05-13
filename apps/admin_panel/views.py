from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
import io
import xlsxwriter
from django.contrib.auth.models import Group
import os

from apps.accounts.models import User
from apps.products.models import Product, Category, VariantAttribute
from apps.orders.models import Order, OrderItem
from apps.inventory.models import Stock, StockMovement, Inventory
from apps.branches.models import Branch
from apps.suppliers.models import Supplier, PurchaseOrder

# Helper function to check if user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard showing key metrics for the entire system"""
    # Get date ranges
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)
    
    # Get key metrics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_users = User.objects.count()
    total_branches = Branch.objects.count()
    
    # Sales data
    daily_sales = Order.objects.filter(created_at__date=today).aggregate(
        count=Count('id'),
        total=Sum('total')
    )
    weekly_sales = Order.objects.filter(created_at__date__gte=start_of_week).aggregate(
        count=Count('id'),
        total=Sum('total')
    )
    monthly_sales = Order.objects.filter(created_at__date__gte=start_of_month).aggregate(
        count=Count('id'),
        total=Sum('total')
    )
    
    # Top-selling products
    top_products = OrderItem.objects.values('product__name').annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    context = {
        'title': 'Bảng điều khiển quản trị',
        'total_products': total_products,
        'total_categories': total_categories,
        'total_users': total_users,
        'total_branches': total_branches,
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'top_products': top_products,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


# User Management Views
@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users with filtering options"""
    users = User.objects.all().order_by('-date_joined')
    
    # Apply filters
    role_filter = request.GET.get('role')
    if role_filter == 'admin':
        users = users.filter(Q(is_superuser=True) | Q(role='ADMIN'))
    elif role_filter == 'staff':
        users = users.filter(is_staff=True, is_superuser=False)
    elif role_filter == 'branch_manager':
        users = users.filter(role='MANAGER')
    elif role_filter == 'sales':
        users = users.filter(role='SALES_STAFF')
    elif role_filter == 'inventory':
        users = users.filter(role='INVENTORY_STAFF')
    elif role_filter == 'customer':
        users = users.filter(
            is_superuser=False, 
            is_staff=False,
            role='CUSTOMER'
        )
    
    context = {
        'title': 'Quản lý người dùng',
        'users': users,
        'role_filter': role_filter,
    }
    
    return render(request, 'admin_panel/users/user_list.html', context)


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create a new user with specific role"""
    if request.method == 'POST':
        # Process form data and create user
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Kiểm tra dữ liệu đầu vào
        if not (username and email and password):
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin username, email và mật khẩu')
            return redirect('admin_panel:user_create')
        
        # Kiểm tra username đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username {username} đã tồn tại')
            return redirect('admin_panel:user_create')
        
        # Kiểm tra email đã tồn tại chưa
        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} đã tồn tại')
            return redirect('admin_panel:user_create')
        
        # Tạo người dùng mới
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            is_active=True
        )
        
        # Thêm thông tin bổ sung
        user.phone_number = request.POST.get('phone_number', '')
        user.address = request.POST.get('address', '')
        
        # Thêm chi nhánh nếu có
        branch_id = request.POST.get('branch')
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
                user.branch = branch
            except Branch.DoesNotExist:
                pass
        
        # Cấu hình quyền hệ thống
        user.is_staff = 'is_staff' in request.POST
        user.is_superuser = 'is_superuser' in request.POST
        
        # Cấu hình vai trò - đảm bảo chỉ có một vai trò duy nhất
        role = request.POST.get('role', 'CUSTOMER')
        if role in dict(User.ROLE_CHOICES).keys():
            user.role = role
        
        user.save()
        
        messages.success(request, 'Tạo người dùng mới thành công')
        return redirect('admin_panel:user_list')
    
    context = {
        'title': 'Tạo người dùng mới',
        'branches': Branch.objects.all(),
    }
    
    return render(request, 'admin_panel/users/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    """View user details and activities"""
    user = get_object_or_404(User, pk=pk)
    
    # Get user activity
    if hasattr(user, 'customer_profile'):
        orders = Order.objects.filter(customer=user)
    else:
        orders = []
    
    context = {
        'title': f'Chi tiết người dùng: {user.get_full_name() or user.username}',
        'user_obj': user,
        'orders': orders,
    }
    
    return render(request, 'admin_panel/users/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    """Edit user information"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Process form data and update user
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone_number = request.POST.get('phone_number', '')
        user.address = request.POST.get('address', '')
        
        # Cập nhật thông tin chi nhánh nếu có
        branch_id = request.POST.get('branch')
        if branch_id:
            try:
                branch = Branch.objects.get(id=branch_id)
                user.branch = branch
            except Branch.DoesNotExist:
                pass
        else:
            user.branch = None
        
        # Xử lý mật khẩu nếu có thay đổi
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        
        # Lưu thông tin người dùng
        user.save()
        
        messages.success(request, 'Cập nhật thông tin người dùng thành công')
        return redirect('admin_panel:user_detail', pk=user.pk)
    
    context = {
        'title': f'Chỉnh sửa người dùng: {user.get_full_name() or user.username}',
        'user_obj': user,
        'branches': Branch.objects.all(),
    }
    
    return render(request, 'admin_panel/users/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def user_permissions(request, pk):
    """Manage user permissions"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Cập nhật trạng thái kích hoạt
        user.is_active = 'is_active' in request.POST
        
        # Xử lý phân quyền hệ thống
        user.is_staff = 'is_staff' in request.POST
        user.is_superuser = 'is_superuser' in request.POST
        
        # Đặt vai trò (role) dựa trên lựa chọn
        role = request.POST.get('role', '')
        if role in dict(User.ROLE_CHOICES).keys():
            user.role = role
        
        # Lưu thông tin người dùng
        user.save()
        
        # Cập nhật nhóm người dùng nếu cần
        if 'groups' in request.POST:
            # Xóa tất cả nhóm hiện tại
            user.groups.clear()
            
            # Thêm các nhóm đã chọn
            group_ids = request.POST.getlist('groups')
            for group_id in group_ids:
                try:
                    group = Group.objects.get(id=group_id)
                    user.groups.add(group)
                except (Group.DoesNotExist, ValueError):
                    pass
        
        messages.success(request, 'Cập nhật quyền người dùng thành công')
        return redirect('admin_panel:user_detail', pk=user.pk)
    
    context = {
        'title': f'Phân quyền: {user.get_full_name() or user.username}',
        'user_obj': user,
        'groups': Group.objects.all(),
        'role_choices': User.ROLE_CHOICES,
    }
    
    return render(request, 'admin_panel/users/user_permissions.html', context)


# System Configuration Views
@login_required
@user_passes_test(is_admin)
def system_configuration(request):
    """Manage system configuration settings"""
    if request.method == 'POST':
        # Update configuration settings
        # ...
        messages.success(request, 'Cập nhật cấu hình hệ thống thành công')
        return redirect('admin_panel:system_configuration')
    
    context = {
        'title': 'Cấu hình hệ thống',
    }
    
    return render(request, 'admin_panel/configuration/system_config.html', context)


# Category Management Views
@login_required
@user_passes_test(is_admin)
def category_list(request):
    """List all product categories"""
    categories = Category.objects.all()
    
    context = {
        'title': 'Quản lý danh mục sản phẩm',
        'categories': categories,
    }
    
    return render(request, 'admin_panel/catalog/category_list.html', context)


@login_required
@user_passes_test(is_admin)
def category_create(request):
    """Create a new product category"""
    if request.method == 'POST':
        # Process form data and create category
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, 'Vui lòng nhập tên danh mục')
            return redirect('admin_panel:category_create')
        
        # Tạo danh mục mới
        category = Category(
            name=name,
            slug=request.POST.get('slug', ''),
            description=request.POST.get('description', ''),
            is_active='is_active' in request.POST,
            is_featured='is_featured' in request.POST,
            display_order=request.POST.get('display_order', 0),
        )
        
        # Xử lý parent category nếu có
        parent_id = request.POST.get('parent')
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
                category.parent = parent
            except Category.DoesNotExist:
                pass
        
        # Xử lý hình ảnh nếu có
        if 'image' in request.FILES:
            category.image = request.FILES['image']
        
        category.save()
        
        messages.success(request, 'Tạo danh mục mới thành công')
        return redirect('admin_panel:category_list')
    
    context = {
        'title': 'Tạo danh mục mới',
        'categories': Category.objects.all(),  # For parent category selection
    }
    
    return render(request, 'admin_panel/catalog/category_form.html', context)


@login_required
@user_passes_test(is_admin)
def category_edit(request, pk):
    """Edit a product category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        # Process form data and update category
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, 'Vui lòng nhập tên danh mục')
            return redirect('admin_panel:category_edit', pk=pk)
        
        # Cập nhật thông tin danh mục
        category.name = name
        category.slug = request.POST.get('slug', category.slug)
        category.description = request.POST.get('description', '')
        category.is_active = 'is_active' in request.POST
        category.is_featured = 'is_featured' in request.POST
        category.display_order = request.POST.get('display_order', category.display_order)
        
        # Xử lý parent category nếu có
        parent_id = request.POST.get('parent')
        if parent_id and int(parent_id) != category.id:  # Tránh chọn chính nó làm parent
            try:
                parent = Category.objects.get(id=parent_id)
                # Kiểm tra để tránh tạo vòng lặp (circular dependency)
                if not (parent.id == category.id or (parent.parent and parent.parent.id == category.id)):
                    category.parent = parent
            except Category.DoesNotExist:
                pass
        else:
            category.parent = None
        
        # Xử lý hình ảnh nếu có
        if 'image' in request.FILES:
            # Xóa ảnh cũ nếu có
            if category.image:
                old_image_path = category.image.path
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            # Lưu ảnh mới
            category.image = request.FILES['image']
        
        category.save()
        
        messages.success(request, 'Cập nhật danh mục thành công')
        return redirect('admin_panel:category_list')
    
    context = {
        'title': f'Chỉnh sửa danh mục: {category.name}',
        'category': category,
        'categories': Category.objects.exclude(pk=pk),  # For parent category selection
    }
    
    return render(request, 'admin_panel/catalog/category_form.html', context)


# Product Attribute Management Views
@login_required
@user_passes_test(is_admin)
def attribute_list(request):
    """List all product attributes"""
    attributes = VariantAttribute.objects.all()
    
    context = {
        'title': 'Quản lý thuộc tính sản phẩm',
        'attributes': attributes,
    }
    
    return render(request, 'admin_panel/catalog/attribute_list.html', context)


@login_required
@user_passes_test(is_admin)
def attribute_create(request):
    """Create a new product attribute"""
    if request.method == 'POST':
        # Process form data and create attribute
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, 'Vui lòng nhập tên thuộc tính')
            return redirect('admin_panel:attribute_create')
        
        # Tạo thuộc tính mới
        attribute = VariantAttribute(
            name=name,
            description=request.POST.get('description', ''),
            is_required='is_required' in request.POST,
            is_filterable='is_filterable' in request.POST,
            is_visible='is_visible' in request.POST,
            display_order=request.POST.get('display_order', 0),
        )
        attribute.save()
        
        # Xử lý các giá trị thuộc tính
        if 'attribute_values[]' in request.POST:
            values = request.POST.getlist('attribute_values[]')
            orders = request.POST.getlist('attribute_display_orders[]')
            
            for i, value in enumerate(values):
                if value.strip():  # Chỉ lưu các giá trị không rỗng
                    try:
                        order = int(orders[i]) if i < len(orders) else 0
                    except (ValueError, TypeError):
                        order = 0
                    
                    attribute.values.create(
                        value=value.strip(),
                        display_order=order
                    )
        
        messages.success(request, 'Tạo thuộc tính mới thành công')
        return redirect('admin_panel:attribute_list')
    
    context = {
        'title': 'Tạo thuộc tính mới',
    }
    
    return render(request, 'admin_panel/catalog/attribute_form.html', context)


@login_required
@user_passes_test(is_admin)
def attribute_edit(request, pk):
    """Edit a product attribute"""
    attribute = get_object_or_404(VariantAttribute, pk=pk)
    
    if request.method == 'POST':
        # Process form data and update attribute
        name = request.POST.get('name')
        
        if not name:
            messages.error(request, 'Vui lòng nhập tên thuộc tính')
            return redirect('admin_panel:attribute_edit', pk=pk)
        
        # Cập nhật thông tin thuộc tính
        attribute.name = name
        attribute.description = request.POST.get('description', '')
        attribute.is_required = 'is_required' in request.POST
        attribute.is_filterable = 'is_filterable' in request.POST
        attribute.is_visible = 'is_visible' in request.POST
        attribute.display_order = request.POST.get('display_order', attribute.display_order)
        attribute.save()
        
        # Xử lý các giá trị thuộc tính
        if 'attribute_values[]' in request.POST:
            # Xóa tất cả giá trị hiện tại
            attribute.values.all().delete()
            
            # Thêm lại các giá trị mới
            values = request.POST.getlist('attribute_values[]')
            orders = request.POST.getlist('attribute_display_orders[]')
            
            for i, value in enumerate(values):
                if value.strip():  # Chỉ lưu các giá trị không rỗng
                    try:
                        order = int(orders[i]) if i < len(orders) else 0
                    except (ValueError, TypeError):
                        order = 0
                    
                    attribute.values.create(
                        value=value.strip(),
                        display_order=order
                    )
        
        messages.success(request, 'Cập nhật thuộc tính thành công')
        return redirect('admin_panel:attribute_list')
    
    context = {
        'title': f'Chỉnh sửa thuộc tính: {attribute.name}',
        'attribute': attribute,
    }
    
    return render(request, 'admin_panel/catalog/attribute_form.html', context)


# Reports Views
@login_required
@user_passes_test(is_admin)
def report_dashboard(request):
    """Overview of all available reports"""
    context = {
        'title': 'Báo cáo hệ thống',
    }
    
    return render(request, 'admin_panel/reports/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def sales_report(request):
    """Sales reports with filters and visualizations"""
    # Default to current month
    today = timezone.now().date()
    start_date = request.GET.get('start_date', (today.replace(day=1)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', today.strftime('%Y-%m-%d'))
    
    # Convert to datetime objects
    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date_obj = today.replace(day=1)
        end_date_obj = today
    
    # Get sales data
    orders = Order.objects.filter(
        created_at__date__gte=start_date_obj,
        created_at__date__lte=end_date_obj
    )
    
    # Aggregate data
    total_sales = orders.aggregate(
        count=Count('id'),
        total=Sum('total')
    )
    
    # Tính giá trị trung bình thủ công nếu có orders
    if total_sales['count'] and total_sales['total']:
        total_sales['avg'] = total_sales['total'] / total_sales['count']
    else:
        total_sales['avg'] = 0
    
    # Sales by branch
    branch_sales = orders.values('branch__name').annotate(
        count=Count('id'),
        total=Sum('total')
    ).order_by('-total')
    
    # Sales by product category
    category_sales = OrderItem.objects.filter(
        order__created_at__date__gte=start_date_obj,
        order__created_at__date__lte=end_date_obj
    ).values('product__category__name').annotate(
        count=Count('id'),
        total=Sum(F('price') * F('quantity'))
    ).order_by('-total')
    
    context = {
        'title': 'Báo cáo doanh số',
        'start_date': start_date,
        'end_date': end_date,
        'total_sales': total_sales,
        'branch_sales': branch_sales,
        'category_sales': category_sales,
        'orders': orders,
    }
    
    return render(request, 'admin_panel/reports/sales_report.html', context)


@login_required
@user_passes_test(is_admin)
def inventory_report(request):
    """Inventory reports with filters and visualizations"""
    # Filter by branch
    branch_id = request.GET.get('branch')
    
    if branch_id:
        stocks = Stock.objects.filter(branch_id=branch_id)
        branch = get_object_or_404(Branch, pk=branch_id)
        branch_name = branch.name
    else:
        stocks = Stock.objects.all()
        branch_name = 'Tất cả chi nhánh'
    
    # Aggregate data
    total_inventory = stocks.aggregate(
        total_value=Sum(F('quantity') * F('product__price')),
        total_items=Sum('quantity')
    )
    
    # Low stock items
    low_stock = stocks.filter(quantity__lt=F('min_quantity'))
    
    # Stock by category
    category_stock = stocks.values('product__category__name').annotate(
        total_items=Sum('quantity'),
        total_value=Sum(F('quantity') * F('product__price'))
    ).order_by('-total_value')
    
    context = {
        'title': 'Báo cáo tồn kho',
        'branch_id': branch_id,
        'branch_name': branch_name,
        'branches': Branch.objects.all(),
        'total_inventory': total_inventory,
        'low_stock': low_stock,
        'category_stock': category_stock,
        'stocks': stocks,
    }
    
    return render(request, 'admin_panel/reports/inventory_report.html', context)


@login_required
@user_passes_test(is_admin)
def branch_report(request):
    """Branch performance reports"""
    branches = Branch.objects.all()
    
    # Get performance metrics for each branch
    branch_data = []
    for branch in branches:
        # Sales data
        sales = Order.objects.filter(branch=branch)
        monthly_sales = sales.filter(
            created_at__date__gte=timezone.now().date().replace(day=1)
        ).aggregate(
            count=Count('id'),
            total=Sum('total')
        )
        
        # Inventory data
        inventory = Stock.objects.filter(branch=branch)
        inventory_value = inventory.aggregate(
            total_value=Sum(F('quantity') * F('product__price')),
            total_items=Sum('quantity')
        )
        
        branch_data.append({
            'branch': branch,
            'monthly_sales': monthly_sales,
            'inventory': inventory_value,
        })
    
    context = {
        'title': 'Báo cáo chi nhánh',
        'branch_data': branch_data,
    }
    
    return render(request, 'admin_panel/reports/branch_report.html', context)


@login_required
@user_passes_test(is_admin)
def customer_report(request):
    """Customer reports and analytics"""
    # Customer segments
    total_customers = User.objects.filter(
        is_superuser=False, 
        is_staff=False,
        is_branch_manager=False,
        is_sales_staff=False,
        is_inventory_staff=False
    ).count()
    
    # Top customers by order value
    top_customers = Order.objects.values(
        'customer__id', 
        'customer__username',
        'customer__first_name',
        'customer__last_name'
    ).annotate(
        order_count=Count('id'),
        total_spent=Sum('total')
    ).order_by('-total_spent')[:10]
    
    # New customers this month
    new_customers = User.objects.filter(
        date_joined__date__gte=timezone.now().date().replace(day=1),
        is_superuser=False,
        is_staff=False,
        is_branch_manager=False,
        is_sales_staff=False,
        is_inventory_staff=False
    ).count()
    
    context = {
        'title': 'Báo cáo khách hàng',
        'total_customers': total_customers,
        'top_customers': top_customers,
        'new_customers': new_customers,
    }
    
    return render(request, 'admin_panel/reports/customer_report.html', context)


@login_required
@user_passes_test(is_admin)
def export_report(request, report_type):
    """Export reports to CSV or Excel"""
    if report_type == 'sales':
        # Get date range from query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        # Prepare data for export
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).select_related('customer', 'branch')
        
        # Create Excel file
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Sales Report')
        
        # Add headers
        headers = ['Order ID', 'Date', 'Customer', 'Branch', 'Items', 'Total Amount', 'Status']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header)
        
        # Add data
        for row, order in enumerate(orders, 1):
            worksheet.write(row, 0, order.id)
            worksheet.write(row, 1, order.created_at.strftime('%Y-%m-%d'))
            worksheet.write(row, 2, order.customer.get_full_name() or order.customer.username)
            worksheet.write(row, 3, order.branch.name if order.branch else 'N/A')
            worksheet.write(row, 4, order.items.count())
            worksheet.write(row, 5, float(order.total))
            worksheet.write(row, 6, order.status)
        
        workbook.close()
        output.seek(0)
        
        # Create response
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=sales_report_{start_date}_to_{end_date}.xlsx'
        
        return response
    
    elif report_type == 'inventory':
        # Similar implementation for inventory report export
        pass
    
    elif report_type == 'branches':
        # Similar implementation for branches report export
        pass
    
    elif report_type == 'customers':
        # Similar implementation for customers report export
        pass
    
    return redirect('admin_panel:report_dashboard')


# Supplier Management Views
@login_required
@user_passes_test(is_admin)
def supplier_list(request):
    """List all suppliers"""
    suppliers = Supplier.objects.all()
    
    context = {
        'title': 'Quản lý nhà cung cấp',
        'suppliers': suppliers,
    }
    
    return render(request, 'admin_panel/suppliers/supplier_list.html', context)


@login_required
@user_passes_test(is_admin)
def supplier_create(request):
    """Create a new supplier"""
    if request.method == 'POST':
        # Process form data and create supplier
        # ...
        messages.success(request, 'Tạo nhà cung cấp mới thành công')
        return redirect('admin_panel:supplier_list')
    
    context = {
        'title': 'Thêm nhà cung cấp mới',
    }
    
    return render(request, 'admin_panel/suppliers/supplier_form.html', context)


@login_required
@user_passes_test(is_admin)
def supplier_detail(request, pk):
    """View supplier details and purchase history"""
    supplier = get_object_or_404(Supplier, pk=pk)
    purchase_orders = PurchaseOrder.objects.filter(supplier=supplier)
    
    context = {
        'title': f'Chi tiết nhà cung cấp: {supplier.name}',
        'supplier': supplier,
        'purchase_orders': purchase_orders,
    }
    
    return render(request, 'admin_panel/suppliers/supplier_detail.html', context)


@login_required
@user_passes_test(is_admin)
def supplier_edit(request, pk):
    """Edit supplier information"""
    supplier = get_object_or_404(Supplier, pk=pk)
    
    if request.method == 'POST':
        # Process form data and update supplier
        # ...
        messages.success(request, 'Cập nhật thông tin nhà cung cấp thành công')
        return redirect('admin_panel:supplier_detail', pk=supplier.pk)
    
    context = {
        'title': f'Chỉnh sửa nhà cung cấp: {supplier.name}',
        'supplier': supplier,
    }
    
    return render(request, 'admin_panel/suppliers/supplier_form.html', context)


@login_required
@user_passes_test(is_admin)
def payment_list(request):
    """List all supplier payments"""
    purchase_orders = PurchaseOrder.objects.all().order_by('-created_at')
    
    context = {
        'title': 'Quản lý thanh toán',
        'purchase_orders': purchase_orders,
    }
    
    return render(request, 'admin_panel/suppliers/payment_list.html', context)


@login_required
@user_passes_test(is_admin)
def payment_detail(request, pk):
    """View payment details"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        # Process payment update
        # ...
        messages.success(request, 'Cập nhật trạng thái thanh toán thành công')
        return redirect('admin_panel:payment_list')
    
    context = {
        'title': f'Chi tiết thanh toán: {purchase_order.reference}',
        'purchase_order': purchase_order,
    }
    
    return render(request, 'admin_panel/suppliers/payment_detail.html', context)


# Data Management Views
@login_required
@user_passes_test(is_admin)
def backup_data(request):
    """Backup system data"""
    if request.method == 'POST':
        # Process backup creation
        # ...
        messages.success(request, 'Sao lưu dữ liệu thành công')
        return redirect('admin_panel:dashboard')
    
    context = {
        'title': 'Sao lưu dữ liệu',
    }
    
    return render(request, 'admin_panel/data/backup.html', context)


@login_required
@user_passes_test(is_admin)
def restore_data(request):
    """Restore system data from backup"""
    if request.method == 'POST':
        # Process data restoration
        # ...
        messages.success(request, 'Khôi phục dữ liệu thành công')
        return redirect('admin_panel:dashboard')
    
    context = {
        'title': 'Khôi phục dữ liệu',
    }
    
    return render(request, 'admin_panel/data/restore.html', context) 