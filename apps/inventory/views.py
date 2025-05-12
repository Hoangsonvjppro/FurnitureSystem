from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, Sum, F, ExpressionWrapper, FloatField, Case, When, Value
from django.db import transaction

from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem
from apps.inventory.forms import StockForm, StockMovementForm, InventoryForm, InventoryItemForm
from apps.products.models import Product, ProductVariant
from apps.branches.models import Branch


class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'inventory/stock_list.html'
    context_object_name = 'stocks'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Tìm kiếm
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(product__sku__icontains=search_query) |
                Q(variant__name__icontains=search_query) |
                Q(variant__sku__icontains=search_query)
            )
        
        # Lọc theo chi nhánh
        branch_id = self.request.GET.get('branch', '')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        elif self.request.user.branch:
            # Mặc định lọc theo chi nhánh của người dùng
            queryset = queryset.filter(branch=self.request.user.branch)
        
        # Lọc theo sản phẩm
        product_id = self.request.GET.get('product', '')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Lọc theo mức tồn kho
        stock_level = self.request.GET.get('stock_level', '')
        if stock_level == 'low':
            queryset = queryset.filter(quantity__lte=F('min_quantity'))
        elif stock_level == 'normal':
            queryset = queryset.filter(quantity__gt=F('min_quantity'), quantity__lt=F('max_quantity'))
        elif stock_level == 'high':
            queryset = queryset.filter(quantity__gte=F('max_quantity'))
        
        # Sắp xếp
        sort_by = self.request.GET.get('sort_by', 'product__name')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thêm thông tin thống kê
        context['total_items'] = self.get_queryset().count()
        context['low_stock_count'] = self.get_queryset().filter(quantity__lte=F('min_quantity')).count()
        context['branches'] = Branch.objects.all()
        
        # Thêm thông tin tìm kiếm
        context['search'] = self.request.GET.get('search', '')
        context['branch_id'] = self.request.GET.get('branch', '')
        context['product_id'] = self.request.GET.get('product', '')
        context['stock_level'] = self.request.GET.get('stock_level', '')
        
        return context


class StockDetailView(LoginRequiredMixin, DetailView):
    model = Stock
    template_name = 'inventory/stock_detail.html'
    context_object_name = 'stock'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thêm thông tin lịch sử chuyển động kho
        context['movements'] = StockMovement.objects.filter(
            product=self.object.product,
            branch=self.object.branch,
            variant=self.object.variant
        ).order_by('-performed_at')[:20]
        
        return context


class StockUpdateView(LoginRequiredMixin, UpdateView):
    model = Stock
    form_class = StockForm
    template_name = 'inventory/stock_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Thông tin tồn kho đã được cập nhật thành công.')
        return response
    
    def get_success_url(self):
        return reverse('inventory:stock_detail', kwargs={'pk': self.object.pk})


class StockMovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = 'inventory/movement_list.html'
    context_object_name = 'movements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Tìm kiếm
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query) |
                Q(product__sku__icontains=search_query) |
                Q(reference__icontains=search_query)
            )
        
        # Lọc theo chi nhánh
        branch_id = self.request.GET.get('branch', '')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        elif self.request.user.branch:
            # Mặc định lọc theo chi nhánh của người dùng
            queryset = queryset.filter(branch=self.request.user.branch)
        
        # Lọc theo loại chuyển động
        movement_type = self.request.GET.get('movement_type', '')
        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)
        
        # Lọc theo ngày
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        if from_date:
            queryset = queryset.filter(performed_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(performed_at__date__lte=to_date)
        
        # Sắp xếp mặc định theo thời gian giảm dần
        queryset = queryset.order_by('-performed_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thêm thông tin thống kê
        context['total_movements'] = self.get_queryset().count()
        context['branches'] = Branch.objects.all()
        context['movement_types'] = dict(StockMovement.MOVEMENT_TYPES)
        
        # Thêm thông tin tìm kiếm
        context['search'] = self.request.GET.get('search', '')
        context['branch_id'] = self.request.GET.get('branch', '')
        context['movement_type'] = self.request.GET.get('movement_type', '')
        
        return context


class StockMovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = 'inventory/movement_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        # Thiết lập giá trị mặc định từ tham số URL nếu có
        product_id = self.request.GET.get('product_id')
        variant_id = self.request.GET.get('variant_id')
        if product_id:
            initial['product'] = product_id
        if variant_id:
            initial['variant'] = variant_id
        if self.request.user.branch:
            initial['branch'] = self.request.user.branch.id
        
        return initial
    
    def form_valid(self, form):
        with transaction.atomic():
            # Lưu thông tin người thực hiện
            form.instance.performed_by = self.request.user
            
            # Xử lý chuyển động kho
            if form.instance.movement_type == 'in':
                # Nhập kho: tăng số lượng
                stock, created = Stock.objects.get_or_create(
                    branch=form.instance.branch,
                    product=form.instance.product,
                    variant=form.instance.variant,
                    defaults={'quantity': 0}
                )
                stock.quantity += form.instance.quantity
                stock.save()
                
            elif form.instance.movement_type == 'out':
                # Xuất kho: giảm số lượng
                stock = get_object_or_404(
                    Stock,
                    branch=form.instance.branch,
                    product=form.instance.product,
                    variant=form.instance.variant
                )
                
                if stock.quantity < form.instance.quantity:
                    form.add_error('quantity', f'Số lượng xuất ({form.instance.quantity}) vượt quá số lượng tồn kho ({stock.quantity}).')
                    return self.form_invalid(form)
                
                stock.quantity -= form.instance.quantity
                stock.save()
                
            elif form.instance.movement_type == 'transfer':
                # Chuyển kho: giảm tại kho nguồn, tăng tại kho đích
                if not form.instance.destination_branch:
                    form.add_error('destination_branch', 'Cần chọn chi nhánh đích cho chuyển kho.')
                    return self.form_invalid(form)
                
                if form.instance.branch == form.instance.destination_branch:
                    form.add_error('destination_branch', 'Chi nhánh đích phải khác chi nhánh nguồn.')
                    return self.form_invalid(form)
                
                # Kiểm tra và giảm tại kho nguồn
                source_stock = get_object_or_404(
                    Stock,
                    branch=form.instance.branch,
                    product=form.instance.product,
                    variant=form.instance.variant
                )
                
                if source_stock.quantity < form.instance.quantity:
                    form.add_error('quantity', f'Số lượng chuyển ({form.instance.quantity}) vượt quá số lượng tồn kho ({source_stock.quantity}).')
                    return self.form_invalid(form)
                
                source_stock.quantity -= form.instance.quantity
                source_stock.save()
                
                # Tăng tại kho đích
                dest_stock, created = Stock.objects.get_or_create(
                    branch=form.instance.destination_branch,
                    product=form.instance.product,
                    variant=form.instance.variant,
                    defaults={'quantity': 0}
                )
                dest_stock.quantity += form.instance.quantity
                dest_stock.save()
                
            elif form.instance.movement_type == 'adjustment':
                # Điều chỉnh: cập nhật trực tiếp số lượng
                stock, created = Stock.objects.get_or_create(
                    branch=form.instance.branch,
                    product=form.instance.product,
                    variant=form.instance.variant,
                    defaults={'quantity': 0}
                )
                
                if form.instance.quantity < 0 and abs(form.instance.quantity) > stock.quantity:
                    form.add_error('quantity', f'Số lượng điều chỉnh ({form.instance.quantity}) không hợp lệ. Tồn kho hiện tại: {stock.quantity}')
                    return self.form_invalid(form)
                
                stock.quantity += form.instance.quantity
                stock.save()
            
            # Lưu chuyển động kho
            response = super().form_valid(form)
            
            messages.success(self.request, f'Chuyển động kho đã được tạo thành công.')
            return response
    
    def get_success_url(self):
        return reverse('inventory:movement_list')


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = 'inventory/inventory_list.html'
    context_object_name = 'inventories'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Lọc theo chi nhánh
        branch_id = self.request.GET.get('branch', '')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        elif self.request.user.branch:
            # Mặc định lọc theo chi nhánh của người dùng
            queryset = queryset.filter(branch=self.request.user.branch)
        
        # Lọc theo trạng thái
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Sắp xếp
        queryset = queryset.order_by('-inventory_date')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = Inventory
    template_name = 'inventory/inventory_detail.html'
    context_object_name = 'inventory'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all()
        
        # Tính toán tổng chênh lệch
        total_discrepancy = sum(item.difference for item in context['items'])
        context['total_discrepancy'] = total_discrepancy
        
        return context


class InventoryCreateView(LoginRequiredMixin, CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = 'inventory/inventory_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.branch:
            initial['branch'] = self.request.user.branch.id
        return initial
    
    def form_valid(self, form):
        with transaction.atomic():
            form.instance.created_by = self.request.user
            inventory = form.save()
            
            # Tự động tạo các item kiểm kê dựa trên tồn kho hiện tại của chi nhánh
            stocks = Stock.objects.filter(branch=inventory.branch)
            for stock in stocks:
                InventoryItem.objects.create(
                    inventory=inventory,
                    product=stock.product,
                    variant=stock.variant,
                    expected_quantity=stock.quantity,
                    actual_quantity=0  # Mặc định 0, sẽ được cập nhật khi kiểm kê
                )
            
            messages.success(self.request, f'Đợt kiểm kê mới đã được tạo thành công. Vui lòng cập nhật số lượng thực tế cho từng sản phẩm.')
            return redirect('inventory:inventory_detail', pk=inventory.pk)


@login_required
def update_inventory_item(request, inventory_id, item_id):
    """Cập nhật số lượng thực tế của một item kiểm kê"""
    inventory = get_object_or_404(Inventory, pk=inventory_id)
    item = get_object_or_404(InventoryItem, pk=item_id, inventory=inventory)
    
    if request.method == 'POST':
        actual_quantity = request.POST.get('actual_quantity')
        try:
            actual_quantity = int(actual_quantity)
            if actual_quantity < 0:
                messages.error(request, 'Số lượng thực tế không được âm.')
            else:
                item.actual_quantity = actual_quantity
                item.save()
                messages.success(request, f'Đã cập nhật số lượng thực tế cho {item.product.name}.')
        except ValueError:
            messages.error(request, 'Số lượng không hợp lệ.')
    
    return redirect('inventory:inventory_detail', pk=inventory_id)


@login_required
def complete_inventory(request, pk):
    """Hoàn thành đợt kiểm kê và tự động điều chỉnh tồn kho"""
    inventory = get_object_or_404(Inventory, pk=pk)
    
    if inventory.status == 'completed':
        messages.warning(request, 'Đợt kiểm kê này đã được hoàn thành.')
        return redirect('inventory:inventory_detail', pk=pk)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Cập nhật trạng thái kiểm kê
            inventory.status = 'completed'
            inventory.completed_at = timezone.now()
            inventory.save()
            
            # Tự động điều chỉnh tồn kho dựa trên kết quả kiểm kê
            for item in inventory.items.all():
                if item.difference != 0:
                    # Tạo chuyển động kho điều chỉnh
                    StockMovement.objects.create(
                        product=item.product,
                        variant=item.variant,
                        branch=inventory.branch,
                        movement_type='adjustment',
                        quantity=item.difference,  # Có thể âm hoặc dương
                        reference=f'Điều chỉnh từ kiểm kê #{inventory.id}',
                        notes=f'Chênh lệch: {item.difference}. Dự kiến: {item.expected_quantity}, Thực tế: {item.actual_quantity}',
                        performed_by=request.user,
                        performed_at=inventory.completed_at
                    )
                    
                    # Cập nhật số lượng tồn kho
                    stock = Stock.objects.get(
                        product=item.product,
                        variant=item.variant,
                        branch=inventory.branch
                    )
                    stock.quantity = item.actual_quantity
                    stock.save()
            
            messages.success(request, 'Đợt kiểm kê đã được hoàn thành và tồn kho đã được điều chỉnh theo kết quả kiểm kê.')
    
    return redirect('inventory:inventory_detail', pk=pk) 