from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model
from catalog.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        related_name='carts',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_price(self):
        return Decimal(self.quantity) * self.product.price
    

class OrderRequest(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

