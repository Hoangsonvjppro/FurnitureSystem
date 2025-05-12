from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product, ProductImage


@receiver(post_save, sender=ProductImage)
def update_product_main_image(sender, instance, created, **kwargs):
    """
    When a product image is saved and marked as primary, update the main image of the product
    """
    if instance.is_primary:
        # Update all other images to not be primary
        ProductImage.objects.filter(
            product=instance.product, 
            is_primary=True
        ).exclude(
            id=instance.id
        ).update(
            is_primary=False
        )
        
        # Update the product's main image
        if instance.product.image != instance.image:
            instance.product.image = instance.image
            instance.product.save(update_fields=['image'])


@receiver(post_delete, sender=ProductImage)
def handle_deleted_product_image(sender, instance, **kwargs):
    """
    When a primary product image is deleted, set another image as primary if available
    """
    if instance.is_primary:
        # Find another image to set as primary
        next_image = ProductImage.objects.filter(product=instance.product).first()
        if next_image:
            next_image.is_primary = True
            next_image.save()
            
            # Update the product's main image
            instance.product.image = next_image.image
            instance.product.save(update_fields=['image']) 