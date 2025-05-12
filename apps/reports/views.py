from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import xlsxwriter
import io
import json

from .models import Report, ScheduledReport, ReportExecution
from apps.orders.models import Order, OrderItem
from apps.inventory.models import Inventory, InventoryItem
from apps.products.models import Product
from apps.branches.models import Branch
from apps.suppliers.models import Supplier, PurchaseOrder

# Kiểm tra quyền xem báo cáo
class ReportAccessMixin(UserPassesTestMixin):
    def test_func(self):
        # Admin, quản lý và nhân viên bán hàng có quyền xem báo cáo
        return self.request.user.is_superuser or hasattr(self.request.user, 'profile') and (
            self.request.user.profile.is_manager or self.request.user.profile.is_sales_staff
        )


# Trang dashboard báo cáo
class ReportDashboardView(LoginRequiredMixin, ReportAccessMixin, ListView):
    template_name = 'reports/reports_dashboard.html'
    model = Report
    context_object_name = 'reports'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Nếu là admin hoặc quản lý, hiển thị tất cả báo cáo
        if self.request.user.is_superuser or (hasattr(self.request.user, 'profile') and self.request.user.profile.is_manager):
            branch = None
        # Nếu là nhân viên, chỉ hiển thị báo cáo của chi nhánh
        elif hasattr(self.request.user, 'profile') and self.request.user.profile.branch:
            branch = self.request.user.profile.branch
        else:
            branch = None
        
        # Thời gian
        today = datetime.now().date()
        start_of_month = datetime(today.year, today.month, 1).date()
        start_of_year = datetime(today.year, 1, 1).date()
        
        # Báo cáo doanh số
        if branch:
            orders = Order.objects.filter(branch=branch)
        else:
            orders = Order.objects.all()
        
        # Doanh số theo thời gian
        daily_sales = orders.filter(created_at__date=today).aggregate(
            amount=Sum('total_amount'),
            count=Count('id')
        )
        monthly_sales = orders.filter(created_at__date__gte=start_of_month).aggregate(
            amount=Sum('total_amount'),
            count=Count('id')
        )
        yearly_sales = orders.filter(created_at__date__gte=start_of_year).aggregate(
            amount=Sum('total_amount'),
            count=Count('id')
        )
        
        # Báo cáo tồn kho
        if branch:
            inventory_items = InventoryItem.objects.filter(inventory__branch=branch)
        else:
            inventory_items = InventoryItem.objects.all()
        
        # Giá trị tồn kho
        inventory_value = inventory_items.aggregate(
            total_value=Sum(F('quantity') * F('product__price')),
            total_items=Sum('quantity'),
            product_count=Count('product', distinct=True)
        )
        
        # Sản phẩm bán chạy (top 5)
        top_products = OrderItem.objects.values('product__name'
        ).annotate(
            quantity=Sum('quantity'),
            revenue=Sum(F('quantity') * F('unit_price'))
        ).order_by('-quantity')[:5]
        
        # Dữ liệu cho biểu đồ
        last_30_days = [(today - timedelta(days=i)).isoformat() for i in range(30, -1, -1)]
        
        sales_data = {}
        for day in last_30_days:
            sales_data[day] = 0
        
        # Lấy dữ liệu doanh số 30 ngày qua
        daily_data = orders.filter(
            created_at__date__gte=today - timedelta(days=30)
        ).values('created_at__date').annotate(
            daily_total=Sum('total_amount')
        )
        
        for item in daily_data:
            date_str = item['created_at__date'].isoformat()
            if date_str in sales_data:
                sales_data[date_str] = float(item['daily_total'])
        
        # Dữ liệu cho biểu đồ hình tròn về danh mục sản phẩm
        category_data = OrderItem.objects.values(
            'product__category__name'
        ).annotate(
            value=Sum(F('quantity') * F('unit_price'))
        ).order_by('-value')[:5]
        
        context.update({
            'daily_sales': daily_sales,
            'monthly_sales': monthly_sales,
            'yearly_sales': yearly_sales,
            'inventory_value': inventory_value,
            'top_products': top_products,
            'sales_chart_data': json.dumps(list(sales_data.items())),
            'category_data': list(category_data),
            'is_admin': self.request.user.is_superuser,
            'is_manager': hasattr(self.request.user, 'profile') and self.request.user.profile.is_manager,
        })
        
        return context


