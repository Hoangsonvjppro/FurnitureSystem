from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from apps.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem
from apps.products.models import Product, ProductVariant
from apps.branches.models import Branch

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = [
            'name', 'code', 'contact_person', 'phone', 'email', 
            'address', 'tax_code', 'website', 'description', 
            'is_active', 'rating'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            code = code.upper()
            # Kiểm tra mã nhà cung cấp đã tồn tại chưa
            supplier_exists = Supplier.objects.filter(code=code)
            if self.instance.pk:
                supplier_exists = supplier_exists.exclude(pk=self.instance.pk)
            if supplier_exists.exists():
                raise forms.ValidationError("Mã nhà cung cấp này đã tồn tại, vui lòng chọn mã khác.")
        return code


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'branch', 'order_date', 'expected_date', 
            'notes', 'status'
        ]
        widgets = {
            'order_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Chỉ hiển thị nhà cung cấp đang hoạt động
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        
        # Nếu người dùng thuộc chi nhánh cụ thể, chỉ hiển thị chi nhánh đó
        if user and user.branch:
            self.fields['branch'].queryset = Branch.objects.filter(pk=user.branch.pk)
            self.fields['branch'].initial = user.branch
            self.fields['branch'].widget.attrs['disabled'] = True
        else:
            self.fields['branch'].queryset = Branch.objects.filter(is_active=True)

        # Mặc định ngày đặt hàng là ngày hiện tại
        if not self.instance.pk:
            self.fields['order_date'].initial = timezone.now().date()
            
        # Giới hạn trạng thái cho phép cập nhật
        if self.instance.pk:
            if self.instance.status == 'received':
                self.fields['status'].widget.attrs['disabled'] = True
                for field_name in self.fields:
                    if field_name != 'notes':
                        self.fields[field_name].widget.attrs['disabled'] = True


class PurchaseOrderItemForm(forms.ModelForm):
    product_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['product', 'variant', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'select2'}),
            'variant': forms.Select(attrs={'class': 'select2'}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
            'unit_price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['variant'].queryset = ProductVariant.objects.none()
        
        if self.instance.pk:
            if self.instance.product:
                self.fields['variant'].queryset = ProductVariant.objects.filter(product=self.instance.product)
                self.fields['product_name'].initial = self.instance.product.name
            if self.instance.purchase_order.status in ['received', 'cancelled']:
                for field_name in self.fields:
                    self.fields[field_name].widget.attrs['disabled'] = True

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        variant = cleaned_data.get('variant')
        
        if product and variant and variant.product != product:
            raise forms.ValidationError({'variant': 'Biến thể này không thuộc sản phẩm đã chọn.'})
            
        return cleaned_data


# Formset cho các mục trong đơn hàng nhập
PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
) 