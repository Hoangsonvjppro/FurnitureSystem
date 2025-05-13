from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.utils import timezone

from .models import StaffProfile, StaffSchedule, Performance
from .forms import StaffProfileForm, StaffScheduleForm, PerformanceForm
from .decorators import sales_staff_required, inventory_staff_required, branch_manager_required
from apps.orders.models import Order


@login_required
@sales_staff_required
def sales_dashboard(request):
    """
    Sales staff dashboard view showing performance metrics, recent orders,
    and other relevant information for sales staff
    """
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=7)
    
    # Get today's orders count and value
    today_orders = Order.objects.filter(
        created_at__date=today,
        sales_staff=request.user
    )
    today_orders_count = today_orders.count()
    today_orders_value = today_orders.aggregate(total=Sum('total'))['total'] or 0
    
    # Calculate sales target percentage
    current_month = today.strftime('%m/%Y')
    performance = Performance.objects.filter(
        staff__user=request.user, 
        period=current_month
    ).first()
    
    sales_target_percentage = 0
    if performance:
        sales_target_percentage = performance.achievement_percentage
    
    # Get recent orders
    recent_orders = Order.objects.filter(
        sales_staff=request.user
    ).order_by('-created_at')[:5]
    
    # Get top selling products
    top_products = []  # Replace with actual query
    
    # Get branch information
    branch = None
    branch_staff_count = 0
    if hasattr(request.user, 'profile') and request.user.profile.branch:
        branch = request.user.profile.branch
        branch_staff_count = StaffProfile.objects.filter(branch=branch).count()
    
    # Get data for sales chart
    sales_dates = []
    sales_data = []
    for i in range(7):
        date = today - timedelta(days=i)
        sales_dates.insert(0, date.strftime('%d/%m'))
        
        daily_sales = Order.objects.filter(
            created_at__date=date,
            sales_staff=request.user
        ).aggregate(total=Sum('total'))['total'] or 0
        
        sales_data.insert(0, daily_sales)
    
    # New customers in last 7 days
    new_customers_count = Order.objects.filter(
        created_at__date__gte=seven_days_ago,
        sales_staff=request.user
    ).values('customer').distinct().count()
    
    context = {
        'today_orders_count': today_orders_count,
        'today_orders_value': today_orders_value,
        'sales_target_percentage': sales_target_percentage,
        'new_customers_count': new_customers_count,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'branch': branch,
        'branch_staff_count': branch_staff_count,
        'sales_dates': sales_dates,
        'sales_data': sales_data,
    }
    
    return render(request, 'staff/sales_dashboard.html', context)


@login_required
@sales_staff_required
def sales_order_list(request):
    """View to display a list of orders for sales staff"""
    orders = Order.objects.filter(sales_staff=request.user).order_by('-created_at')
    
    # Handle search and filtering
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query) |
            Q(customer__email__icontains=search_query)
        )
        
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    context = {
        'orders': orders,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'staff/sales_order_list.html', context)


@login_required
@sales_staff_required
def sales_order_detail(request, order_id):
    """View để hiển thị chi tiết đơn hàng và cho phép cập nhật trạng thái"""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    }
    
    return render(request, 'staff/sales_order_detail.html', context)


@login_required
@sales_staff_required
def sales_order_create(request):
    """View đã bị vô hiệu hóa - Đơn hàng chỉ được tạo bởi khách hàng"""
    messages.error(request, "Không thể tạo đơn hàng mới. Đơn hàng chỉ được tạo bởi khách hàng khi thanh toán giỏ hàng.")
    return redirect('staff:sales_order_list')


