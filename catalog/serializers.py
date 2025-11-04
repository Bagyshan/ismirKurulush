from rest_framework import serializers
from .models import (
    Product, 
    ProductImage, 
    # Characteristic, 
    # Review, 
    Brand, 
    Category
)

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt', 'order']

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
        fields = ['id','name','slug','brand','categories','price','currency','main_image','in_stock','popularity_score']

    def get_main_image(self, obj):
        img = obj.images.first()
        return img.image.url if img else None

    def get_in_stock(self, obj):
        return obj.in_stock()

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    # characteristics = CharacteristicSerializer(many=True, read_only=True)
    # reviews = ReviewSerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    similar = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'  # можно ограничить
        read_only_fields = ['search_vector', 'popularity_score']

    def get_similar(self, obj):
        similar_products = obj.get_similar(limit=10)
        return ProductListSerializer(similar_products, many=True, context=self.context).data
