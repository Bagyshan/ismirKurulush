from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CartItemViewSet, OrderRequestCreateAPIView

router = DefaultRouter()
# подключаем наборы через basename и viewset actions
router.register(r'cart', CartViewSet, basename='cart')
# router.register(r'cart-items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    # path('order/request/', OrderRequestCreateAPIView.as_view(), name='order-request'),
]