@login_required
@sales_staff_required
def sales_order_update(request, order_id):
    """View cho phép nhân viên bán hàng cập nhật trạng thái đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            
            # Cập nhật thời gian theo trạng thái
            if new_status == 'CONFIRMED' and not order.confirmed_at:
                order.confirmed_at = timezone.now()
            elif new_status == 'SHIPPING' and not order.shipped_at:
                order.shipped_at = timezone.now()
            elif new_status == 'DELIVERED' and not order.delivered_at:
                order.delivered_at = timezone.now()
            elif new_status == 'CANCELLED' and not order.cancelled_at:
                order.cancelled_at = timezone.now()
            
            order.sales_staff = request.user
            order.save()
            
            messages.success(request, f'Trạng thái đơn hàng đã được cập nhật từ {dict(Order.STATUS_CHOICES)[old_status]} sang {dict(Order.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Trạng thái không hợp lệ.')
    
    return redirect('staff:sales_order_detail', order_id=order.id)


@login_required
@sales_staff_required
def sales_customer_list(request):
    """View to display a list of customers for sales staff"""
    # You may need to adjust this query based on your model relationships
    customers = Order.objects.filter(sales_staff=request.user).values('customer').distinct()
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'staff/sales_customer_list.html', context)


@login_required
@sales_staff_required
def sales_customer_detail(request, customer_id):
    """View to display customer details for sales staff"""
    # Implementation depends on your Customer model
    customer = get_object_or_404(User, id=customer_id)  # Replace User with your Customer model
    
    # Get customer's orders processed by the current staff
    customer_orders = Order.objects.filter(customer=customer, sales_staff=request.user)
    
    context = {
        'customer': customer,
        'customer_orders': customer_orders,
    }
    
    return render(request, 'staff/sales_customer_detail.html', context)


@login_required
@sales_staff_required
def sales_customer_create(request):
    """View to create a new customer by sales staff"""
    # Implementation depends on your Customer model and form
    if request.method == 'POST':
        # Process form submission
        pass
    
    context = {
        # Add form and other context data
    }
    
    return render(request, 'staff/sales_customer_form.html', context)


@login_required
@sales_staff_required
def sales_customer_update(request, customer_id):
    """View to update an existing customer by sales staff"""
    # Implementation depends on your Customer model
    customer = get_object_or_404(User, id=customer_id)  # Replace User with your Customer model
    
    if request.method == 'POST':
        # Process form submission
        pass
    
    context = {
        'customer': customer,
    }
    
    return render(request, 'staff/sales_customer_form.html', context)


@login_required
@sales_staff_required
def sales_product_list(request):
    """View to display a list of products for sales staff"""
    # Implementation depends on your Product model
    # products = Product.objects.all()  # Replace with your Product model
    products = []  # Placeholder
    
    context = {
        'products': products,
    }
    
    return render(request, 'staff/sales_product_list.html', context)


@login_required
@sales_staff_required
def sales_product_detail(request, product_id):
    """View to display product details for sales staff"""
    # Implementation depends on your Product model
    # product = get_object_or_404(Product, id=product_id)  # Replace with your Product model
    product = {}  # Placeholder
    
    context = {
        'product': product,
    }
    
    return render(request, 'staff/sales_product_detail.html', context)


@login_required
@sales_staff_required
def sales_reports(request):
    """View to display sales reports for sales staff"""
    context = {}
    return render(request, 'staff/sales_reports.html', context)


@login_required
@sales_staff_required
def sales_daily_report(request):
    """View to display daily sales report for sales staff"""
    today = datetime.now().date()
    
    # Get daily sales data
    daily_sales = Order.objects.filter(
        created_at__date=today,
        sales_staff=request.user
    ).aggregate(
        total_sales=Sum('total'),
        total_orders=Count('id')
    )
    
    context = {
        'daily_sales': daily_sales,
        'date': today,
    }
    
    return render(request, 'staff/sales_daily_report.html', context)


@login_required
@sales_staff_required
def sales_monthly_report(request):
    """View to display monthly sales report for sales staff"""
    today = datetime.now().date()
    first_day = today.replace(day=1)
    
    # Get monthly sales data
    monthly_sales = Order.objects.filter(
        created_at__date__gte=first_day,
        created_at__date__lte=today,
        sales_staff=request.user
    ).aggregate(
        total_sales=Sum('total'),
        total_orders=Count('id')
    )
    
    context = {
        'monthly_sales': monthly_sales,
        'month': today.strftime('%B %Y'),
    }
    
    return render(request, 'staff/sales_monthly_report.html', context)


@login_required
@sales_staff_required
def sales_profile(request):
    """View to display staff profile"""
    # Assuming StaffProfile is related to User via a ForeignKey named 'user'
    profile = get_object_or_404(StaffProfile, user=request.user)
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'staff/sales_profile.html', context)


@login_required
@sales_staff_required
def sales_profile_update(request):
    """View to update staff profile"""
    profile = get_object_or_404(StaffProfile, user=request.user)
    
    if request.method == 'POST':
        # Process form submission
        pass
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'staff/sales_profile_form.html', context)


class ManagerAccessMixin(UserPassesTestMixin):
    """Mixin để kiểm tra quyền truy cập của quản lý"""
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.role == 'MANAGER'
        
    def handle_no_permission(self):
        messages.error(self.request, "Bạn không có quyền truy cập khu vực này.")
        return redirect('products:home')


class StaffListView(LoginRequiredMixin, ManagerAccessMixin, ListView):
    model = StaffProfile
    template_name = 'staff/staff_list.html'
    context_object_name = 'staff_list'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Nếu là quản lý chi nhánh, chỉ hiển thị nhân viên cùng chi nhánh
        if not self.request.user.is_superuser and hasattr(self.request.user, 'profile') and self.request.user.profile.branch:
            queryset = queryset.filter(branch=self.request.user.profile.branch)
        
        # Tìm kiếm
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) | 
                Q(user__last_name__icontains=search_query) |
                Q(staff_id__icontains=search_query)
            )
        
        # Lọc theo vai trò
        role_filter = self.request.GET.get('role', '')
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = dict(StaffProfile.ROLE_CHOICES)
        context['is_admin'] = self.request.user.is_superuser
        return context


class StaffDetailView(LoginRequiredMixin, ManagerAccessMixin, DetailView):
    model = StaffProfile
    template_name = 'staff/staff_detail.html'
    context_object_name = 'staff'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = self.get_object()
        
        # Hiệu suất gần đây
        today = datetime.now()
        current_month = today.strftime('%m/%Y')
        
        context['performance'] = Performance.objects.filter(staff=staff, period=current_month).first()
        
        # Lịch làm việc tuần này
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        
        context['schedules'] = StaffSchedule.objects.filter(
            staff=staff,
            date__gte=start_week,
            date__lte=end_week
        ).order_by('date', 'start_time')
        
        # Đơn hàng gần đây
        context['recent_orders'] = Order.objects.filter(sales_staff=staff.user).order_by('-created_at')[:10]
        
        # Tổng doanh số
        context['total_sales'] = Order.objects.filter(sales_staff=staff.user).aggregate(
            total=Sum('total')
        )['total'] or 0
        
        # Tổng đơn hàng
        context['total_orders'] = Order.objects.filter(sales_staff=staff.user).count()
        
        return context


class StaffCreateView(LoginRequiredMixin, ManagerAccessMixin, CreateView):
    model = StaffProfile
    form_class = StaffProfileForm
    template_name = 'staff/staff_form.html'
    success_url = reverse_lazy('staff:list')
    
    def form_valid(self, form):
        messages.success(self.request, "Nhân viên đã được thêm thành công.")
        return super().form_valid(form)


class StaffUpdateView(LoginRequiredMixin, ManagerAccessMixin, UpdateView):
    model = StaffProfile
    form_class = StaffProfileForm
    template_name = 'staff/staff_form.html'
    
    def get_success_url(self):
        return reverse_lazy('staff:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, "Thông tin nhân viên đã được cập nhật.")
        return super().form_valid(form)


class StaffScheduleCreateView(LoginRequiredMixin, ManagerAccessMixin, CreateView):
    model = StaffSchedule
    form_class = StaffScheduleForm
    template_name = 'staff/schedule_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        staff_id = self.kwargs.get('staff_id')
        kwargs['staff_id'] = staff_id
        return kwargs
    
    def form_valid(self, form):
        staff_id = self.kwargs.get('staff_id')
        form.instance.staff = get_object_or_404(StaffProfile, pk=staff_id)
        messages.success(self.request, "Lịch làm việc đã được thêm.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('staff:detail', kwargs={'pk': self.kwargs.get('staff_id')})


class PerformanceCreateView(LoginRequiredMixin, ManagerAccessMixin, CreateView):
    model = Performance
    form_class = PerformanceForm
    template_name = 'staff/performance_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        staff_id = self.kwargs.get('staff_id')
        kwargs['staff_id'] = staff_id
        return kwargs
    
    def form_valid(self, form):
        staff_id = self.kwargs.get('staff_id')
        form.instance.staff = get_object_or_404(StaffProfile, pk=staff_id)
        messages.success(self.request, "Hiệu suất đã được thêm.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('staff:detail', kwargs={'pk': self.kwargs.get('staff_id')})


# API để lấy dữ liệu hiệu suất cho biểu đồ
def staff_performance_api(request, staff_id):
    """API cung cấp dữ liệu hiệu suất nhân viên cho biểu đồ"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    staff = get_object_or_404(StaffProfile, pk=staff_id)
    
    # Lấy dữ liệu hiệu suất trong 12 tháng gần nhất
    performances = Performance.objects.filter(staff=staff).order_by('-period')[:12]
    
    # Định dạng dữ liệu cho biểu đồ
    performance_data = []
    for perf in performances:
        performance_data.append({
            'period': perf.period,
            'target': float(perf.sales_target),
            'achieved': float(perf.sales_achieved),
            'percentage': float(perf.achievement_percentage),
        })
    
    return JsonResponse({
        'staff_name': staff.user.get_full_name(),
        'performance_data': performance_data
    }) 