from django.contrib import admin
from .models import Product, Brand, Category, ProductImage
# Register your models here.





class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'quantity', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'brand', 'categories')
    search_fields = ('name', 'description')
    # prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'created_at'
    exclude = ('search_vector',)
    readonly_fields = ('created_at', 'updated_at', 'favorites_count', 'popularity_score', 'favorites_count', )
    inlines = [ProductImageInline]

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent')
    search_fields = ('name',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image', 'order')
    list_filter = ('product',)


























from django.core.exceptions import ImproperlyConfigured
from django.contrib import admin

from django.contrib.auth.models import Group

from rest_framework.authtoken.models import Token, TokenProxy

from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
)

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)

def safe_unregister(model):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass



safe_unregister(Group)

safe_unregister(Token)
safe_unregister(TokenProxy)



safe_unregister(PeriodicTask)
safe_unregister(IntervalSchedule)
safe_unregister(CrontabSchedule)
safe_unregister(SolarSchedule)
safe_unregister(ClockedSchedule)



safe_unregister(OutstandingToken)
safe_unregister(BlacklistedToken)