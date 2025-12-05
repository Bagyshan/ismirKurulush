import django_filters
from django_filters import rest_framework as filters
from .models import Product, Brand, Category
from django.db.models import Q

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    brand = filters.ModelMultipleChoiceFilter(field_name='brand__id', to_field_name='id', queryset=Brand.objects.all())
    categories = filters.ModelMultipleChoiceFilter(field_name='categories__id', to_field_name='id', queryset=Category.objects.all())
    category = filters.NumberFilter(method='filter_category_with_children')
    in_stock = filters.BooleanFilter(method='filter_in_stock')
    search = filters.CharFilter(method='fulltext_search')  # общий поисковый параметр

    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'brand', 'categories', 'category', 'in_stock', 'search']



    def filter_category_with_children(self, queryset, name, value):
        """
        Фильтрация по одной категории с учетом всех потомков.
        """
        try:
            category = Category.objects.get(id=value)
        except Category.DoesNotExist:
            return queryset

        all_ids = category.get_descendants()
        return queryset.filter(categories__id__in=all_ids)


    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(quantity__gt=0) if value else queryset

    def fulltext_search(self, queryset, name, value):
        # Простая fallback-реализация: поиск по name/description/brand
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__name__icontains=value)
        )
