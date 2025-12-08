from django.shortcuts import render

# Create your views here.
from rest_framework import generics, filters as drf_filters
from django_filters import rest_framework as django_filters
from .models import Product, Category, Brand
from .serializers import ProductListSerializer, ProductDetailSerializer, CategorySerializer, BrandSerializer, CategoryTreeSerializer
from .filters import ProductFilter
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .caches import get_product_details
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import increment_product_view


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_published=True).select_related('brand').prefetch_related('categories','images')
    serializer_class = ProductListSerializer
    filter_backends = [django_filters.DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price','created_at','popularity_score']
    ordering = ['-created_at']
    pagination_class = None  # заменить на PageNumberPagination в проде

    # пример кэширования на уровне view (по URL + query params)
    @method_decorator(cache_page(60*2))  # 2 минуты
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_published=True).select_related('brand').prefetch_related('categories','images'
                                                                                                #   ,'characteristics','reviews'
                                                                                                  )
    serializer_class = ProductDetailSerializer
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs.get(self.lookup_field)

        # достаем данные из кеша или формируем заново
        data = get_product_details(product_id, context={"request": request})

        # инкремент popular_score (через Redis счетчик)
        increment_product_view(data["id"])

        return Response(data)

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


# @extend_schema(
#     summary="Получение категорий",
#     description=(
#         "Возвращает список категорий. "
#         "Поддерживает два режима фильтрации:\n"
#         "- `category_id`: вернуть категорию и все её дочерние (рекурсивно)\n"
#         "- `root_only`: вернуть только корневые категории (parent=null)"
#     ),
#     parameters=[
#         OpenApiParameter(
#             name="category_id",
#             type=OpenApiTypes.INT,
#             location=OpenApiParameter.QUERY,
#             required=False,
#             description="ID категории. Возвращает её и все дочерние категории."
#         ),
#         OpenApiParameter(
#             name="root_only",
#             type=OpenApiTypes.BOOL,
#             location=OpenApiParameter.QUERY,
#             required=False,
#             description="Флаг. Если true/1 — возвращает только родительские категории."
#         ),
#     ],
#     responses={
#         200: CategorySerializer(many=True),
#         400: OpenApiTypes.OBJECT,
#     },
# )
# class CategoryListView(generics.ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     pagination_class = None

#     def get_queryset(self):
#         qs = Category.objects.all()

#         # фильтрация по дочерним категориям
#         category_id = self.request.query_params.get('category_id')
#         if category_id:
#             try:
#                 category = Category.objects.get(id=category_id)
#             except Category.DoesNotExist:
#                 return Category.objects.none()

#             ids = category.get_descendants()  # рекурсивный сбор ID
#             return qs.filter(id__in=ids)

#         # фильтрация только по родительским категориям
#         root_only = self.request.query_params.get('root_only')
#         if root_only in ['1', 'true', 'True']:
#             return qs.filter(parent__isnull=True)

#         return qs

@extend_schema(
    summary="Получение категорий в древовидной структуре",
    description=(
        "Возвращает категории в виде дерева. "
        "`category_id` — вернуть дерево, начиная с конкретной категории. "
        "`root_only` — вернуть только корневые узлы."
    ),
    parameters=[
        OpenApiParameter(
            name="category_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=False,
            description="ID категории. Возвращает дерево, начиная с неё."
        ),
        OpenApiParameter(
            name="root_only",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Если true/1 — вернуть только категории верхнего уровня."
        ),
    ],
    responses={200: CategoryTreeSerializer(many=True)},
)
class CategoryTreeView(generics.ListAPIView):
    serializer_class = CategoryTreeSerializer
    pagination_class = None

    def get_queryset(self):
        qs = Category.objects.all()

        category_id = self.request.query_params.get('category_id')
        if category_id:
            try:
                return Category.objects.filter(id=category_id)
            except Category.DoesNotExist:
                return Category.objects.none()

        root_only = self.request.query_params.get('root_only')
        if root_only in ["1", "true", "True"]:
            return Category.objects.filter(parent__isnull=True)

        # дефолт: отдаём только корневые категории в дереве
        return Category.objects.filter(parent__isnull=True)

class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = None



class SortingOptionsView(APIView):
    """
    Допустимые параметры сортировки.
    """
    SORTING_OPTIONS = {
        "lowest_price": {
        "name": "Самая низкая цена",
        "value": "price"
        },
        "highest_price": {
        "name": "Самая высокая цена",
        "value": "-price"
        },
        "newest": {
        "name": "Новинки",
        "value": "-created_at"
        },
        "oldest": {
        "name": "Самые старые",
        "value": "created_at"
        },
        "most_popular": {
        "name": "Самые популярные",
        "value": "-popularity_score"
        },
        "least_popular": {
        "name": "Наименее популярные",
        "value": "popularity_score"
        }
    }


    def get(self, request):
        return Response(
            {"sorting_options": self.SORTING_OPTIONS},
            status=status.HTTP_200_OK
        )