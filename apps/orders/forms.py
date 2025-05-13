from django import forms
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order, OrderItem, Payment, Delivery


class OrderForm(forms.ModelForm):
    """Form tạo đơn hàng"""
    class Meta:
        model = Order
        fields = [
            'branch', 'recipient_name', 'recipient_phone',
            'shipping_address', 'city', 'district', 'ward',
            'payment_method', 'shipping_fee', 'tax', 'discount', 'notes'
        ]
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set các trường không bắt buộc
        self.fields['branch'].required = False
        self.fields['tax'].required = False
        self.fields['discount'].required = False
        self.fields['shipping_fee'].required = False
        self.fields['notes'].required = False
        
        # Đặt giá trị mặc định
        self.fields['tax'].initial = 0
        self.fields['discount'].initial = 0
        self.fields['shipping_fee'].initial = 0
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Kiểm tra các giá trị không âm
        for field in ['shipping_fee', 'tax', 'discount']:
            value = cleaned_data.get(field)
            if value and value < 0:
                self.add_error(field, _("Giá trị không được âm."))
        
        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """Form chi tiết đơn hàng"""
    class Meta:
        model = OrderItem
        fields = ['product', 'price', 'quantity']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Đặt giá trị mặc định
        self.fields['quantity'].initial = 1
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Kiểm tra số lượng
        quantity = cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            self.add_error('quantity', _("Số lượng phải lớn hơn 0."))
        
        return cleaned_data


class PaymentForm(forms.ModelForm):
    """Form thanh toán"""
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id', 'status', 'notes']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set các trường không bắt buộc
        self.fields['transaction_id'].required = False
        self.fields['notes'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Kiểm tra số tiền
        amount = cleaned_data.get('amount')
        if amount and amount <= 0:
            self.add_error('amount', _("Số tiền phải lớn hơn 0."))
        
        return cleaned_data


class DeliveryForm(forms.ModelForm):
    """Form giao hàng"""
    class Meta:
        model = Delivery
        fields = ['tracking_number', 'carrier', 'delivery_date', 'status', 'notes']
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set các trường không bắt buộc
        self.fields['tracking_number'].required = False
        self.fields['carrier'].required = False
        self.fields['delivery_date'].required = False
        self.fields['notes'].required = False 