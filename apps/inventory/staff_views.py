from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
import json

from apps.products.models import Product, Category
from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem
from apps.branches.models import Branch


@login_required
def dashboard(request):
    """Dashboard của nhân viên kho"""
    branch = request.user.branch
    
    # Tổng số sản phẩm
    total_products = Stock.objects.filter(branch=branch).count()
    
    # Tổng số tồn kho
    total_quantity = Stock.objects.filter(branch=branch).aggregate(
        total=Sum('quantity'))['total'] or 0
    
    # Số sản phẩm sắp hết
    low_stock_count = Stock.objects.filter(
        branch=branch,
        quantity__gt=0,
        quantity__lte=F('min_quantity')
    ).count()
    
    # Số sản phẩm hết hàng
    out_of_stock_count = Stock.objects.filter(
        branch=branch,
        quantity=0
    ).count()
    
    # Danh sách sản phẩm sắp hết hàng
    low_stock_products = Stock.objects.filter(
        branch=branch,
        quantity__lte=F('min_quantity')
    ).select_related('product').order_by('quantity')[:10]
    
    # Hoạt động gần đây
    recent_activities = StockMovement.objects.filter(
        Q(from_branch=branch) | Q(to_branch=branch)
    ).select_related('product', 'staff').order_by('-created_at')[:10]
    
    # Thống kê tồn kho theo danh mục
    category_data = Stock.objects.filter(branch=branch).values(
        'product__category__name'
    ).annotate(
        total=Sum('quantity')
    ).order_by('-total')[:10]
    
    category_names = [item['product__category__name'] or 'Không phân loại' for item in category_data]
    category_quantities = [item['total'] for item in category_data]
    
    context = {
        'total_products': total_products,
        'total_quantity': total_quantity,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_products': low_stock_products,
        'recent_activities': recent_activities,
        'category_names': json.dumps(category_names),
        'category_quantities': json.dumps(category_quantities),
    }
    
    return render(request, 'inventory/dashboard.html', context)


@login_required
def stock_list(request):
    """Danh sách tồn kho"""
    branch = request.user.branch
    
    # Tìm kiếm theo tên sản phẩm, mã SKU
    query = request.GET.get('query', '')
    if query:
        stocks = Stock.objects.filter(
            branch=branch,
            Q(product__name__icontains=query) | 
            Q(product__sku__icontains=query)
        )
    else:
        stocks = Stock.objects.filter(branch=branch)
    
    # Lọc theo danh mục
    category_id = request.GET.get('category', '')
    if category_id:
        stocks = stocks.filter(product__category_id=category_id)
    
    # Lọc theo trạng thái tồn kho
    stock_status = request.GET.get('status', '')
    if stock_status == 'low':
        stocks = stocks.filter(quantity__gt=0, quantity__lte=F('min_quantity'))
    elif stock_status == 'out':
        stocks = stocks.filter(quantity=0)
    elif stock_status == 'ok':
        stocks = stocks.filter(quantity__gt=F('min_quantity'))
    
    # Phân trang
    stocks = stocks.select_related('product', 'product__category').order_by('product__name')
    
    categories = Category.objects.all()
    
    context = {
        'stocks': stocks,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'stock_status': stock_status,
    }
    
    return render(request, 'inventory/stock_list.html', context)


@login_required
def stock_detail(request, pk):
    """Chi tiết tồn kho"""
    branch = request.user.branch
    stock = get_object_or_404(Stock, pk=pk, branch=branch)
    
    # Lịch sử di chuyển của sản phẩm
    movements = StockMovement.objects.filter(
        Q(from_branch=branch) | Q(to_branch=branch),
        product=stock.product
    ).order_by('-created_at')[:20]
    
    context = {
        'stock': stock,
        'movements': movements,
    }
    
    return render(request, 'inventory/stock_detail.html', context)


@login_required
def stock_in_list(request):
    """Danh sách phiếu nhập kho"""
    branch = request.user.branch
    
    stock_in_movements = StockMovement.objects.filter(
        to_branch=branch,
        movement_type='IN'
    ).order_by('-created_at')
    
    context = {
        'stock_in_movements': stock_in_movements,
    }
    
    return render(request, 'inventory/stock_in_list.html', context)


@login_required
def stock_in_create(request):
    """Tạo phiếu nhập kho mới"""
    # Implement form handling here
    return render(request, 'inventory/stock_in_form.html')


@login_required
def stock_in_detail(request, pk):
    """Chi tiết phiếu nhập kho"""
    branch = request.user.branch
    movement = get_object_or_404(StockMovement, pk=pk, to_branch=branch, movement_type='IN')
    
    context = {
        'movement': movement,
    }
    
    return render(request, 'inventory/stock_in_detail.html', context)


@login_required
def stock_out_list(request):
    """Danh sách phiếu xuất kho"""
    branch = request.user.branch
    
    stock_out_movements = StockMovement.objects.filter(
        from_branch=branch,
        movement_type='OUT'
    ).order_by('-created_at')
    
    context = {
        'stock_out_movements': stock_out_movements,
    }
    
    return render(request, 'inventory/stock_out_list.html', context)


@login_required
def stock_out_create(request):
    """Tạo phiếu xuất kho mới"""
    # Implement form handling here
    return render(request, 'inventory/stock_out_form.html')


@login_required
def stock_out_detail(request, pk):
    """Chi tiết phiếu xuất kho"""
    branch = request.user.branch
    movement = get_object_or_404(StockMovement, pk=pk, from_branch=branch, movement_type='OUT')
    
    context = {
        'movement': movement,
    }
    
    return render(request, 'inventory/stock_out_detail.html', context)


