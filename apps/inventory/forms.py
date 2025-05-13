from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.inventory.models import Stock, StockMovement, Inventory, InventoryItem
from apps.products.models import Product, ProductVariant
from apps.branches.models import Branch


class StockForm(forms.ModelForm):
    """Form cập nhật thông tin tồn kho"""
    class Meta:
        model = Stock
        fields = ['min_quantity', 'max_quantity', 'quantity']
        help_texts = {
            'min_quantity': _('Khi số lượng tồn kho dưới mức này, hệ thống sẽ cảnh báo tồn kho thấp'),
            'max_quantity': _('Khi số lượng tồn kho vượt mức này, hệ thống sẽ cảnh báo tồn kho cao'),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        min_quantity = cleaned_data.get('min_quantity')
        max_quantity = cleaned_data.get('max_quantity')
        
        if min_quantity is not None and max_quantity is not None and min_quantity > max_quantity:
            self.add_error('min_quantity', _('Số lượng tối thiểu không được lớn hơn số lượng tối đa'))
        
        return cleaned_data


class StockMovementForm(forms.ModelForm):
    """Form tạo chuyển động kho"""
    class Meta:
        model = StockMovement
        fields = [
            'product', 'movement_type', 'quantity', 'from_branch', 'to_branch',
            'reference', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Đặt các trường không bắt buộc
        self.fields['from_branch'].required = False
        self.fields['to_branch'].required = False
        self.fields['reference'].required = False
        self.fields['notes'].required = False
        
        # Chỉ hiển thị sản phẩm đang hoạt động
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
    
    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        from_branch = cleaned_data.get('from_branch')
        to_branch = cleaned_data.get('to_branch')
        quantity = cleaned_data.get('quantity')
        
        # Kiểm tra số lượng
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', _('Số lượng phải lớn hơn 0'))
        
        # Kiểm tra yêu cầu branch cho các loại chuyển động
        if movement_type == 'TRANSFER':
            if not from_branch:
                self.add_error('from_branch', _('Chi nhánh nguồn là bắt buộc khi chuyển kho'))
            if not to_branch:
                self.add_error('to_branch', _('Chi nhánh đích là bắt buộc khi chuyển kho'))
        elif movement_type == 'IN':
            if not to_branch:
                self.add_error('to_branch', _('Chi nhánh đích là bắt buộc khi nhập kho'))
        elif movement_type == 'OUT':
            if not from_branch:
                self.add_error('from_branch', _('Chi nhánh nguồn là bắt buộc khi xuất kho'))
        
        return cleaned_data


class InventoryForm(forms.ModelForm):
    """Form tạo đợt kiểm kê"""
    class Meta:
        model = Inventory
        fields = ['branch', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False


class InventoryItemForm(forms.ModelForm):
    """Form cập nhật item kiểm kê"""
    class Meta:
        model = InventoryItem
        fields = ['actual_quantity', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False
    
    def clean_actual_quantity(self):
        actual_quantity = self.cleaned_data.get('actual_quantity')
        if actual_quantity is not None and actual_quantity < 0:
            raise forms.ValidationError(_('Số lượng thực tế không được âm'))
        return actual_quantity 