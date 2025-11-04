
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product
from django_redis import get_redis_connection


def invalidate_product_cache(product_slug: str):
    r = get_redis_connection("default")
    r.delete(f"product_details:{product_slug}")

@receiver([post_save, post_delete], sender=Product)
def product_changed(sender, instance, **kwargs):
    invalidate_product_cache(instance.slug)