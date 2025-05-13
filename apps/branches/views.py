from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Branch
from apps.staff.models import StaffProfile, Performance
from apps.orders.models import Order
from apps.inventory.models import Stock
from apps.products.models import Product


@login_required
def manager_dashboard(request):
    """Dashboard view for branch managers"""
    # Get the manager's branch
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    today = timezone.now().date()
    current_month = today.replace(day=1)
    previous_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # Branch performance metrics
    daily_sales = Order.objects.filter(
        branch=branch,
        created_at__date=today
    ).aggregate(
        total_amount=Sum('total_amount'),
        count=Count('id')
    )
    
    monthly_sales = Order.objects.filter(
        branch=branch,
        created_at__date__gte=current_month,
        created_at__date__lte=today
    ).aggregate(
        total_amount=Sum('total_amount'),
        count=Count('id')
    )
    
    # Calculate month-over-month growth
    previous_monthly_sales = Order.objects.filter(
        branch=branch,
        created_at__date__gte=previous_month,
        created_at__date__lt=current_month
    ).aggregate(
        total_amount=Sum('total_amount')
    )
    
    if previous_monthly_sales['total_amount'] and monthly_sales['total_amount']:
        monthly_growth = ((monthly_sales['total_amount'] - previous_monthly_sales['total_amount']) / 
                          previous_monthly_sales['total_amount']) * 100
    else:
        monthly_growth = 0
    
    # Inventory status
    inventory_status = Stock.objects.filter(branch=branch).aggregate(
        total_products=Count('product', distinct=True),
        low_stock=Count('id', filter=Q(quantity__lte=F('min_quantity'))),
        out_of_stock=Count('id', filter=Q(quantity=0))
    )
    
    # Staff performance
    staff_members = StaffProfile.objects.filter(branch=branch)
    top_performers = Performance.objects.filter(
        staff__in=staff_members,
        period=today.strftime('%m/%Y')
    ).order_by('-achievement_percentage')[:5]
    
    # Recent orders
    recent_orders = Order.objects.filter(branch=branch).order_by('-created_at')[:10]
    
    # Sales by category data for chart
    sales_by_category = Order.objects.filter(
        branch=branch,
        created_at__date__gte=current_month
    ).values('items__product__category__name').annotate(
        total=Sum(F('items__quantity') * F('items__price'))
    ).order_by('-total')
    
    category_names = [item['items__product__category__name'] for item in sales_by_category if item['items__product__category__name']]
    category_values = [float(item['total']) for item in sales_by_category if item['items__product__category__name']]
    
    # Daily sales data for chart (last 7 days)
    daily_sales_data = []
    daily_sales_dates = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_sales_dates.append(date.strftime('%d/%m'))
        
        day_sales = Order.objects.filter(
            branch=branch,
            created_at__date=date
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        daily_sales_data.append(day_sales)
    
    context = {
        'branch': branch,
        'daily_sales': daily_sales,
        'monthly_sales': monthly_sales,
        'monthly_growth': monthly_growth,
        'inventory_status': inventory_status,
        'top_performers': top_performers,
        'recent_orders': recent_orders,
        'category_names': category_names,
        'category_values': category_values,
        'daily_sales_dates': daily_sales_dates,
        'daily_sales_data': daily_sales_data,
    }
    
    return render(request, 'branches/manager_dashboard.html', context)


@login_required
def manager_sales(request):
    """View for branch managers to manage sales"""
    # Get the manager's branch
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get sales data
    sales_data = Order.objects.filter(branch=branch).order_by('-created_at')
    
    context = {
        'branch': branch,
        'sales_data': sales_data,
    }
    
    return render(request, 'branches/manager_sales.html', context)


@login_required
def manager_daily_sales(request):
    """View for daily sales report"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get date parameter or use today
    date_str = request.GET.get('date')
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = timezone.now().date()
    else:
        date = timezone.now().date()
    
    # Get daily sales
    orders = Order.objects.filter(
        branch=branch,
        created_at__date=date
    ).order_by('-created_at')
    
    daily_total = orders.aggregate(
        total_amount=Sum('total_amount'),
        count=Count('id')
    )
    
    context = {
        'branch': branch,
        'date': date,
        'orders': orders,
        'daily_total': daily_total,
    }
    
    return render(request, 'branches/manager_daily_sales.html', context)


@login_required
def manager_monthly_sales(request):
    """View for monthly sales report"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get month parameter or use current month
    month_str = request.GET.get('month')
    if month_str:
        try:
            month_date = datetime.strptime(month_str, '%Y-%m')
            year, month = month_date.year, month_date.month
        except ValueError:
            today = timezone.now().date()
            year, month = today.year, today.month
    else:
        today = timezone.now().date()
        year, month = today.year, today.month
    
    # Get first and last day of the month
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # Get monthly sales
    orders = Order.objects.filter(
        branch=branch,
        created_at__date__gte=first_day,
        created_at__date__lte=last_day
    ).order_by('-created_at')
    
    monthly_total = orders.aggregate(
        total_amount=Sum('total_amount'),
        count=Count('id')
    )
    
    # Group by day for chart
    daily_data = []
    
    for day in range(1, last_day.day + 1):
        day_date = datetime(year, month, day).date()
        day_orders = orders.filter(created_at__date=day_date)
        day_total = day_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        daily_data.append({
            'day': day,
            'total': day_total,
            'count': day_orders.count()
        })
    
    context = {
        'branch': branch,
        'year': year,
        'month': month,
        'month_name': first_day.strftime('%B'),
        'orders': orders,
        'monthly_total': monthly_total,
        'daily_data': daily_data,
    }
    
    return render(request, 'branches/manager_monthly_sales.html', context)


@login_required
def manager_yearly_sales(request):
    """View for yearly sales report"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get year parameter or use current year
    year_str = request.GET.get('year')
    if year_str:
        try:
            year = int(year_str)
        except ValueError:
            year = timezone.now().date().year
    else:
        year = timezone.now().date().year
    
    # Get yearly sales
    first_day = datetime(year, 1, 1).date()
    last_day = datetime(year, 12, 31).date()
    
    orders = Order.objects.filter(
        branch=branch,
        created_at__date__gte=first_day,
        created_at__date__lte=last_day
    )
    
    yearly_total = orders.aggregate(
        total_amount=Sum('total_amount'),
        count=Count('id')
    )
    
    # Group by month for chart
    monthly_data = []
    
    for month in range(1, 13):
        month_first_day = datetime(year, month, 1).date()
        if month == 12:
            month_last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        month_orders = orders.filter(
            created_at__date__gte=month_first_day,
            created_at__date__lte=month_last_day
        )
        
        month_total = month_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        monthly_data.append({
            'month': month_first_day.strftime('%B'),
            'total': month_total,
            'count': month_orders.count()
        })
    
    context = {
        'branch': branch,
        'year': year,
        'orders': orders,
        'yearly_total': yearly_total,
        'monthly_data': monthly_data,
    }
    
    return render(request, 'branches/manager_yearly_sales.html', context)


@login_required
def manager_inventory(request):
    """View for inventory management by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get inventory data
    inventory = Stock.objects.filter(branch=branch).select_related('product', 'product__category')
    
    # Filter by category if requested
    category_id = request.GET.get('category')
    if category_id:
        inventory = inventory.filter(product__category_id=category_id)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        inventory = inventory.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query)
        )
    
    context = {
        'branch': branch,
        'inventory': inventory,
        'search_query': search_query,
        'category_id': category_id,
    }
    
    return render(request, 'branches/manager_inventory.html', context)


