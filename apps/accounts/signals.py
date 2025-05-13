from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, CustomerProfile
from apps.cart.models import Cart


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Tạo profile cho khách hàng mới"""
    if created and instance.role == 'CUSTOMER':
        CustomerProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_customer_cart(sender, instance, created, **kwargs):
    """Tạo giỏ hàng cho khách hàng mới"""
    if created and instance.role == 'CUSTOMER':
        Cart.objects.create(customer=instance)
