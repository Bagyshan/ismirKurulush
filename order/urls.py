from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CartItemViewSet, OrderRequestCreateView, OrderRequestListByUserView

router = DefaultRouter()
# подключаем наборы через basename и viewset actions
router.register(r'cart', CartViewSet, basename='cart')
# router.register(r'cart-items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    # path('order/request/', OrderRequestCreateAPIView.as_view(), name='order-request'),
    path('order-request/', OrderRequestCreateView.as_view(), name='order-create'),
    path('order-requests-by-user/', OrderRequestListByUserView.as_view(), name='order-requests-by-user'),
]