from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, Sum, F, ExpressionWrapper, FloatField, Case, When, Value, Count
from django.db import transaction

from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem
from apps.inventory.forms import StockForm, StockMovementForm, InventoryForm, InventoryItemForm
from apps.products.models import Product, ProductVariant
from apps.branches.models import Branch


@login_required
def inventory_dashboard(request):
    """Dashboard view for inventory staff"""
    today = timezone.now().date()
    
    # Get counts for today's stock movements
    stock_ins_today = StockMovement.objects.filter(
        created_at__date=today,
        movement_type='IN'
    ).count()
    
    stock_outs_today = StockMovement.objects.filter(
        created_at__date=today,
        movement_type='OUT'
    ).count()
    
    # Total products count
    total_products = Stock.objects.values('product').distinct().count()
    
    # Low stock items
    low_stock_count = Stock.objects.filter(quantity__lte=F('min_quantity')).count()
    low_stock_products = Stock.objects.filter(quantity__lte=F('min_quantity')).select_related('product', 'variant', 'branch')[:10]
    
    # Pending orders that need to be fulfilled
    # Adjust this query based on your actual model relationships
    pending_orders = []  # Replace with actual query
    
    # Get inventory by category for chart
    category_data = Stock.objects.values('product__category__name').annotate(
        count=Count('id'),
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')
    
    category_names = [item['product__category__name'] for item in category_data]
    category_counts = [item['total_quantity'] for item in category_data]
    
    # Recent activities (stock movements)
    recent_activities = StockMovement.objects.all().order_by('-created_at')[:10]
    
    for activity in recent_activities:
        # Assign icon and color based on movement type
        if activity.movement_type == 'IN':
            activity.icon = 'fa-truck-loading'
            activity.type_color = 'success'
        elif activity.movement_type == 'OUT':
            activity.icon = 'fa-shipping-fast'
            activity.type_color = 'primary'
        elif activity.movement_type == 'TRANSFER':
            activity.icon = 'fa-exchange-alt'
            activity.type_color = 'info'
        elif activity.movement_type == 'ADJUSTMENT':
            activity.icon = 'fa-clipboard-check'
            activity.type_color = 'warning'
        else:
            activity.icon = 'fa-box'
            activity.type_color = 'secondary'
    
    context = {
        'total_products': total_products,
        'stock_ins_today': stock_ins_today,
        'stock_outs_today': stock_outs_today,
        'low_stock_count': low_stock_count,
        'low_stock_products': low_stock_products,
        'pending_orders': pending_orders,
        'recent_activities': recent_activities,
        'category_names': category_names,
        'category_counts': category_counts,
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
def stock_list(request):
    """View for listing all stock items"""
    stock_items = Stock.objects.all()
    
    # Add filtering logic if needed
    search_query = request.GET.get('search', '')
    if search_query:
        stock_items = stock_items.filter(
            Q(product__name__icontains=search_query) |
            Q(product__sku__icontains=search_query)
        )
    
    context = {
        'stock_items': stock_items,
        'search_query': search_query
    }
    
    return render(request, 'inventory/stock_list.html', context)


@login_required
def stock_detail(request, stock_id):
    """View for showing stock details"""
    stock = get_object_or_404(Stock, id=stock_id)
    
    # Get stock movement history
    movements = StockMovement.objects.filter(
        product=stock.product,
        branch=stock.branch
    ).order_by('-created_at')[:20]
    
    context = {
        'stock': stock,
        'movements': movements
    }
    
    return render(request, 'inventory/stock_detail.html', context)


@login_required
def stock_update(request, stock_id):
    """View for updating stock details"""
    stock = get_object_or_404(Stock, id=stock_id)
    
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock information updated successfully.')
            return redirect('inventory:stock_detail', stock_id=stock.id)
    else:
        form = StockForm(instance=stock)
    
    context = {
        'form': form,
        'stock': stock
    }
    
    return render(request, 'inventory/stock_form.html', context)


@login_required
def low_stock(request):
    """View for showing low stock items"""
    low_stock_items = Stock.objects.filter(quantity__lte=F('min_quantity'))
    
    context = {
        'low_stock_items': low_stock_items
    }
    
    return render(request, 'inventory/low_stock.html', context)


@login_required
def receiving_list(request):
    """View for listing receiving/stock-in records"""
    receiving_items = StockMovement.objects.filter(movement_type='IN').order_by('-created_at')
    
    context = {
        'receiving_items': receiving_items
    }
    
    return render(request, 'inventory/receiving_list.html', context)


@login_required
def receiving_create(request):
    """View for creating new receiving/stock-in record"""
    if request.method == 'POST':
        # Process form
        pass
    
    context = {}
    
    return render(request, 'inventory/receiving_form.html', context)


@login_required
def receiving_detail(request, receiving_id):
    """View for showing receiving/stock-in details"""
    movement = get_object_or_404(StockMovement, id=receiving_id, movement_type='IN')
    
    context = {
        'movement': movement
    }
    
    return render(request, 'inventory/receiving_detail.html', context)


@login_required
def receiving_update(request, receiving_id):
    """View for updating receiving/stock-in record"""
    movement = get_object_or_404(StockMovement, id=receiving_id, movement_type='IN')
    
    if request.method == 'POST':
        # Process form
        pass
    
    context = {
        'movement': movement
    }
    
    return render(request, 'inventory/receiving_form.html', context)


@login_required
def receiving_complete(request, receiving_id):
    """View for completing receiving/stock-in process"""
    movement = get_object_or_404(StockMovement, id=receiving_id, movement_type='IN')
    
    # Process completion logic
    
    return redirect('inventory:receiving_detail', receiving_id=receiving_id)


@login_required
def shipping_list(request):
    """View for listing shipping/stock-out records"""
    shipping_items = StockMovement.objects.filter(movement_type='OUT').order_by('-created_at')
    
    context = {
        'shipping_items': shipping_items
    }
    
    return render(request, 'inventory/shipping_list.html', context)


@login_required
def shipping_create(request):
    """View for creating new shipping/stock-out record"""
    if request.method == 'POST':
        # Process form
        pass
    
    context = {}
    
    return render(request, 'inventory/shipping_form.html', context)


@login_required
def shipping_detail(request, shipping_id):
    """View for showing shipping/stock-out details"""
    movement = get_object_or_404(StockMovement, id=shipping_id, movement_type='OUT')
    
    context = {
        'movement': movement
    }
    
    return render(request, 'inventory/shipping_detail.html', context)


@login_required
def shipping_update(request, shipping_id):
    """View for updating shipping/stock-out record"""
    movement = get_object_or_404(StockMovement, id=shipping_id, movement_type='OUT')
    
    if request.method == 'POST':
        # Process form
        pass
    
    context = {
        'movement': movement
    }
    
    return render(request, 'inventory/shipping_form.html', context)


@login_required
def shipping_complete(request, shipping_id):
    """View for completing shipping/stock-out process"""
    movement = get_object_or_404(StockMovement, id=shipping_id, movement_type='OUT')
    
    # Process completion logic
    
    return redirect('inventory:shipping_detail', shipping_id=shipping_id)


@login_required
def transfer_list(request):
    """View for listing transfer records"""
    transfer_items = StockMovement.objects.filter(movement_type='TRANSFER').order_by('-created_at')
    
    context = {
        'transfer_items': transfer_items
    }
    
    return render(request, 'inventory/transfer_list.html', context)


@login_required
def transfer_create(request):
    """View for creating new transfer record"""
    if request.method == 'POST':
        # Process form
        pass
    
    context = {}
    
    return render(request, 'inventory/transfer_form.html', context)


@login_required
def transfer_detail(request, transfer_id):
    """View for showing transfer details"""
    movement = get_object_or_404(StockMovement, id=transfer_id, movement_type='TRANSFER')
    
    context = {
        'movement': movement
    }
    
    return render(request, 'inventory/transfer_detail.html', context)


@login_required
def transfer_update(request, transfer_id):
    """View for updating transfer record"""
    movement = get_object_or_404(StockMovement, id=transfer_id, movement_type='TRANSFER')
    
    if request.method == 'POST':
        # Process form
        pass
    
    context = {
        'movement': movement
    }
    
    return render(request, 'inventory/transfer_form.html', context)


@login_required
def transfer_complete(request, transfer_id):
    """View for completing transfer process"""
    movement = get_object_or_404(StockMovement, id=transfer_id, movement_type='TRANSFER')
    
    # Process completion logic
    
    return redirect('inventory:transfer_detail', transfer_id=transfer_id)


@login_required
def inventory_audit(request):
    """View for inventory audit list"""
    audits = Inventory.objects.all().order_by('-created_at')
    
    context = {
        'audits': audits
    }
    
    return render(request, 'inventory/audit_list.html', context)


@login_required
def audit_create(request):
    """View for creating new audit"""
    if request.method == 'POST':
        # Process form
        pass
    
    context = {}
    
    return render(request, 'inventory/audit_form.html', context)


@login_required
def audit_detail(request, audit_id):
    """View for showing audit details"""
    audit = get_object_or_404(Inventory, id=audit_id)
    
    context = {
        'audit': audit
    }
    
    return render(request, 'inventory/audit_detail.html', context)


@login_required
def audit_update(request, audit_id):
    """View for updating audit"""
    audit = get_object_or_404(Inventory, id=audit_id)
    
    if request.method == 'POST':
        # Process form
        pass
    
    context = {
        'audit': audit
    }
    
    return render(request, 'inventory/audit_form.html', context)


@login_required
def audit_complete(request, audit_id):
    """View for completing audit process"""
    audit = get_object_or_404(Inventory, id=audit_id)
    
    # Process completion logic
    
    return redirect('inventory:audit_detail', audit_id=audit_id)


@login_required
def inventory_reports(request):
    """View for inventory reports"""
    context = {}
    
    return render(request, 'inventory/reports.html', context)


@login_required
def movement_report(request):
    """View for inventory movement report"""
    movements = StockMovement.objects.all().order_by('-created_at')
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        movements = movements.filter(created_at__date__gte=start_date)
    if end_date:
        movements = movements.filter(created_at__date__lte=end_date)
    
    context = {
        'movements': movements,
        'start_date': start_date,
        'end_date': end_date
    }
    
    return render(request, 'inventory/movement_report.html', context)


@login_required
def turnover_report(request):
    """View for inventory turnover report"""
    # Calculate turnover for products
    
    context = {}
    
    return render(request, 'inventory/turnover_report.html', context)


@login_required
def staff_profile(request):
    """View for staff profile"""
    context = {}
    
    return render(request, 'inventory/staff_profile.html', context)


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
        ).order_by('-created_at')[:20]
        
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
            queryset = queryset.filter(created_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)
        
        # Sắp xếp mặc định theo thời gian giảm dần
        queryset = queryset.order_by('-created_at')
        
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
            if form.instance.movement_type == 'IN':
                # Nhập kho: tăng số lượng
                stock, created = Stock.objects.get_or_create(
                    branch=form.instance.branch,
                    product=form.instance.product,
                    variant=form.instance.variant,
                    defaults={'quantity': 0}
                )
                stock.quantity += form.instance.quantity
                stock.save()
                
            elif form.instance.movement_type == 'OUT':
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
                
            elif form.instance.movement_type == 'TRANSFER':
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
                
            elif form.instance.movement_type == 'ADJUSTMENT':
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
        queryset = queryset.order_by('-created_at')
        
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
                        movement_type='ADJUSTMENT',
                        quantity=item.difference,  # Có thể âm hoặc dương
                        reference=f'Điều chỉnh từ kiểm kê #{inventory.id}',
                        notes=f'Chênh lệch: {item.difference}. Dự kiến: {item.expected_quantity}, Thực tế: {item.actual_quantity}',
                        staff=request.user,
                        created_at=inventory.completed_at
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