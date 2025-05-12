from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, Sum, F, Value, Count
from django.db import transaction

from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.suppliers.forms import SupplierForm, PurchaseOrderForm, PurchaseOrderItemFormSet
from apps.products.models import Product, ProductVariant
from apps.inventory.models import StockMovement


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'suppliers/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Tìm kiếm
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(contact_person__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Lọc theo trạng thái
        is_active = self.request.GET.get('is_active', '')
        if is_active:
            is_active_bool = is_active == 'True'
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Sắp xếp
        sort_by = self.request.GET.get('sort_by', 'name')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_suppliers'] = self.model.objects.count()
        context['active_suppliers'] = self.model.objects.filter(is_active=True).count()
        
        # Thêm thông tin tìm kiếm
        context['search'] = self.request.GET.get('search', '')
        context['is_active'] = self.request.GET.get('is_active', '')
        
        return context


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'suppliers/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thêm danh sách đơn hàng nhập gần đây từ nhà cung cấp này
        context['purchase_orders'] = PurchaseOrder.objects.filter(
            supplier=self.object
        ).order_by('-created_at')[:10]
        
        # Thống kê tổng giá trị đã nhập từ nhà cung cấp này
        context['total_purchased'] = PurchaseOrder.objects.filter(
            supplier=self.object,
            status__in=['confirmed', 'received']
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Thống kê số lượng sản phẩm đã nhập từ nhà cung cấp này
        context['product_count'] = PurchaseOrderItem.objects.filter(
            purchase_order__supplier=self.object
        ).values('product').distinct().count()
        
        return context


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    success_url = reverse_lazy('suppliers:supplier_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Nhà cung cấp {self.object.name} đã được tạo thành công.')
        return response


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'suppliers/supplier_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Thông tin nhà cung cấp {self.object.name} đã được cập nhật.')
        return response
    
    def get_success_url(self):
        return reverse('suppliers:supplier_detail', kwargs={'pk': self.object.pk})


class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'suppliers/purchase_order_list.html'
    context_object_name = 'purchase_orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Tìm kiếm
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query) |
                Q(supplier__name__icontains=search_query)
            )
        
        # Lọc theo nhà cung cấp
        supplier_id = self.request.GET.get('supplier', '')
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        
        # Lọc theo trạng thái
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Lọc theo chi nhánh
        branch_id = self.request.GET.get('branch', '')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        elif self.request.user.branch:
            queryset = queryset.filter(branch=self.request.user.branch)
        
        # Lọc theo ngày
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        if from_date:
            queryset = queryset.filter(order_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(order_date__lte=to_date)
        
        # Sắp xếp
        sort_by = self.request.GET.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thống kê theo trạng thái
        context['draft_count'] = PurchaseOrder.objects.filter(status='draft').count()
        context['pending_count'] = PurchaseOrder.objects.filter(status='pending').count()
        context['confirmed_count'] = PurchaseOrder.objects.filter(status='confirmed').count()
        context['received_count'] = PurchaseOrder.objects.filter(status='received').count()
        
        # Danh sách nhà cung cấp cho dropdown lọc
        context['suppliers'] = Supplier.objects.filter(is_active=True)
        
        # Thêm thông tin tìm kiếm
        context['search'] = self.request.GET.get('search', '')
        context['status'] = self.request.GET.get('status', '')
        context['supplier_id'] = self.request.GET.get('supplier', '')
        context['branch_id'] = self.request.GET.get('branch', '')
        
        return context


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'suppliers/purchase_order_detail.html'
    context_object_name = 'purchase_order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Danh sách các item trong đơn hàng
        context['items'] = self.object.items.all()
        
        # Thêm lựa chọn cập nhật trạng thái
        context['status_choices'] = self.model.STATUS_CHOICES
        
        return context


class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'suppliers/purchase_order_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['items_formset'] = PurchaseOrderItemFormSet(self.request.POST, prefix='items')
        else:
            context['items_formset'] = PurchaseOrderItemFormSet(prefix='items')
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['items_formset']
        
        with transaction.atomic():
            # Lưu thông tin người tạo
            form.instance.created_by = self.request.user
            
            # Thiết lập chi nhánh mặc định nếu không chọn
            if not form.instance.branch and self.request.user.branch:
                form.instance.branch = self.request.user.branch
            
            # Lưu đơn hàng
            purchase_order = form.save()
            
            # Kiểm tra và lưu các item
            if formset.is_valid():
                formset.instance = purchase_order
                items = formset.save(commit=False)
                
                # Tính tổng tiền
                total_amount = 0
                for item in items:
                    item.purchase_order = purchase_order
                    item.save()
                    total_amount += item.unit_price * item.quantity
                
                # Cập nhật tổng tiền
                purchase_order.total_amount = total_amount
                purchase_order.save()
                
                messages.success(self.request, f'Đơn hàng nhập #{purchase_order.order_number} đã được tạo thành công.')
                return redirect('suppliers:purchase_order_detail', pk=purchase_order.pk)
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('suppliers:purchase_order_detail', kwargs={'pk': self.object.pk})


class PurchaseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = 'suppliers/purchase_order_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['items_formset'] = PurchaseOrderItemFormSet(self.request.POST, prefix='items', instance=self.object)
        else:
            context['items_formset'] = PurchaseOrderItemFormSet(prefix='items', instance=self.object)
        
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['items_formset']
        
        # Chỉ cho phép cập nhật nếu đơn hàng ở trạng thái nháp hoặc chờ xác nhận
        if self.object.status not in ['draft', 'pending']:
            messages.error(self.request, f'Đơn hàng #{self.object.order_number} không thể cập nhật vì đã được xác nhận hoặc nhận hàng.')
            return redirect('suppliers:purchase_order_detail', pk=self.object.pk)
        
        with transaction.atomic():
            # Lưu đơn hàng
            purchase_order = form.save()
            
            # Kiểm tra và lưu các item
            if formset.is_valid():
                formset.instance = purchase_order
                items = formset.save(commit=False)
                
                # Kiểm tra các item đã xóa
                for obj in formset.deleted_objects:
                    obj.delete()
                
                # Lưu các item và tính tổng tiền
                total_amount = 0
                for item in items:
                    item.purchase_order = purchase_order
                    item.save()
                    total_amount += item.unit_price * item.quantity
                
                # Cập nhật tổng tiền
                purchase_order.total_amount = total_amount
                purchase_order.save()
                
                messages.success(self.request, f'Đơn hàng nhập #{purchase_order.order_number} đã được cập nhật thành công.')
                return redirect('suppliers:purchase_order_detail', pk=purchase_order.pk)
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('suppliers:purchase_order_detail', kwargs={'pk': self.object.pk})


@login_required
def update_purchase_order_status(request, pk):
    """Cập nhật trạng thái đơn hàng nhập"""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(PurchaseOrder.STATUS_CHOICES):
            old_status = purchase_order.status
            purchase_order.status = new_status
            
            # Xử lý các trường hợp đặc biệt
            if new_status == 'received' and not purchase_order.received_date:
                purchase_order.received_date = timezone.now().date()
                
                # Khi nhận hàng, tự động cập nhật tồn kho
                with transaction.atomic():
                    for item in purchase_order.items.all():
                        # Cập nhật số lượng đã nhận
                        item.received_quantity = item.quantity
                        item.save()
                        
                        # Tạo chuyển động kho nhập hàng
                        StockMovement.objects.create(
                            product=item.product,
                            variant=item.variant,
                            branch=purchase_order.branch,
                            movement_type='in',
                            quantity=item.quantity,
                            reference=f"PO#{purchase_order.order_number}",
                            notes=f"Nhập hàng từ {purchase_order.supplier.name}",
                            performed_by=request.user,
                            performed_at=timezone.now()
                        )
            
            purchase_order.save()
            
            messages.success(request, f'Trạng thái đơn hàng đã được cập nhật từ {dict(PurchaseOrder.STATUS_CHOICES)[old_status]} sang {dict(PurchaseOrder.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Trạng thái không hợp lệ.')
    
    return redirect('suppliers:purchase_order_detail', pk=pk) 