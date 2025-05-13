from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Sum
from django.core.paginator import Paginator
from django.template.loader import get_template

from apps.orders.models import Order, OrderItem, Payment, Delivery
from apps.orders.forms import OrderForm, OrderItemForm, PaymentForm, DeliveryForm
from apps.products.models import Product, ProductVariant
from apps.cart.models import Cart, CartItem
from apps.inventory.models import Stock
from apps.branches.models import Branch


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Tìm kiếm
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(order_number__icontains=search_query) |
                Q(full_name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Lọc theo trạng thái
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Lọc theo phương thức thanh toán
        payment_method = self.request.GET.get('payment_method', '')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
        
        # Lọc theo chi nhánh
        branch_id = self.request.GET.get('branch', '')
        if branch_id:
            queryset = queryset.filter(branch_id=branch_id)
        
        # Lọc theo ngày
        from_date = self.request.GET.get('from_date', '')
        to_date = self.request.GET.get('to_date', '')
        if from_date:
            queryset = queryset.filter(created_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_orders'] = self.get_queryset().count()
        context['pending_orders'] = self.get_queryset().filter(status='pending').count()
        context['processing_orders'] = self.get_queryset().filter(status='processing').count()
        context['shipped_orders'] = self.get_queryset().filter(status='shipped').count()
        context['delivered_orders'] = self.get_queryset().filter(status='delivered').count()
        context['cancelled_orders'] = self.get_queryset().filter(status='cancelled').count()
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.all()
        context['payments'] = self.object.payments.all()
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        
        if not form.instance.branch:
            form.instance.branch = self.request.user.branch
        
        response = super().form_valid(form)
        messages.success(self.request, f'Đơn hàng #{self.object.order_number} đã được tạo thành công.')
        
        return response


@login_required
def create_order_from_cart(request):
    """Tạo đơn hàng từ giỏ hàng"""
    cart = Cart.objects.get_or_create(customer=request.user)[0]
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items.exists():
        messages.warning(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            
            # Tính toán giá trị đơn hàng
            subtotal = sum(item.subtotal for item in cart_items)
            order.subtotal = subtotal
            order.total = subtotal + order.shipping_fee + order.tax - order.discount
            
            # Gán chi nhánh cho đơn hàng
            if not order.branch:
                # Sử dụng chi nhánh của người dùng nếu có
                if request.user.branch:
                    order.branch = request.user.branch
                else:
                    # Hoặc sử dụng chi nhánh đầu tiên trong hệ thống
                    default_branch = Branch.objects.filter(is_active=True).first()
                    if default_branch:
                        order.branch = default_branch
                    else:
                        messages.error(request, 'Không thể tạo đơn hàng: Không tìm thấy chi nhánh phù hợp.')
                        return redirect('cart:cart_detail')
            
            order.save()
            
            # Chuyển các mặt hàng từ giỏ hàng sang đơn hàng
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    price=cart_item.price,
                    quantity=cart_item.quantity,
                    subtotal=cart_item.subtotal
                )
                
                # Cập nhật tồn kho
                stock_filters = {
                    'product': cart_item.product,
                    'branch': order.branch
                }
                
                if cart_item.variant:
                    stock_filters['variant'] = cart_item.variant
                    
                stock = Stock.objects.filter(**stock_filters).first()
                
                if stock:
                    stock.quantity -= cart_item.quantity
                    stock.save()
            
            # Xóa giỏ hàng
            cart_items.delete()
            
            messages.success(request, f'Đơn hàng #{order.order_number} đã được tạo thành công.')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        initial_data = {
            'recipient_name': request.user.get_full_name(),
            'recipient_phone': request.user.phone_number,
            'shipping_address': request.user.address
        }
        
        # Thêm địa chỉ giao hàng nếu có
        try:
            shipping_address = request.user.shipping_addresses.filter(is_default=True).first()
            if shipping_address:
                initial_data.update({
                    'recipient_name': shipping_address.recipient_name,
                    'recipient_phone': shipping_address.phone,
                    'shipping_address': shipping_address.address,
                    'city': shipping_address.city,
                    'district': shipping_address.district,
                    'ward': shipping_address.ward,
                })
        except:
            pass
        
        form = OrderForm(initial=initial_data)
    
    # Tính toán tổng giá trị
    subtotal = sum(item.subtotal for item in cart_items)
    shipping_fee = 0  # Có thể tính toán dựa trên địa chỉ giao hàng
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_fee': shipping_fee,
        'total': subtotal + shipping_fee
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Kiểm tra quyền truy cập
    if not (request.user.is_superuser or request.user.role == 'MANAGER' or request.user.role == 'SALES_STAFF'):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('orders:order_detail', pk=order.pk)
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status and status in dict(Order.STATUS_CHOICES):
            # Cập nhật trạng thái đơn hàng
            order.status = status
            order.processed_by = request.user
            order.processed_at = timezone.now()
            order.save()
            
            messages.success(request, f'Trạng thái đơn hàng đã được cập nhật thành {dict(Order.STATUS_CHOICES)[status]}.')
        else:
            messages.error(request, 'Trạng thái không hợp lệ.')
    
    return redirect('orders:order_detail', pk=order.pk)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'orders/payment_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Kiểm tra quyền truy cập
        if not (request.user.is_superuser or request.user.role == 'MANAGER' or request.user.role == 'SALES_STAFF'):
            messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
            return redirect('orders:order_detail', pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        return context
    
    def form_valid(self, form):
        order = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        
        payment = form.save(commit=False)
        payment.order = order
        payment.created_by = self.request.user
        
        # Cập nhật trạng thái thanh toán của đơn hàng
        if payment.status == 'completed':
            # Tính tổng tiền đã thanh toán
            existing_payments = Payment.objects.filter(
                order=order, 
                status='completed'
            ).aggregate(total=Sum('amount'))
            
            total_paid = existing_payments.get('total') or 0
            total_paid += payment.amount
            
            # Cập nhật trạng thái thanh toán
            if total_paid >= order.total:
                order.payment_status = 'paid'
            elif total_paid > 0:
                order.payment_status = 'partial'
            
            order.save()
        
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Thanh toán đã được thêm thành công.')
        return reverse('orders:order_detail', kwargs={'pk': self.kwargs.get('pk')})


@login_required
def generate_invoice_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Kiểm tra quyền truy cập
    if not (request.user.is_superuser or request.user.role == 'MANAGER' or request.user.role == 'SALES_STAFF' or request.user == order.customer):
        messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
        return redirect('orders:order_detail', pk=order.pk)
    
    # Nếu chưa có đơn hàng, chuyển hướng về trang chi tiết với thông báo lỗi
    if not order.items.exists():
        messages.error(request, 'Không thể tạo hóa đơn: Đơn hàng không có sản phẩm.')
        return redirect('orders:order_detail', pk=order.pk)
    
    # Nếu đơn hàng chưa thanh toán, chuyển hướng về trang chi tiết với thông báo lỗi
    if order.payment_status != 'paid':
        messages.warning(request, 'Đơn hàng chưa thanh toán đầy đủ. Hóa đơn có thể không chính xác.')
    
    # Tạo hóa đơn
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from io import BytesIO
        from decimal import Decimal
        
        # Tạo một đối tượng BytesIO để ghi PDF vào
        buffer = BytesIO()
        
        # Tạo đối tượng PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        styles = getSampleStyleSheet()
        
        # Tạo các phần tử cho PDF
        elements = []
        
        # Thêm tiêu đề
        elements.append(Paragraph(f"Hóa đơn #{order.order_number}", styles['Heading1']))
        elements.append(Spacer(1, 20))
        
        # Thông tin cửa hàng
        elements.append(Paragraph("Cửa hàng nội thất XYZ", styles['Heading2']))
        elements.append(Paragraph(f"Chi nhánh: {order.branch.name}", styles['Normal']))
        elements.append(Paragraph(f"Địa chỉ: {order.branch.address}", styles['Normal']))
        elements.append(Paragraph(f"Điện thoại: {order.branch.phone}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Thông tin khách hàng
        elements.append(Paragraph("Thông tin khách hàng", styles['Heading2']))
        elements.append(Paragraph(f"Khách hàng: {order.full_name}", styles['Normal']))
        elements.append(Paragraph(f"Địa chỉ: {order.shipping_address}, {order.ward}, {order.district}, {order.city}", styles['Normal']))
        elements.append(Paragraph(f"Điện thoại: {order.phone}", styles['Normal']))
        elements.append(Paragraph(f"Email: {order.email}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Thông tin đơn hàng
        elements.append(Paragraph("Chi tiết đơn hàng", styles['Heading2']))
        elements.append(Paragraph(f"Ngày đặt hàng: {order.created_at.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"Phương thức thanh toán: {dict(Order.PAYMENT_METHOD_CHOICES).get(order.payment_method)}", styles['Normal']))
        elements.append(Spacer(1, 10))
        
        # Bảng chi tiết sản phẩm
        data = [
            ['STT', 'Sản phẩm', 'Đơn giá', 'Số lượng', 'Thành tiền']
        ]
        
        for index, item in enumerate(order.items.all(), start=1):
            product_info = f"{item.product.name}"
            if item.variant:
                product_info += f"\n{item.variant.name}"
            
            data.append([
                str(index),
                product_info,
                f"{item.price:,.0f} đ",
                str(item.quantity),
                f"{item.subtotal:,.0f} đ"
            ])
        
        # Thêm tổng tiền
        data.append(['', '', '', 'Tạm tính', f"{order.subtotal:,.0f} đ"])
        
        if order.shipping_fee:
            data.append(['', '', '', 'Phí vận chuyển', f"{order.shipping_fee:,.0f} đ"])
        
        if order.tax:
            data.append(['', '', '', 'Thuế', f"{order.tax:,.0f} đ"])
        
        if order.discount:
            data.append(['', '', '', 'Giảm giá', f"-{order.discount:,.0f} đ"])
        
        data.append(['', '', '', 'Tổng cộng', f"{order.total:,.0f} đ"])
        
        # Tạo bảng
        table = Table(data, colWidths=[30, 220, 80, 80, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -5), (-1, -1), 'Helvetica-Bold'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('LINEABOVE', (0, -5), (-1, -5), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Chữ ký và ghi chú
        elements.append(Paragraph("Ghi chú:", styles['Heading3']))
        elements.append(Paragraph("- Hàng đã bán không đổi trả, trừ trường hợp lỗi do nhà sản xuất.", styles['Normal']))
        elements.append(Paragraph("- Quý khách vui lòng kiểm tra kỹ sản phẩm trước khi nhận hàng.", styles['Normal']))
        elements.append(Spacer(1, 30))
        
        # Tạo bảng chữ ký
        signature_data = [
            ['Người mua hàng', '', 'Người bán hàng'],
            ['(Ký, ghi rõ họ tên)', '', '(Ký, đóng dấu)'],
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
            [order.full_name, '', request.user.get_full_name()],
        ]
        
        signature_table = Table(signature_data, colWidths=[160, 80, 160])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))
        
        elements.append(signature_table)
        
        # Xây dựng PDF
        doc.build(elements)
        
        # Lấy nội dung PDF
        pdf_value = buffer.getvalue()
        buffer.close()
        
        # Tạo HTTP Response với PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="invoice_{order.order_number}.pdf"'
        response.write(pdf_value)
        
        return response
    
    except Exception as e:
        messages.error(request, f'Không thể tạo hóa đơn: {str(e)}')
        return redirect('orders:order_detail', pk=order.pk)


class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'orders/delivery_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Kiểm tra quyền truy cập
        if not (request.user.is_superuser or request.user.role == 'MANAGER' or request.user.role == 'SALES_STAFF'):
            messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
            return redirect('orders:order_detail', pk=self.kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        order = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        delivery, created = Delivery.objects.get_or_create(order=order)
        return delivery
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, pk=self.kwargs.get('pk'))
        return context
    
    def form_valid(self, form):
        delivery = form.save()
        order = delivery.order
        
        # Cập nhật trạng thái đơn hàng nếu cần
        if delivery.status == 'delivered' and order.status != 'delivered':
            order.status = 'delivered'
            order.save()
        elif delivery.status == 'shipping' and order.status == 'pending':
            order.status = 'shipped'
            order.save()
        elif delivery.status == 'returned' and order.status != 'cancelled':
            order.status = 'cancelled'
            order.save()
        
        messages.success(self.request, 'Thông tin giao hàng đã được cập nhật thành công.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.kwargs.get('pk')}) 