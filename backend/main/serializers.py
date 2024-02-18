from rest_framework import serializers

from main.models import Product, CartItem


class ProductSerializer(serializers.Serializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'weight', 'measure', 'category', 'image']

        def to_representation(self, instance):
            data = super().to_representation(instance)
            if instance.is_hidden:
                return None

            if instance.temporary_price and instance.temporary_price != 0:
                data['price'] = instance.temporary_price
            elif instance.price and instance.price != 0:
                data['price'] = instance.price
            else:
                return None

            return data


class CartItemSerializer(serializers.Serializer):
    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
