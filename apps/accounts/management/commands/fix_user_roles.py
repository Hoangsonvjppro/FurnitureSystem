from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Thiết lập vai trò cho người dùng'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Tên đăng nhập của người dùng cần cập nhật')
        parser.add_argument('--role', type=str, choices=['ADMIN', 'MANAGER', 'SALES_STAFF', 'INVENTORY_STAFF', 'CUSTOMER'], 
                            help='Đặt vai trò cho người dùng')
        parser.add_argument('--activate', action='store_true', help='Kích hoạt tài khoản')
        parser.add_argument('--deactivate', action='store_true', help='Vô hiệu hóa tài khoản')
        
    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            
            # Hiển thị thông tin hiện tại
            self.stdout.write(f'Thông tin người dùng: {user.get_full_name()} ({username})')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Kích hoạt: {user.is_active}')
            self.stdout.write(f'  Vai trò: {user.role}')
            self.stdout.write('')
            
            # Cập nhật vai trò nếu có chỉ định
            if options['role']:
                user.role = options['role']
                self.stdout.write(f'>> Đã cập nhật vai trò: {user.role}')
                
            # Cập nhật trạng thái kích hoạt
            if options['activate']:
                user.is_active = True
                self.stdout.write('>> Đã kích hoạt tài khoản')
            elif options['deactivate']:
                user.is_active = False
                self.stdout.write('>> Đã vô hiệu hóa tài khoản')
                
            user.save()
            
            # Hiển thị thông tin sau khi cập nhật
            self.stdout.write('\nSau khi cập nhật:')
            self.stdout.write(f'  Kích hoạt: {user.is_active}')
            self.stdout.write(f'  Vai trò: {user.role}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Không tìm thấy người dùng với tên "{username}"')) 