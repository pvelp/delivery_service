from rest_framework import serializers

from main.models import Product, CartItem, RecommendedProducts, Order, Cart
from main.validators import PhoneNumberValidator, BuyerNameValidator, AddressValidator, PaymentMethodValidator, DeliveryMethodValidator


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'weight', 'measure',
                  'category', 'image', 'price']

    def get_price(self, obj):
        if obj.temporary_price:
            return obj.temporary_price
        else:
            return obj.price


class RecommendedProductsSerializer(serializers.ModelSerializer):
    product_1 = ProductSerializer()
    product_2 = ProductSerializer()
    product_3 = ProductSerializer()

    class Meta:
        model = RecommendedProducts
        fields = ['product_1', 'product_2', 'product_3']


class ProductRetrieveSerializer(serializers.ModelSerializer):
    recommended_products = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'weight', 'measure',
                  'category', 'image', 'price', 'recommended_products']

    def get_recommended_products(self, obj):
        recommended_products = RecommendedProducts.objects.first()
        if recommended_products:
            serializer = RecommendedProductsSerializer(recommended_products)
            return serializer.data
        return {}

    def get_price(self, obj):
        if obj.temporary_price:
            return obj.temporary_price
        else:
            return obj.price


class OrderSerializer(serializers.ModelSerializer):
    buyer_phone_number = serializers.CharField(validators=[PhoneNumberValidator('buyer_phone_number')])
    delivery_address = serializers.CharField(validators=[AddressValidator('delivery_address')])
    buyer_name = serializers.CharField(validators=[BuyerNameValidator('buyer_name')])
    payment_method = serializers.CharField(validators=[PaymentMethodValidator('payment_method')])
    delivery_method = serializers.CharField(validators=[DeliveryMethodValidator('delivery_method')])

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        user = self.context.get('user')

        if user:
            cart = Cart.objects.get(user=user)
        else:
            session_id = self.context.get('session_key')
            cart = Cart.objects.get(session_id=session_id)

        order = Order.objects.create(
            buyer=user,
            buyer_name=validated_data['buyer_name'],
            buyer_phone_number=validated_data['buyer_phone_number'],
            delivery_address=validated_data['delivery_address'],
            order_amount=cart.total_amount,
            payment_method=validated_data['payment_method'],
            delivery_method=validated_data['delivery_method'],
            promo=cart.promo
        )

        return order
