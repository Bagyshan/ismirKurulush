from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True, null=True, blank=True)
    name = models.CharField(max_length=400)
    slug = models.SlugField(max_length=400, unique=True)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name='products')
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='сом')
    quantity = models.IntegerField(default=0)  # наличие
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)  # для Postgres full-text (опционально)
    popularity_score = models.DecimalField(default=0.0, max_digits=10, decimal_places=1)  # computed field (views/purchases/ratings)

    class Meta:
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['-created_at']),
            GinIndex(fields=['search_vector']),
        ]

    def in_stock(self):
        return self.quantity > 0

    def __str__(self):
        return self.name

    def get_similar(self, limit=10):
        """
        Быстрая реализация похожих товаров:
        1) сначала — товары, которые разделяют категории (кол-во совпадений)
        2) затем — товары того же бренда
        3) затем — товары с похожими характеристиками (если есть)
        Пришлю пример реализации ниже.
        """
        from django.db.models import Count, Q

        cat_ids = list(self.categories.values_list('id', flat=True))

        # Основная выборка — по категориям
        qs_by_categories = (
            Product.objects
            .filter(is_published=True)
            .exclude(id=self.id)
            .filter(categories__in=cat_ids)
            .annotate(shared_categories=Count('categories', filter=Q(categories__in=cat_ids)))
            .order_by('-shared_categories')
            .distinct()
        )

        result = list(qs_by_categories[:limit])

        # Если меньше `limit`, добираем товарами того же бренда
        if len(result) < limit and self.brand:
            missing = limit - len(result)
            qs_by_brand = (
                Product.objects
                .filter(is_published=True, brand=self.brand)
                .exclude(id=self.id)
                .exclude(id__in=[p.id for p in result])
                .order_by('-popularity_score')[:missing]
            )
            result.extend(qs_by_brand)

        return result[:limit]

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

# class Characteristic(models.Model):
#     product = models.ForeignKey(Product, related_name='characteristics', on_delete=models.CASCADE)
#     key = models.CharField(max_length=200)
#     value = models.CharField(max_length=800)

#     class Meta:
#         unique_together = ('product', 'key')

# class Review(models.Model):
#     product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
#     author_name = models.CharField(max_length=200)
#     rating = models.PositiveSmallIntegerField()  # 1..5
#     text = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']
