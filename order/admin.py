from django.contrib import admin
from .models import Cart, CartItem, OrderRequest, OrderRequestType

# Register your models here.

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_id', 'created_at')
    inlines = [CartItemInline]
    search_fields = ('user__username', 'session_id')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')
    search_fields = ('cart__session_id', 'product__name')


class CartInline(admin.TabularInline):
    model = Cart
    extra = 1
    inline_classes = [CartItemInline]
@admin.register(OrderRequest)
class OrderRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'created_at')
    list_filter = ('created_at',)
    inlines = [CartInline]
    search_fields = ('name', 'phone')

# @admin.register(OrderRequestType)
# class OrderRequestTypeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     search_fields = ('name',)