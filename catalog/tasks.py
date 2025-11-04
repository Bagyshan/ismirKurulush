from celery import shared_task
from django_redis import get_redis_connection
from catalog.models import Product
from django.db.models import F

@shared_task
def sync_product_views():
    r = get_redis_connection("analytics")
    keys = r.keys("product:views:*")
    for key in keys:
        product_id = int(key.decode().split(":")[-1])
        views = int(r.get(key))

        Product.objects.filter(id=product_id).update(
            popularity_score=F('popularity_score') + (views * 0.4) # Вес просмотров в популярности
        )

        r.delete(key)