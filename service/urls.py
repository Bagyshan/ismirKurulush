from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ServiceDetailView, ServiceListView

router = DefaultRouter()
# подключаем наборы через basename и viewset actions
# router.register(r'cart-items', CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/<int:pk>/', ServiceDetailView.as_view(), name='service-detail'),
]