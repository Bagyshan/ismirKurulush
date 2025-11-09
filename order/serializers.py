from rest_framework import serializers
from .models import Cart, CartItem

# class CartItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product', 'quantity', 'total_price']


# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)
#     total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

#     class Meta:
#         model = Cart
#         fields = ['id', 'items', 'total_amount']


from decimal import Decimal
from rest_framework import serializers
from django.utils import timezone

from .models import Cart, CartItem, OrderRequest
from catalog.models import Product


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be positive')
        return value

    def validate(self, data):
        product = data['product']
        if not product.is_published:
            raise serializers.ValidationError('Product not available')
        return data


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_product(self, obj):
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'price': str(obj.product.price),
            'currency': obj.product.currency,
            'in_stock': obj.product.in_stock(),
        }

    def get_total_price(self, obj):
        return str(obj.total_price)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'items', 'total_amount']
        read_only_fields = ['user', 'session_id']

    def get_total_amount(self, obj):
        total = sum(Decimal(item.total_price) for item in obj.items.all())
        return str(total)


class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = ['id', 'name', 'phone', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_phone(self, value):
        # Простая валидация: оставим гибкой. В продакшне рекомендую более строгую
        if not value:
            raise serializers.ValidationError('Phone is required')
        return value
    
from rest_framework import serializers
from .models import OrderRequest

class OrderRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderRequest
        fields = ['id', 'name', 'phone', 'comment', 'created_at', 'updated_at', 'is_processed']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_processed']

    def validate_phone(self, value):
        # Простая валидация: оставим гибкой. В продакшне рекомендую более строгую
        if not value:
            raise serializers.ValidationError('Phone is required')
        return value
    









"================================= Cart Swagger Docs Serializers ==============================="

class CartAddSerializer(serializers.Serializer):
    product = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)


class CartUpdateSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)


class CartRemoveSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(required=True)
