from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import StaffProfile, StaffSchedule, Performance
from .forms import StaffProfileForm, StaffScheduleForm, PerformanceForm
from apps.orders.models import Order


class ManagerAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or hasattr(self.request.user, 'profile') and self.request.user.profile.is_manager


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
        context['recent_orders'] = Order.objects.filter(staff=staff.user).order_by('-created_at')[:10]
        
        # Tổng doanh số
        context['total_sales'] = Order.objects.filter(staff=staff.user).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Tổng đơn hàng
        context['total_orders'] = Order.objects.filter(staff=staff.user).count()
        
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