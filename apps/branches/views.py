from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Branch


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