@login_required
def manager_low_stock(request):
    """View for low stock items by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get low stock items
    low_stock = Stock.objects.filter(
        branch=branch,
        quantity__lte=F('min_quantity')
    ).select_related('product', 'product__category')
    
    context = {
        'branch': branch,
        'low_stock': low_stock,
    }
    
    return render(request, 'branches/manager_low_stock.html', context)


@login_required
def manager_inventory_valuation(request):
    """View for inventory valuation by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get inventory with values
    inventory = Stock.objects.filter(branch=branch).select_related('product')
    
    # Calculate total valuation
    total_valuation = sum(item.quantity * item.product.cost_price for item in inventory)
    
    context = {
        'branch': branch,
        'inventory': inventory,
        'total_valuation': total_valuation,
    }
    
    return render(request, 'branches/manager_inventory_valuation.html', context)


@login_required
def manager_orders(request):
    """View for orders management by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get orders
    orders = Order.objects.filter(branch=branch).order_by('-created_at')
    
    # Filter by status if requested
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'branch': branch,
        'orders': orders,
        'status': status,
    }
    
    return render(request, 'branches/manager_orders.html', context)


@login_required
def manager_order_detail(request, order_id):
    """View for order details by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get order
    order = get_object_or_404(Order, id=order_id, branch=branch)
    
    context = {
        'branch': branch,
        'order': order,
    }
    
    return render(request, 'branches/manager_order_detail.html', context)