# API lấy dữ liệu báo cáo
def report_data_api(request, report_type):
    """API cung cấp dữ liệu cho báo cáo"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    if report_type == 'sales':
        # Thông số
        period = request.GET.get('period', 'monthly')  # daily, weekly, monthly, yearly
        branch_id = request.GET.get('branch', None)
        
        # Lọc theo chi nhánh
        if branch_id:
            orders = Order.objects.filter(branch_id=branch_id)
        else:
            orders = Order.objects.all()
        
        # Lọc theo thời gian
        today = timezone.now().date()
        if period == 'daily':
            start_date = today
        elif period == 'weekly':
            start_date = today - timedelta(days=7)
        elif period == 'monthly':
            start_date = today.replace(day=1)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
        else:
            start_date = today - timedelta(days=30)
        
        orders = orders.filter(created_at__date__gte=start_date)
        
        # Tính tổng số
        total_sales = orders.aggregate(
            total=Sum('total_amount'),
            count=Count('id')
        )
        
        # Dữ liệu chi tiết
        if period == 'daily':
            sales_by_hour = orders.extra(
                select={'hour': "EXTRACT(hour FROM created_at)"}
            ).values('hour').annotate(
                amount=Sum('total_amount'),
                count=Count('id')
            ).order_by('hour')
            
            return JsonResponse({
                'total': total_sales,
                'details': list(sales_by_hour)
            })
        else:
            sales_by_day = orders.values('created_at__date').annotate(
                amount=Sum('total_amount'),
                count=Count('id')
            ).order_by('created_at__date')
            
            return JsonResponse({
                'total': total_sales,
                'details': list(sales_by_day)
            })
    
    elif report_type == 'inventory':
        branch_id = request.GET.get('branch', None)
        category_id = request.GET.get('category', None)
        low_stock_only = request.GET.get('low_stock', False)
        
        # Base query
        query = InventoryItem.objects.select_related('product', 'inventory')
        
        # Filters
        if branch_id:
            query = query.filter(inventory__branch_id=branch_id)
        
        if category_id:
            query = query.filter(product__category_id=category_id)
        
        if low_stock_only:
            query = query.filter(quantity__lte=F('product__low_stock_threshold'))
        
        # Aggregated data
        inventory_summary = query.aggregate(
            total_items=Sum('quantity'),
            total_value=Sum(F('quantity') * F('product__price')),
            average_value=Avg(F('quantity') * F('product__price'))
        )
        
        # Detailed data
        inventory_by_product = query.values(
            'product__name',
            'product__sku',
            'quantity'
        ).annotate(
            value=F('quantity') * F('product__price')
        ).order_by('-quantity')[:50]  # Limit to 50 products
        
        return JsonResponse({
            'summary': inventory_summary,
            'by_product': list(inventory_by_product)
        })
    
    return JsonResponse({'error': 'Invalid report type'}, status=400)


# Export báo cáo sang Excel
def export_report(request, report_type):
    """Xuất báo cáo ra file Excel"""
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)
    
    # Tạo file Excel trong bộ nhớ
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Định dạng
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#4F81BD',
        'color': 'white',
        'border': 1
    })
    
    # Báo cáo doanh số
    if report_type == 'sales':
        period = request.GET.get('period', 'monthly')
        branch_id = request.GET.get('branch', None)
        
        # Filter
        if branch_id:
            branch = get_object_or_404(Branch, id=branch_id)
            branch_name = branch.name
            orders = Order.objects.filter(branch_id=branch_id)
        else:
            branch_name = "Tất cả chi nhánh"
            orders = Order.objects.all()
        
        # Period filter
        today = timezone.now().date()
        if period == 'daily':
            start_date = today
            title = f"BÁO CÁO DOANH SỐ NGÀY {today.strftime('%d/%m/%Y')}"
        elif period == 'weekly':
            start_date = today - timedelta(days=7)
            title = f"BÁO CÁO DOANH SỐ TUẦN ({start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')})"
        elif period == 'monthly':
            start_date = today.replace(day=1)
            title = f"BÁO CÁO DOANH SỐ THÁNG {today.strftime('%m/%Y')}"
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
            title = f"BÁO CÁO DOANH SỐ NĂM {today.year}"
        else:
            start_date = today - timedelta(days=30)
            title = f"BÁO CÁO DOANH SỐ 30 NGÀY ({start_date.strftime('%d/%m/%Y')} - {today.strftime('%d/%m/%Y')})"
        
        orders = orders.filter(created_at__date__gte=start_date)
        
        # Header
        worksheet.write(0, 0, title, header_format)
        worksheet.merge_range('A1:G1', title, header_format)
        worksheet.write(2, 0, f"Chi nhánh: {branch_name}")
        worksheet.write(3, 0, f"Ngày xuất báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Table header
        headers = ["Mã đơn hàng", "Ngày tạo", "Khách hàng", "Nhân viên", "Số sản phẩm", "Tổng tiền", "Trạng thái"]
        for col, header in enumerate(headers):
            worksheet.write(5, col, header, header_format)
        
        # Data
        row = 6
        for order in orders:
            worksheet.write(row, 0, order.order_number)
            worksheet.write(row, 1, order.created_at.strftime('%d/%m/%Y %H:%M'))
            worksheet.write(row, 2, order.customer.get_full_name() if order.customer else "Khách lẻ")
            worksheet.write(row, 3, order.staff.get_full_name() if order.staff else "Online")
            worksheet.write(row, 4, order.items.aggregate(total=Sum('quantity'))['total'] or 0)
            worksheet.write(row, 5, f"{order.total_amount:,.0f} VNĐ")
            worksheet.write(row, 6, order.get_status_display())
            row += 1
        
        # Summary
        total_row = row + 2
        worksheet.write(total_row, 0, "TỔNG CỘNG:", header_format)
        worksheet.write(total_row, 1, f"{orders.count()} đơn hàng")
        total_amount = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        worksheet.write(total_row, 5, f"{total_amount:,.0f} VNĐ", header_format)
    
    # Báo cáo tồn kho
    elif report_type == 'inventory':
        branch_id = request.GET.get('branch', None)
        
        if branch_id:
            branch = get_object_or_404(Branch, id=branch_id)
            branch_name = branch.name
            inventory_items = InventoryItem.objects.filter(inventory__branch_id=branch_id)
        else:
            branch_name = "Tất cả chi nhánh"
            inventory_items = InventoryItem.objects.all()
        
        # Header
        title = f"BÁO CÁO TỒN KHO - {branch_name}"
        worksheet.merge_range('A1:F1', title, header_format)
        worksheet.write(2, 0, f"Ngày xuất báo cáo: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Table header
        headers = ["Mã SP", "Tên sản phẩm", "Danh mục", "Đơn giá", "Số lượng tồn", "Giá trị tồn"]
        for col, header in enumerate(headers):
            worksheet.write(4, col, header, header_format)
        
        # Data
        row = 5
        for item in inventory_items.select_related('product', 'product__category'):
            worksheet.write(row, 0, item.product.sku)
            worksheet.write(row, 1, item.product.name)
            worksheet.write(row, 2, item.product.category.name if item.product.category else "")
            worksheet.write(row, 3, f"{item.product.price:,.0f} VNĐ")
            worksheet.write(row, 4, item.quantity)
            value = item.quantity * item.product.price
            worksheet.write(row, 5, f"{value:,.0f} VNĐ")
            row += 1
        
        # Summary
        total_row = row + 2
        worksheet.write(total_row, 0, "TỔNG CỘNG:", header_format)
        total_value = inventory_items.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0
        total_items = inventory_items.aggregate(Sum('quantity'))['quantity__sum'] or 0
        worksheet.write(total_row, 4, total_items)
        worksheet.write(total_row, 5, f"{total_value:,.0f} VNĐ", header_format)
    
    workbook.close()
    
    # Return file
    output.seek(0)
    
    # Set filename and content type
    filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response 