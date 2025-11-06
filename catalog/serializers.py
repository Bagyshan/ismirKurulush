from rest_framework import serializers
from .models import (
    Product, 
    ProductImage, 
    # Characteristic, 
    # Review, 
    Brand, 
    Category
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt', 'order']


    def get_image(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        if request:
            return request.build_absolute_uri(obj.image.url)
        # fallback если сериализатор используется без HTTP-контекста
        from django.conf import settings
        return f"{settings.SITE_DOMAIN}{obj.image.url}"

# class CharacteristicSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Characteristic
#         fields = ['key', 'value']

# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = ['id', 'author_name', 'rating', 'text', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug']

class ProductListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    categories = CategorySerializer(read_only=True, many=True)
    main_image = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id','name','slug','brand','categories','price','currency','main_image','in_stock','popularity_score','created_at']

    def get_main_image(self, obj):
        img = obj.images.first()
        if not img or not img.image:
            return None
        
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(img.image.url)

        from django.conf import settings
        return f"{settings.SITE_DOMAIN}{img.image.url}"

    def get_in_stock(self, obj):
        return obj.in_stock()

class ProductDetailSerializer(serializers.ModelSerializer):
    # images = ProductImageSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    # characteristics = CharacteristicSerializer(many=True, read_only=True)
    # reviews = ReviewSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    similar = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'  # можно ограничить
        read_only_fields = ['search_vector', 'popularity_score']

    def get_images(self, obj):
        return ProductImageSerializer(obj.images.all(), many=True, context=self.context).data

    def get_similar(self, obj):
        similar_products = obj.get_similar(limit=10)
        return ProductListSerializer(similar_products, many=True, context=self.context).data