@login_required
def manager_pending_orders(request):
    """View for pending orders by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get pending orders
    pending_orders = Order.objects.filter(
        branch=branch,
        status='pending'
    ).order_by('-created_at')
    
    context = {
        'branch': branch,
        'pending_orders': pending_orders,
    }
    
    return render(request, 'branches/manager_pending_orders.html', context)


@login_required
def manager_completed_orders(request):
    """View for completed orders by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get completed orders
    completed_orders = Order.objects.filter(
        branch=branch,
        status='completed'
    ).order_by('-created_at')
    
    context = {
        'branch': branch,
        'completed_orders': completed_orders,
    }
    
    return render(request, 'branches/manager_completed_orders.html', context)


@login_required
def manager_cancelled_orders(request):
    """View for cancelled orders by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get cancelled orders
    cancelled_orders = Order.objects.filter(
        branch=branch,
        status='cancelled'
    ).order_by('-created_at')
    
    context = {
        'branch': branch,
        'cancelled_orders': cancelled_orders,
    }
    
    return render(request, 'branches/manager_cancelled_orders.html', context)


@login_required
def manager_staff(request):
    """View for staff management by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get staff members
    staff_members = StaffProfile.objects.filter(branch=branch)
    
    context = {
        'branch': branch,
        'staff_members': staff_members,
    }
    
    return render(request, 'branches/manager_staff.html', context)


@login_required
def manager_staff_detail(request, staff_id):
    """View for staff details by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get staff member
    staff = get_object_or_404(StaffProfile, id=staff_id, branch=branch)
    
    # Get performance data
    performances = Performance.objects.filter(staff=staff).order_by('-period')
    
    # Get recent orders handled by this staff
    recent_orders = Order.objects.filter(staff=staff.user).order_by('-created_at')[:10]
    
    context = {
        'branch': branch,
        'staff': staff,
        'performances': performances,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'branches/manager_staff_detail.html', context)


@login_required
def manager_staff_create(request):
    """View for creating new staff member by branch manager"""
    # Implementation depends on your forms and models
    return render(request, 'branches/manager_staff_form.html')


@login_required
def manager_staff_update(request, staff_id):
    """View for updating staff member by branch manager"""
    # Implementation depends on your forms and models
    staff = get_object_or_404(StaffProfile, id=staff_id)
    return render(request, 'branches/manager_staff_form.html', {'staff': staff})


@login_required
def manager_staff_performance(request):
    """View for staff performance overview by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Get current period
    today = timezone.now().date()
    current_period = today.strftime('%m/%Y')
    
    # Get all staff performances for current period
    performances = Performance.objects.filter(
        staff__branch=branch,
        period=current_period
    ).select_related('staff')
    
    context = {
        'branch': branch,
        'performances': performances,
        'current_period': current_period,
    }
    
    return render(request, 'branches/manager_staff_performance.html', context)