@login_required
def transfer_list(request):
    """Danh sách phiếu chuyển kho"""
    branch = request.user.branch
    
    transfers = StockMovement.objects.filter(
        Q(from_branch=branch) | Q(to_branch=branch),
        movement_type='TRANSFER'
    ).order_by('-created_at')
    
    context = {
        'transfers': transfers,
    }
    
    return render(request, 'inventory/transfer_list.html', context)


@login_required
def transfer_create(request):
    """Tạo phiếu chuyển kho mới"""
    # Implement form handling here
    return render(request, 'inventory/transfer_form.html')


@login_required
def transfer_detail(request, pk):
    """Chi tiết phiếu chuyển kho"""
    branch = request.user.branch
    
    # Đầu tiên tìm tất cả các phiếu chuyển kho có movement_type='TRANSFER'
    transfer_movements = StockMovement.objects.filter(
        movement_type='TRANSFER',
        pk=pk
    )
    
    # Sau đó lọc theo chi nhánh
    movement = get_object_or_404(
        transfer_movements.filter(Q(from_branch=branch) | Q(to_branch=branch))
    )
    
    context = {
        'movement': movement,
    }
    
    return render(request, 'inventory/transfer_detail.html', context)


@login_required
def return_list(request):
    """Danh sách phiếu trả hàng"""
    branch = request.user.branch
    
    returns = StockMovement.objects.filter(
        to_branch=branch,
        movement_type='RETURN'
    ).order_by('-created_at')
    
    context = {
        'returns': returns,
    }
    
    return render(request, 'inventory/return_list.html', context)


@login_required
def return_create(request):
    """Tạo phiếu trả hàng mới"""
    # Implement form handling here
    return render(request, 'inventory/return_form.html')


@login_required
def return_detail(request, pk):
    """Chi tiết phiếu trả hàng"""
    branch = request.user.branch
    movement = get_object_or_404(StockMovement, pk=pk, to_branch=branch, movement_type='RETURN')
    
    context = {
        'movement': movement,
    }
    
    return render(request, 'inventory/return_detail.html', context)


@login_required
def movement_list(request):
    """Danh sách tất cả các di chuyển kho"""
    branch = request.user.branch
    
    movements = StockMovement.objects.filter(
        Q(from_branch=branch) | Q(to_branch=branch)
    ).order_by('-created_at')
    
    # Lọc theo loại di chuyển
    movement_type = request.GET.get('type', '')
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    
    # Lọc theo sản phẩm
    product_id = request.GET.get('product', '')
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    # Lọc theo ngày
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    if from_date:
        movements = movements.filter(created_at__date__gte=from_date)
    if to_date:
        movements = movements.filter(created_at__date__lte=to_date)
    
    context = {
        'movements': movements,
        'movement_type': movement_type,
        'product_id': product_id,
        'from_date': from_date,
        'to_date': to_date,
    }
    
    return render(request, 'inventory/movement_list.html', context)


@login_required
def inventory_list(request):
    """Danh sách phiếu kiểm kê"""
    branch = request.user.branch
    
    inventories = Inventory.objects.filter(branch=branch).order_by('-created_at')
    
    context = {
        'inventories': inventories,
    }
    
    return render(request, 'inventory/inventory_list.html', context)


@login_required
def inventory_create(request):
    """Tạo phiếu kiểm kê mới"""
    # Implement form handling here
    return render(request, 'inventory/inventory_form.html')


@login_required
def inventory_detail(request, pk):
    """Chi tiết phiếu kiểm kê"""
    branch = request.user.branch
    inventory = get_object_or_404(Inventory, pk=pk, branch=branch)
    
    inventory_items = InventoryItem.objects.filter(inventory=inventory)
    
    context = {
        'inventory': inventory,
        'inventory_items': inventory_items,
    }
    
    return render(request, 'inventory/inventory_detail.html', context)


@login_required
def inventory_complete(request, pk):
    """Hoàn thành phiếu kiểm kê"""
    branch = request.user.branch
    inventory = get_object_or_404(Inventory, pk=pk, branch=branch)
    
    # Only allow if the inventory is in 'pending' status
    if inventory.status != 'pending':
        messages.error(request, 'Chỉ có thể hoàn thành phiếu kiểm kê đang chờ xử lý.')
        return redirect('inventory_staff:inventory_detail', pk=pk)
    
    if request.method == 'POST':
        inventory.status = 'completed'
        inventory.completed_at = timezone.now()
        inventory.save()
        
        # Update stock quantities based on the inventory
        inventory_items = InventoryItem.objects.filter(inventory=inventory)
        for item in inventory_items:
            stock = Stock.objects.get(product=item.product, branch=branch)
            
            # Create a movement record for the adjustment
            difference = item.actual_quantity - item.expected_quantity
            if difference != 0:
                StockMovement.objects.create(
                    product=item.product,
                    movement_type='ADJUST',
                    quantity=abs(difference),
                    from_branch=branch if difference < 0 else None,
                    to_branch=branch if difference > 0 else None,
                    staff=request.user,
                    notes=f'Điều chỉnh sau kiểm kê #{inventory.inventory_number}'
                )
                
                # Update stock quantity
                stock.quantity = item.actual_quantity
                stock.save()
        
        messages.success(request, f'Đã hoàn thành phiếu kiểm kê #{inventory.inventory_number} và cập nhật tồn kho.')
        return redirect('inventory_staff:inventory_list')
    
    return render(request, 'inventory/inventory_complete.html', {'inventory': inventory}) 