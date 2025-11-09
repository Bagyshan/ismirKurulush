from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Favorite
from .serializers import FavoriteSerializer
from catalog.models import Product
from django.db import models

# Create your views here.
class FavoriteListView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class ToggleFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        user = request.user
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Объявление не найдено'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=user, product=product)
        if not created:
            favorite.delete()
            product.favorites_count = models.F('favorites_count') - 1
            product.save(update_fields=['favorites_count'])
            return Response({'detail': 'Удалено из избранного'}, status=status.HTTP_200_OK)

        product.favorites_count = models.F('favorites_count') + 1
        product.save(update_fields=['favorites_count'])
        return Response({'detail': 'Добавлено в избранное'}, status=status.HTTP_201_CREATED)