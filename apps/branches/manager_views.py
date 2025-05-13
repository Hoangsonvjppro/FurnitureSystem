from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import json
import calendar

from apps.accounts.models import User
from apps.products.models import Product
from apps.inventory.models import Stock, StockMovement
from apps.orders.models import Order
from apps.branches.models import Branch


@login_required
def dashboard(request):
    """Dashboard cho quản lý chi nhánh"""
    # Chi nhánh của người quản lý
    branch = request.user.branch
    
    # Ngày hiện tại
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    current_month = today.month
    current_year = today.year
    
    # Doanh thu hôm nay
    today_revenue = Order.objects.filter(
        branch=branch,
        created_at__date=today,
        status__in=['delivered', 'completed']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Đếm đơn hàng mới
    new_orders_count = Order.objects.filter(
        branch=branch,
        status='pending'
    ).count()
    
    # Đếm sản phẩm sắp hết
    low_stock_count = Stock.objects.filter(
        branch=branch,
        quantity__lte=F('min_quantity')
    ).count()
    
    # Đếm nhân viên
    staff_count = User.objects.filter(
        branch=branch,
        role__in=['SALES_STAFF', 'INVENTORY_STAFF']
    ).count()
    
    # Doanh thu theo tháng trong 12 tháng gần nhất
    revenue_data = []
    revenue_months = []
    
    for i in range(12, 0, -1):
        month = (today.month - i) % 12 + 1
        year = today.year - ((i - month) // 12 + (1 if month > today.month else 0))
        month_name = calendar.month_name[month][:3] + " " + str(year)
        
        # Tính tổng doanh thu trong tháng đó
        month_revenue = Order.objects.filter(
            branch=branch,
            created_at__month=month,
            created_at__year=year,
            status__in=['delivered', 'completed']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Chuyển đổi sang đơn vị triệu
        revenue_data.append(round(month_revenue / 1000000, 2))
        revenue_months.append(month_name)
    
    # Thống kê đơn hàng theo trạng thái
    pending_count = Order.objects.filter(branch=branch, status='pending').count()
    processing_count = Order.objects.filter(branch=branch, status='processing').count()
    shipped_count = Order.objects.filter(branch=branch, status='shipped').count()
    delivered_count = Order.objects.filter(branch=branch, status='delivered').count()
    cancelled_count = Order.objects.filter(branch=branch, status='cancelled').count()
    
    order_status_data = [pending_count, processing_count, shipped_count, delivered_count, cancelled_count]
    
    # 10 đơn hàng mới nhất
    recent_orders = Order.objects.filter(branch=branch).order_by('-created_at')[:10]
    
    # 10 sản phẩm sắp hết hàng
    low_stock_products = Stock.objects.filter(
        branch=branch,
        quantity__lte=F('min_quantity')
    ).select_related('product').order_by('quantity')[:10]
    
    context = {
        'today_revenue': today_revenue,
        'new_orders_count': new_orders_count,
        'low_stock_count': low_stock_count,
        'staff_count': staff_count,
        'revenue_data': json.dumps(revenue_data),
        'revenue_months': json.dumps(revenue_months),
        'order_status_data': json.dumps(order_status_data),
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'branch_manager/dashboard.html', context)


@login_required
def staff_list(request):
    """Danh sách nhân viên trong chi nhánh"""
    branch = request.user.branch
    
    staff = User.objects.filter(
        branch=branch,
        role__in=['SALES_STAFF', 'INVENTORY_STAFF']
    ).order_by('role', 'last_name', 'first_name')
    
    context = {
        'staff': staff,
    }
    
    return render(request, 'branch_manager/staff_list.html', context)


@login_required
def staff_create(request):
    """Tạo nhân viên mới"""
    # Implement form handling here
    return render(request, 'branch_manager/staff_form.html')


@login_required
def staff_detail(request, pk):
    """Chi tiết nhân viên"""
    staff = get_object_or_404(User, pk=pk, branch=request.user.branch)
    
    context = {
        'staff': staff,
    }
    
    return render(request, 'branch_manager/staff_detail.html', context)


@login_required
def staff_update(request, pk):
    """Cập nhật thông tin nhân viên"""
    # Implement form handling here
    staff = get_object_or_404(User, pk=pk, branch=request.user.branch)
    
    context = {
        'staff': staff,
    }
    
    return render(request, 'branch_manager/staff_form.html', context)


@login_required
def inventory_overview(request):
    """Tổng quan kho hàng"""
    branch = request.user.branch
    
    # Tính tổng giá trị kho
    total_value = Stock.objects.filter(branch=branch).annotate(
        value=F('quantity') * F('product__price')
    ).aggregate(total=Sum('value'))['total'] or 0
    
    # Tổng số sản phẩm khác nhau trong kho
    unique_products = Stock.objects.filter(branch=branch).count()
    
    # Tổng số lượng tất cả sản phẩm
    total_quantity = Stock.objects.filter(branch=branch).aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    # Sản phẩm hết hàng
    out_of_stock = Stock.objects.filter(branch=branch, quantity=0).count()
    
    # Sản phẩm sắp hết hàng
    low_stock = Stock.objects.filter(
        branch=branch, 
        quantity__gt=0,
        quantity__lte=F('min_quantity')
    ).count()
    
    context = {
        'total_value': total_value,
        'unique_products': unique_products,
        'total_quantity': total_quantity,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
    }
    
    return render(request, 'branch_manager/inventory_overview.html', context)


@login_required
def stock_list(request):
    """Danh sách tồn kho"""
    branch = request.user.branch
    
    stocks = Stock.objects.filter(branch=branch).select_related('product')
    
    context = {
        'stocks': stocks,
    }
    
    return render(request, 'branch_manager/stock_list.html', context)


@login_required
def stock_detail(request, pk):
    """Chi tiết tồn kho của một sản phẩm"""
    branch = request.user.branch
    stock = get_object_or_404(Stock, pk=pk, branch=branch)
    
    # Lịch sử di chuyển kho của sản phẩm
    movements = StockMovement.objects.filter(
        Q(from_branch=branch) | Q(to_branch=branch),
        product=stock.product
    ).order_by('-created_at')[:20]
    
    context = {
        'stock': stock,
        'movements': movements,
    }
    
    return render(request, 'branch_manager/stock_detail.html', context)


@login_required
def sales_overview(request):
    """Tổng quan doanh số"""
    branch = request.user.branch
    
    # Ngày hiện tại
    today = timezone.now().date()
    
    # Doanh thu hôm nay
    today_revenue = Order.objects.filter(
        branch=branch,
        created_at__date=today,
        status__in=['delivered', 'completed']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Doanh thu tuần này
    start_of_week = today - timedelta(days=today.weekday())
    week_revenue = Order.objects.filter(
        branch=branch,
        created_at__date__gte=start_of_week,
        status__in=['delivered', 'completed']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Doanh thu tháng này
    start_of_month = today.replace(day=1)
    month_revenue = Order.objects.filter(
        branch=branch,
        created_at__date__gte=start_of_month,
        status__in=['delivered', 'completed']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Đơn hàng hôm nay
    today_orders = Order.objects.filter(
        branch=branch,
        created_at__date=today
    ).count()
    
    context = {
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'month_revenue': month_revenue,
        'today_orders': today_orders,
    }
    
    return render(request, 'branch_manager/sales_overview.html', context)


@login_required
def sales_report(request):
    """Báo cáo doanh số chi tiết"""
    # Implement filter and report generation
    return render(request, 'branch_manager/sales_report.html')


@login_required
def order_list(request):
    """Danh sách đơn hàng"""
    branch = request.user.branch
    
    # Lọc đơn hàng theo status nếu có
    status = request.GET.get('status')
    if status:
        orders = Order.objects.filter(branch=branch, status=status)
    else:
        orders = Order.objects.filter(branch=branch)
    
    # Sắp xếp theo thời gian tạo, mới nhất lên đầu
    orders = orders.order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'branch_manager/order_list.html', context)


@login_required
def order_detail(request, pk):
    """Chi tiết đơn hàng"""
    branch = request.user.branch
    order = get_object_or_404(Order, pk=pk, branch=branch)
    
    context = {
        'order': order,
    }
    
    return render(request, 'branch_manager/order_detail.html', context)


@login_required
def approval_list(request):
    """Danh sách yêu cầu cần phê duyệt"""
    # Implement
    return render(request, 'branch_manager/approval_list.html')


@login_required
def approval_detail(request, pk):
    """Chi tiết yêu cầu cần phê duyệt"""
    # Implement
    return render(request, 'branch_manager/approval_detail.html')


@login_required
def approve_request(request, pk):
    """Phê duyệt yêu cầu"""
    # Implement
    return redirect('branch_manager:approval_list')


@login_required
def reject_request(request, pk):
    """Từ chối yêu cầu"""
    # Implement
    return redirect('branch_manager:approval_list') 