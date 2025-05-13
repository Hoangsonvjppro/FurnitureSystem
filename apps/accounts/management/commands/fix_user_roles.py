from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix user roles for specific users or show roles of all users'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username to fix')
        parser.add_argument('--list', action='store_true', help='List all users and their roles')
        parser.add_argument('--make-sales', action='store_true', help='Set is_sales_staff=True for the user')
        parser.add_argument('--make-inventory', action='store_true', help='Set is_inventory_staff=True for the user')
        parser.add_argument('--make-manager', action='store_true', help='Set is_branch_manager=True for the user')

    def handle(self, *args, **options):
        # List all users and their roles
        if options['list']:
            self.stdout.write(self.style.SUCCESS('Listing all users and their roles:'))
            for user in User.objects.all():
                self.stdout.write(f'Username: {user.username}')
                self.stdout.write(f'  Superuser: {user.is_superuser}')
                self.stdout.write(f'  Staff: {user.is_staff}')
                self.stdout.write(f'  Sales staff: {user.is_sales_staff}')
                self.stdout.write(f'  Inventory staff: {user.is_inventory_staff}')
                self.stdout.write(f'  Branch manager: {user.is_branch_manager}')
                self.stdout.write('-' * 30)
            return

        # Fix roles for a specific user
        username = options['username']
        if not username:
            self.stdout.write(self.style.ERROR('Please provide a username with --username'))
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
            return

        # Show current roles
        self.stdout.write(f'Current roles for {user.username}:')
        self.stdout.write(f'  Superuser: {user.is_superuser}')
        self.stdout.write(f'  Staff: {user.is_staff}')
        self.stdout.write(f'  Sales staff: {user.is_sales_staff}')
        self.stdout.write(f'  Inventory staff: {user.is_inventory_staff}')
        self.stdout.write(f'  Branch manager: {user.is_branch_manager}')

        # Update roles
        updated = False
        if options['make_sales']:
            user.is_sales_staff = True
            updated = True
            self.stdout.write(self.style.SUCCESS(f'Set {user.username} as sales staff'))

        if options['make_inventory']:
            user.is_inventory_staff = True
            updated = True
            self.stdout.write(self.style.SUCCESS(f'Set {user.username} as inventory staff'))

        if options['make_manager']:
            user.is_branch_manager = True
            updated = True
            self.stdout.write(self.style.SUCCESS(f'Set {user.username} as branch manager'))

        if updated:
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User {user.username} updated successfully'))
        else:
            self.stdout.write(self.style.WARNING('No role changes were made. Use --make-sales, --make-inventory, or --make-manager to update roles.')) 