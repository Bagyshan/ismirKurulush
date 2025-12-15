from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Product

# Create your models here.

User = get_user_model()

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by', verbose_name="Товар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"