from django import forms
from django.contrib.auth import get_user_model
from .models import StaffProfile, StaffSchedule, Performance

User = get_user_model()


class StaffProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label="Tên")
    last_name = forms.CharField(max_length=30, label="Họ")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput(), required=False, label="Mật khẩu")
    
    class Meta:
        model = StaffProfile
        fields = [
            'staff_id', 'role', 'branch', 'date_hired', 'phone', 
            'address', 'emergency_contact', 'profile_image', 'status'
        ]
        widgets = {
            'date_hired': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Nếu đang chỉnh sửa một hồ sơ hiện có
        if instance:
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['email'].initial = instance.user.email
            self.fields['email'].widget.attrs['readonly'] = True
        
        # Mật khẩu chỉ bắt buộc khi tạo mới
        if not instance:
            self.fields['password'].required = True
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Lấy hoặc tạo user
        if profile.pk:  # Nếu đang cập nhật
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            
            # Cập nhật mật khẩu nếu có cung cấp
            password = self.cleaned_data.get('password')
            if password:
                user.set_password(password)
            
            user.save()
        else:  # Nếu đang tạo mới
            user = User.objects.create_user(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name']
            )
            profile.user = user
        
        if commit:
            profile.save()
        
        return profile


class StaffScheduleForm(forms.ModelForm):
    class Meta:
        model = StaffSchedule
        fields = ['date', 'start_time', 'end_time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.staff_id = kwargs.pop('staff_id', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        date = cleaned_data.get('date')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu.")
        
        # Kiểm tra xem có lịch trình chồng chéo không
        if start_time and end_time and date and self.staff_id:
            overlapping_schedules = StaffSchedule.objects.filter(
                staff_id=self.staff_id,
                date=date
            ).exclude(pk=self.instance.pk if self.instance and self.instance.pk else None)
            
            for schedule in overlapping_schedules:
                if (start_time <= schedule.end_time and end_time >= schedule.start_time):
                    raise forms.ValidationError(
                        f"Lịch trình này chồng chéo với lịch trình từ {schedule.start_time} đến {schedule.end_time}."
                    )
        
        return cleaned_data


class PerformanceForm(forms.ModelForm):
    class Meta:
        model = Performance
        fields = ['period', 'sales_target', 'sales_achieved', 'orders_processed', 'customer_rating', 'notes']
        widgets = {
            'period': forms.TextInput(attrs={'placeholder': 'MM/YYYY'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.staff_id = kwargs.pop('staff_id', None)
        super().__init__(*args, **kwargs)
        
        # Thiết lập giá trị mặc định cho period là tháng hiện tại
        if not self.instance.pk:
            import datetime
            self.fields['period'].initial = datetime.datetime.now().strftime('%m/%Y')
    
    def clean_period(self):
        period = self.cleaned_data.get('period')
        
        # Kiểm tra định dạng MM/YYYY
        import re
        if not re.match(r'^(0[1-9]|1[0-2])/20\d{2}$', period):
            raise forms.ValidationError("Định dạng phải là MM/YYYY (ví dụ: 01/2023).")
        
        # Kiểm tra trùng lặp
        if self.staff_id:
            existing = Performance.objects.filter(
                staff_id=self.staff_id,
                period=period
            ).exclude(pk=self.instance.pk if self.instance and self.instance.pk else None)
            
            if existing.exists():
                raise forms.ValidationError(f"Đã tồn tại hiệu suất cho kỳ {period}.")
        
        return period 