@login_required
def manager_staff_schedule(request):
    """View for staff schedule by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Implementation depends on your schedule model
    
    context = {
        'branch': branch,
    }
    
    return render(request, 'branches/manager_staff_schedule.html', context)


@login_required
def manager_customers(request):
    """View for customer management by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    # Implementation depends on your customer model
    
    context = {
        'branch': branch,
    }
    
    return render(request, 'branches/manager_customers.html', context)


@login_required
def manager_customer_detail(request, customer_id):
    """View for customer details by branch manager"""
    # Implementation depends on your customer model
    return render(request, 'branches/manager_customer_detail.html')


@login_required
def manager_vip_customers(request):
    """View for VIP customers by branch manager"""
    # Implementation depends on your customer model
    return render(request, 'branches/manager_vip_customers.html')


@login_required
def manager_reports(request):
    """View for reports dashboard by branch manager"""
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
    else:
        messages.warning(request, "You are not assigned to a branch.")
        return redirect('account_login')
    
    context = {
        'branch': branch,
    }
    
    return render(request, 'branches/manager_reports.html', context)


@login_required
def manager_sales_report(request):
    """View for sales report by branch manager"""
    # Implementation depends on your reporting needs
    return render(request, 'branches/manager_sales_report.html')


@login_required
def manager_inventory_report(request):
    """View for inventory report by branch manager"""
    # Implementation depends on your reporting needs
    return render(request, 'branches/manager_inventory_report.html')


@login_required
def manager_staff_report(request):
    """View for staff report by branch manager"""
    # Implementation depends on your reporting needs
    return render(request, 'branches/manager_staff_report.html')


@login_required
def manager_customer_report(request):
    """View for customer report by branch manager"""
    # Implementation depends on your reporting needs
    return render(request, 'branches/manager_customer_report.html')


@login_required
def manager_export_report_pdf(request, report_type):
    """View for exporting reports as PDF by branch manager"""
    # Implementation depends on your PDF generation approach
    return redirect('branches:manager_reports')


@login_required
def manager_settings(request):
    """View for branch manager settings"""
    # Implementation depends on your settings model
    return render(request, 'branches/manager_settings.html')


@login_required
def manager_branch_settings(request):
    """View for branch settings by branch manager"""
    # Implementation depends on your settings model
    return render(request, 'branches/manager_branch_settings.html')


@login_required
def manager_targets_settings(request):
    """View for sales targets settings by branch manager"""
    # Implementation depends on your targets model
    return render(request, 'branches/manager_targets_settings.html')


class AdminAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or hasattr(self.request.user, 'profile') and self.request.user.profile.is_manager


class BranchListView(LoginRequiredMixin, ListView):
    model = Branch
    template_name = 'branches/branch_list.html'
    context_object_name = 'branches'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Nếu không phải admin, chỉ hiển thị chi nhánh hoạt động
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_active=True)
        
        return queryset


class BranchDetailView(LoginRequiredMixin, DetailView):
    model = Branch
    template_name = 'branches/branch_detail.html'
    context_object_name = 'branch'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        branch = self.get_object()
        
        # Thêm thông tin bổ sung về chi nhánh
        context['staff_count'] = branch.staff_count
        context['active_orders'] = branch.active_orders_count
        
        return context


class BranchCreateView(LoginRequiredMixin, AdminAccessMixin, CreateView):
    model = Branch
    template_name = 'branches/branch_form.html'
    fields = ['name', 'address', 'phone', 'email', 'manager', 'is_active', 'opening_date']
    success_url = reverse_lazy('branches:branch_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Chi nhánh {form.instance.name} đã được tạo thành công.")
        return super().form_valid(form)


class BranchUpdateView(LoginRequiredMixin, AdminAccessMixin, UpdateView):
    model = Branch
    template_name = 'branches/branch_form.html'
    fields = ['name', 'address', 'phone', 'email', 'manager', 'is_active', 'opening_date']
    
    def get_success_url(self):
        return reverse_lazy('branches:branch_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, f"Chi nhánh {form.instance.name} đã được cập nhật.")
        return super().form_valid(form) 