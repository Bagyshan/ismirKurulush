from django.shortcuts import render

# Create your views here.
from django.db import transaction
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .tasks import send_order_to_telegram

from .models import Cart, CartItem, Product, OrderRequest
from .serializers import (
    CartAddSerializer, CartRemoveSerializer, CartSerializer, CartItemSerializer, CartItemCreateSerializer, CartUpdateSerializer,
    OrderRequestSerializer
)

session_header = openapi.Parameter(
    name='X-Session-Id',
    in_=openapi.IN_HEADER,
    type=openapi.TYPE_STRING,
    required=False,
    description='ID сессии для анонимной корзины (не требуется для авторизованных пользователей)',
)


def _get_session_id(request):
    # ожидание: фронт отправляет заголовок X-Session-Id для анонимных
    return request.headers.get('X-Session-Id') or request.query_params.get('session_id')


def _get_or_create_cart(request, create=True):
    user = request.user if request.user.is_authenticated else None
    session_id = _get_session_id(request)

    if user:
        cart, _ = Cart.objects.get_or_create(user=user)
        # если есть анонимный cart, можно выполнить merge (опционально)
        if session_id:
            try:
                anon = Cart.objects.get(session_id=session_id, user__isnull=True)
                # merge anon -> user cart
                for item in anon.items.all():
                    existing = cart.items.filter(product=item.product).first()
                    if existing:
                        existing.quantity = existing.quantity + item.quantity
                        existing.save()
                    else:
                        item.cart = cart
                        item.save()
                anon.delete()
            except Cart.DoesNotExist:
                pass
        return cart

    if session_id:
        cart, _ = Cart.objects.get_or_create(session_id=session_id, user=None)
        return cart

    if not create:
        return None

    # fallback: создать временный cart и вернуть его. Фронт должен получить cart.id
    cart = Cart.objects.create(session_id=str(timezone.now().timestamp()))
    return cart


class CartViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="X-Session-ID", location=OpenApiParameter.HEADER, required=False, type=str),
        ],
        responses={
            200: CartSerializer,
        },
        summary="Получить корзину",
        description="Возвращает все товары, добавленные в корзину по session_id."
    )
    def list(self, request):
        cart = _get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    


    
    @extend_schema(
        parameters=[
            OpenApiParameter(name="X-Session-ID", location=OpenApiParameter.HEADER, required=False, type=str),
        ],

        request=CartAddSerializer,
        responses={200: CartSerializer},
        summary="Добавить товар в корзину",
        description="Добавляет товар в корзину по session_id."
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Добавить товар в корзину или увеличить количество"""
        cart = _get_or_create_cart(request)
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart, product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                item.quantity = item.quantity + quantity
                item.save()

        cart_serializer = CartSerializer(cart)

        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)





    @extend_schema(
        parameters=[
            OpenApiParameter(name="X-Session-ID", location=OpenApiParameter.HEADER, required=False, type=str),
        ],
        request=CartUpdateSerializer,
        responses={200: CartSerializer},
        summary="Обновить количество товара",
        description="Изменяет количество позиции в корзине."
    )
    @action(detail=False, methods=['patch'])
    # def update_item(self, request):
    #     """Изменить количество позиции"""
    #     item_id = request.data.get('id')
    #     if not item_id:
    #         return Response({'detail': 'item id is required'}, status=400)
    #     item = get_object_or_404(CartItem, pk=item_id)
    #     serializer = CartItemCreateSerializer(item, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response({'status': 'ok'})
    def update_item(self, request):
        serializer = CartUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data['item_id']
        quantity = serializer.validated_data['quantity']

        cart = _get_or_create_cart(request, create=False)
        if not cart:
            return Response({'detail': 'Cart not found'}, status=404)

        item = get_object_or_404(CartItem, pk=item_id, cart=cart)

        item.quantity = quantity
        item.save()

        cart_serializer = CartSerializer(cart)

        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    





    @extend_schema(
        parameters=[
            OpenApiParameter(name="X-Session-ID", location=OpenApiParameter.HEADER, required=False, type=str),
        ],
        request=CartRemoveSerializer,
        responses={200: CartSerializer},
        summary="Удалить товар из корзины",
        description="Удаляет товар из корзины по session_id.",
        # request_body=CartRemoveSerializer
    )
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        # item_id = request.data.get('id')
        # if not item_id:
        #     return Response({'detail': 'item id is required'}, status=400)
        # item = get_object_or_404(CartItem, pk=item_id)
        # item.delete()
        # return Response(status=status.HTTP_204_NO_CONTENT)
    
        serializer = CartRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data['item_id']

        cart = _get_or_create_cart(request, create=False)
        if not cart:
            return Response({'detail': 'Cart not found'}, status=404)

        item = get_object_or_404(CartItem, pk=item_id, cart=cart)

        item.delete()

        cart_serializer = CartSerializer(cart)

        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    





    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(name="X-Session-ID", location=OpenApiParameter.HEADER, required=False, type=str),
    #     ]
    # )
    # @action(detail=False, methods=['post'])
    # def checkout(self, request):
    #     """Сохранение заказа (минимальный пример). В продакшне сюда добавляется оплата, адреса и т.д."""
    #     cart = _get_or_create_cart(request, create=False)
    #     if not cart:
    #         return Response({'detail': 'Cart not found'}, status=404)

    #     # В этой версии checkout просто переводит cart в readonly заказную сущность -- не реализуем сейчас
    #     # Вернём текущее состояние корзины
    #     serializer = CartSerializer(cart)
    #     return Response(serializer.data)


class CartItemViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def retrieve(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemSerializer(item)
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        serializer = CartItemCreateSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CartItemSerializer(item).data)  
      
    def destroy(self, request, pk=None):
        item = get_object_or_404(CartItem, pk=pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)







class OrderRequestCreateView(generics.CreateAPIView):
    queryset = OrderRequest.objects.all()
    serializer_class = OrderRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Сохраняем заявку
        order = serializer.save(user=user)
        
        # Отправляем в Telegram канал через Celery
        send_order_to_telegram.delay(order.id)
        
        return Response(
            {
                'status': 'success',
                'message': 'Заявка успешно отправлена',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class OrderRequestListByUserView(generics.ListAPIView):
    queryset = OrderRequest.objects.all()
    serializer_class = OrderRequestSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)