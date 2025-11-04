from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .serializers import ProductDetailSerializer, ProductListSerializer
from .models import Product

def get_related_products(product_id: int):
    cache_key = f"related_products:{product_id}"
    data = cache.get(cache_key)

    if data:
        return data

    # product = Product.objects.select_related("categories", "brand").get(id=product_id)

    # qs = (
    #     Product.objects.filter(categories=product.categories, brand=product.brand)
    #     .exclude(id=product.id)
    #     .values("id", "name", "sku", "price")[:10]
    # )

    product = Product.objects.get(id=product_id)
    qs = product.get_similar(limit=10)

    data = list(qs)
    cache.set(cache_key, data, timeout=60 * 10)  # TTL 10 минут
    return data


def get_product_details(product_slug: str, *, context=None):
    """
    Достаём детальную карточку товара из кеша, иначе собираем, сериализуем и кешируем.
    """
    cache_key = f"product_details:{product_slug}"
    data = cache.get(cache_key)

    if data is not None:
        return data

    product = (
        Product.objects
        .filter(is_published=True)
        .select_related("brand")
        .prefetch_related("categories", "images")
        .prefetch_related("categories__children")  # если нужно иерархию тянуть
    )

    product = get_object_or_404(product, slug=product_slug)

    serializer = ProductDetailSerializer(product, context=context)
    data = serializer.data

    # TTL — 10 минут (можно увеличить до 1 часа, если данные редко меняются)
    cache.set(cache_key, data, timeout=60 * 10)

    return data