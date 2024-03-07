from rest_framework import serializers

from main.models import Product, CartItem, RecommendedProducts


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'weight', 'measure',
                  'category', 'image', 'price', 'temporary_price']


class RecommendedProductsSerializer(serializers.ModelSerializer):
    product_1 = ProductSerializer()
    product_2 = ProductSerializer()
    product_3 = ProductSerializer()

    class Meta:
        model = RecommendedProducts
        fields = ['product_1', 'product_2', 'product_3']


class ProductRetrieveSerializer(serializers.ModelSerializer):
    recommended_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'weight', 'measure',
                  'category', 'image', 'price', 'temporary_price', 'recommended_products']

    def get_recommended_products(self, obj):
        recommended_products = RecommendedProducts.objects.first()
        if recommended_products:
            serializer = RecommendedProductsSerializer(recommended_products)
            return serializer.data
        return {}
