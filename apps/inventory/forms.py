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
            'product', 'variant', 'branch', 'destination_branch',
            'movement_type', 'quantity', 'reference', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Đặt các trường không bắt buộc
        self.fields['variant'].required = False
        self.fields['destination_branch'].required = False
        self.fields['reference'].required = False
        self.fields['notes'].required = False
        
        # Chỉ hiển thị sản phẩm đang hoạt động
        self.fields['product'].queryset = Product.objects.filter(is_active=True)
        
        # Dynamic filtering cho variant field dựa trên product
        if 'product' in self.data:
            try:
                product_id = int(self.data.get('product'))
                self.fields['variant'].queryset = ProductVariant.objects.filter(
                    product_id=product_id, is_active=True
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.product:
            self.fields['variant'].queryset = self.instance.product.variants.filter(
                is_active=True
            )
        else:
            self.fields['variant'].queryset = ProductVariant.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('movement_type')
        destination_branch = cleaned_data.get('destination_branch')
        quantity = cleaned_data.get('quantity')
        
        # Kiểm tra số lượng
        if quantity is not None and quantity <= 0:
            self.add_error('quantity', _('Số lượng phải lớn hơn 0'))
        
        # Kiểm tra yêu cầu destination_branch cho chuyển kho
        if movement_type == 'transfer' and not destination_branch:
            self.add_error('destination_branch', _('Chi nhánh đích là bắt buộc khi chuyển kho'))
        
        return cleaned_data


class InventoryForm(forms.ModelForm):
    """Form tạo đợt kiểm kê"""
    class Meta:
        model = Inventory
        fields = ['branch', 'inventory_date', 'notes']
        widgets = {
            'inventory_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False
        
        # Mặc định ngày kiểm kê là hôm nay
        if not self.instance.pk:
            self.fields['inventory_date'].initial = timezone.now().date()
    
    def clean_inventory_date(self):
        inventory_date = self.cleaned_data.get('inventory_date')
        if inventory_date and inventory_date > timezone.now().date():
            raise forms.ValidationError(_('Ngày kiểm kê không được lớn hơn ngày hiện tại'))
        return inventory_date


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