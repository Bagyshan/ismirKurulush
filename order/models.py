from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model
from catalog.models import Product
from service.models import Service

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='carts',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    def __str__(self):
        return f"Корзина {self.id} пользователя {self.user.email if self.user else self.session_id}"
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    @property
    def total_price(self):
        return Decimal(self.quantity) * self.product.price
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} в корзине {self.cart.id}"
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
    

class OrderRequestType(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название типа")

    class Meta:
        verbose_name = "Тип заявки"
        verbose_name_plural = "Типы заявок"
        ordering = ["name"]

    def __str__(self):
        return self.name


class OrderRequest(models.Model):
    user = models.ForeignKey(
        User,
        related_name='order_requests',
        on_delete=models.CASCADE,
        null=True, blank=True
    )    
    request_type = models.CharField(max_length=200, verbose_name="Тип заявки", null=True, blank=True)
    cart = models.OneToOneField(
        Cart, 
        related_name='order_requests', 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Корзина"
    )
    service = models.ForeignKey(
        Service, 
        related_name='order_requests', 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Услуга"
    )
    name = models.CharField(max_length=200, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email", null=True, blank=True)
    phone = models.CharField(max_length=50, verbose_name="Телефон")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.name} ({self.phone})"
