from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name
    

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

class Category(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name="Родительская категория")

    def get_descendants(self):
        """
        Возвращает список ID всех дочерних категорий (рекурсивно),
        включая саму категорию.
        """
        ids = [self.id]
        queue = [self]

        while queue:
            item = queue.pop(0)
            children = list(item.children.all())
            ids.extend([c.id for c in children])
            queue.extend(children)

        return ids

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True, null=True, blank=True, verbose_name="Складской артикул")
    name = models.CharField(max_length=400, verbose_name="Название")
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name='products', verbose_name="Бренд")
    categories = models.ManyToManyField(Category, related_name='products', blank=True, verbose_name="Категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    currency = models.CharField(max_length=10, default='сом', verbose_name="Валюта")
    quantity = models.IntegerField(default=0, verbose_name="Наличие")  # наличие
    is_published = models.BooleanField(default=True, verbose_name="Опубликован")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    favorites_count = models.PositiveIntegerField(default=0, verbose_name="Количество добавлений в избранное")
    popularity_score = models.DecimalField(default=0.0, max_digits=10, decimal_places=1, verbose_name="Популярность")  # computed field (views/purchases/ratings)
    search_vector = SearchVectorField(null=True, blank=True)  # для Postgres full-text (опционально)

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
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
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name="Товар")
    image = models.ImageField(upload_to='product_images/', verbose_name="Изображение")
    alt = models.CharField(max_length=255, blank=True, verbose_name="Альтернативный текст")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок")

    def __str__(self):
        return f"Изображение {self.id} для {self.product.name}"
    class Meta:
        verbose_name = "Фотография продукта"
        verbose_name_plural = "Фотографии продуктов"
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
