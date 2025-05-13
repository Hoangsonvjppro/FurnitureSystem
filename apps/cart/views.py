from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Cart, CartItem
from apps.products.models import Product, ProductVariant


@login_required
def cart_detail(request):
    """Hiển thị giỏ hàng"""
    cart, created = Cart.objects.get_or_create(customer=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'cart/cart.html', context)


@login_required
@require_POST
def add_to_cart(request):
    """Thêm sản phẩm vào giỏ hàng"""
    product_id = request.POST.get('product_id')
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))
    
    product = get_object_or_404(Product, id=product_id)
    variant = None
    
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id)
    
    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product, variant=variant)
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Đã cập nhật số lượng {product.name} trong giỏ hàng.')
    except CartItem.DoesNotExist:
        CartItem.objects.create(
            cart=cart,
            product=product,
            variant=variant,
            quantity=quantity
        )
        messages.success(request, f'Đã thêm {product.name} vào giỏ hàng.')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = {
            'total_items': cart.total_items,
            'total_price': cart.total_price
        }
        return JsonResponse(data)
    
    return redirect('cart:cart_detail')


@login_required
@require_POST
def update_cart(request):
    """Cập nhật số lượng sản phẩm trong giỏ hàng"""
    cart_item_id = request.POST.get('cart_item_id')
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__customer=request.user)
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart
        data = {
            'total_items': cart.total_items,
            'total_price': cart.total_price,
            'item_total': cart_item.total_price if quantity > 0 else 0
        }
        return JsonResponse(data)
    
    return redirect('cart:cart_detail')


@login_required
def remove_from_cart(request, item_id):
    """Xóa sản phẩm khỏi giỏ hàng"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f'Đã xóa {product_name} khỏi giỏ hàng.')
    return redirect('cart:cart_detail')


@login_required
def clear_cart(request):
    """Xóa toàn bộ giỏ hàng"""
    cart = Cart.objects.filter(customer=request.user).first()
    if cart:
        CartItem.objects.filter(cart=cart).delete()
        messages.success(request, 'Đã xóa toàn bộ giỏ hàng.')
    
    return redirect('cart:cart_detail') 