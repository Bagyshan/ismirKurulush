from django_redis import get_redis_connection



def increment_product_view(product_id: int):
    """
    Увеличиваем счетчик просмотров товара в Redis (db=1).
    """
    r = get_redis_connection("analytics")
    r.incr(f"product:views:{product_id}")