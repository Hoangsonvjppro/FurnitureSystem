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
    """Cập nhật trạng thái đơn hàng"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            old_status = order.status
            order.status = new_status
            
            # Cập nhật thời gian theo trạng thái
            if new_status == 'shipped' and not order.shipped_at:
                order.shipped_at = timezone.now()
            elif new_status == 'delivered' and not order.delivered_at:
                order.delivered_at = timezone.now()
            elif new_status == 'cancelled' and not order.cancelled_at:
                order.cancelled_at = timezone.now()
            
            order.processed_by = request.user
            order.save()
            
            messages.success(request, f'Trạng thái đơn hàng đã được cập nhật từ {dict(Order.STATUS_CHOICES)[old_status]} sang {dict(Order.STATUS_CHOICES)[new_status]}.')
        else:
            messages.error(request, 'Trạng thái không hợp lệ.')
    
    return redirect('orders:order_detail', pk=order.pk)


class PaymentCreateView(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'orders/payment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        context['order'] = get_object_or_404(Order, id=order_id)
        return context
    
    def form_valid(self, form):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        form.instance.order = order
        form.instance.created_by = self.request.user
        
        response = super().form_valid(form)
        
        # Cập nhật thông tin thanh toán của đơn hàng
        if form.instance.status == 'completed':
            order.paid_amount += form.instance.amount
            
            # Cập nhật trạng thái thanh toán
            if order.paid_amount >= order.total:
                order.payment_status = 'paid'
                order.paid_at = timezone.now()
            elif order.paid_amount > 0:
                order.payment_status = 'partial'
            
            order.save()
        
        messages.success(self.request, f'Thanh toán {form.instance.amount} đã được ghi nhận.')
        
        return response
    
    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.kwargs.get('order_id')})


@login_required
def generate_invoice_pdf(request, pk):
    """Tạo và in hóa đơn PDF cho đơn hàng"""
    try:
        # Import pisa chỉ khi cần sử dụng
        import pisa
        
        order = get_object_or_404(Order, pk=pk)
        
        # Kiểm tra quyền hạn - chỉ admin, người tạo đơn hàng hoặc nhân viên bán hàng mới có quyền
        if not (request.user.is_superuser or request.user == order.created_by or 
                request.user.is_sales_staff or request.user.is_branch_manager):
            messages.error(request, 'Bạn không có quyền thực hiện chức năng này.')
            return redirect('orders:order_detail', pk=order.pk)
        
        # Lấy các thông tin cần thiết
        order_items = order.items.all()
        payments = order.payments.all()
        
        # Tạo context cho template
        context = {
            'order': order,
            'order_items': order_items,
            'payments': payments,
            'current_date': timezone.now(),
            'staff_name': request.user.get_full_name()
        }
        
        # Tạo PDF từ template
        template = get_template('orders/invoice_pdf.html')
        html = template.render(context)
        
        # Tạo response với content type là PDF
        response = HttpResponse(content_type='application/pdf')
        
        # Đặt filename cho tệp PDF khi tải xuống
        filename = f"invoice-{order.order_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Tạo PDF sử dụng xhtml2pdf
        pisa_status = pisa.CreatePDF(html, dest=response)
        
        # Trả về error nếu có lỗi
        if pisa_status.err:
            return HttpResponse('Đã xảy ra lỗi khi tạo hóa đơn PDF: %s' % pisa_status.err)
        
        return response
    except ImportError:
        messages.error(request, 'Không thể tạo file PDF. Thư viện xhtml2pdf không khả dụng.')
        return redirect('orders:order_detail', pk=pk)


class DeliveryUpdateView(LoginRequiredMixin, UpdateView):
    model = Delivery
    form_class = DeliveryForm
    template_name = 'orders/delivery_form.html'
    
    def get_object(self, queryset=None):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        delivery, created = Delivery.objects.get_or_create(order=order)
        return delivery
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        context['order'] = get_object_or_404(Order, id=order_id)
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Thông tin giao hàng đã được cập nhật.')
        
        # Cập nhật trạng thái đơn hàng nếu đã giao hàng
        if form.instance.status == 'delivered':
            order = form.instance.order
            if order.status != 'delivered':
                order.status = 'delivered'
                order.delivered_at = timezone.now()
                order.save()
        
        return response
    
    def get_success_url(self):
        return reverse('orders:order_detail', kwargs={'pk': self.kwargs.get('order_id')}) 