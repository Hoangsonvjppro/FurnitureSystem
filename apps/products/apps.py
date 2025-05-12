from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Quản lý sản phẩm'
    
    def ready(self):
        import apps.products.signals 