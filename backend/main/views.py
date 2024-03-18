from decimal import Decimal
from datetime import datetime, time, timedelta
from pytz import timezone

from django.db import IntegrityError, DataError
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from config.settings import tg_token

from main.serializers import ProductSerializer, ProductRetrieveSerializer, OrderSerializer
from main.filters import ProductFilter
from main.models import Product, RecommendedProducts, Cart, CartItem, Promo, PromoUsage, Order, OrderItem, HappyHours
from main.tasks import send_telegram_message, send_email_message
from main.pagination import ProductPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    filterset_fields = ['category']
    pagination_class = ProductPagination

    def get_queryset(self):
        category_ids_str = self.request.query_params.get('categories', '')
        category_ids = category_ids_str.split(',')
        category_ids = [int(category_id) for category_id in category_ids if category_id.isdigit()]

        queryset = Product.objects.filter(is_hidden=False).order_by('id')
        if category_ids:
            queryset = queryset.filter(category_id__in=category_ids)
        return queryset


class ProductRetrieveAPIView(RetrieveAPIView):
    serializer_class = ProductRetrieveSerializer
    queryset = Product.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_hidden:
            return Response({'detail': 'Product is not available'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class AddToCart(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity',
                                    1)  # Если количество не указано, то по умолчанию 1, предполагается нажатие на "+"

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        if user:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(session_id=session_id)

        try:
            product = Product.objects.get(pk=product_id)
            if product.is_hidden:
                return Response({'error': 'Cannot added hidden product'}, status=status.HTTP_400_BAD_REQUEST)

            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()
            response_data = [
                {"message": 'Product added to cart successfully'},
                {
                    'cart_id': cart.id,
                    'product_id': cart_item.product.id,
                    'quantity': cart_item.quantity
                }
            ]
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class RemoveFromCart(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        try:
            if user:
                cart = Cart.objects.get(user=user)
            else:
                session_id = request.session.session_key
                cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(pk=product_id)

            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                if cart_item.quantity > 0:
                    cart_item.quantity -= 1
                    if cart_item.quantity == 0:
                        cart_item.delete()
                        return Response(
                            {'message': 'Product deleted from cart'},
                            status=status.HTTP_200_OK)
                    else:
                        cart_item.save()
                        return Response([
                            {'message': 'Product removed from cart successfully'},
                            {'details':
                                {
                                    'cart_id': cart.id,
                                    'product_id': cart_item.product.id,
                                    'quantity': cart_item.quantity
                                }}
                            ],
                            status=status.HTTP_200_OK)
            except CartItem.DoesNotExist:
                return Response({'error': 'Product is not in the cart'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


class CartView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        try:
            if user:
                cart = Cart.objects.get(user=user)
            else:
                session_id = request.session.session_key
                cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = CartItem.objects.filter(cart=cart.id)
        cart_data = []
        total_amount = 0

        moscow_timezone = timezone('Europe/Moscow')
        current_time = datetime.now(moscow_timezone).time()

        try:
            happy_hours = HappyHours.objects.get(is_active=True)
        except HappyHours.DoesNotExist:
            happy_hours = None

        is_weekday = datetime.now().weekday() < 5

        for cart_item in cart_items:
            price = cart_item.product.temporary_price if cart_item.product.temporary_price else cart_item.product.price

            if cart_item.product.category.title.lower() == 'напитки':
                total_price = cart_item.quantity * price
            elif happy_hours and is_weekday and happy_hours.time_to_start <= current_time <= happy_hours.time_to_end:
                discount_percentage = happy_hours.discount_percentage
                total_price = (cart_item.quantity * price) * (100 - discount_percentage) / 100
            else:
                total_price = cart_item.quantity * price

            item_data = {
                'product_id': cart_item.product.id,
                'title': cart_item.product.title,
                'quantity': cart_item.quantity,
                'price': price,
                'total_price': total_price
            }
            cart_data.append(item_data)
            total_amount += total_price

        cart.total_amount = total_amount
        cart.save()

        # Применение скидки к общей сумме корзины, если есть промокод
        if cart.promo:
            promo = cart.promo
            if promo.discount_percentage:
                discount_amount = total_amount * (Decimal(promo.discount_percentage) / 100)
                total_amount_with_discount = total_amount - discount_amount
                cart.total_amount = total_amount_with_discount
                cart.save()
                response_data = {
                    'cart_items': cart_data,
                    'total_amount': cart.total_amount,
                    'total_amount_with_discount': total_amount_with_discount
                }
                return Response(response_data, status=status.HTTP_200_OK)
            elif promo.promo_product:
                promo_product_data = {
                    'product_id': promo.promo_product.id,
                    'title': promo.promo_product.title,
                    'quantity': 1,
                    'price': 0,
                    'total_price': 0
                }
                cart_data.append(promo_product_data)

        response_data = {
            'cart_items': cart_data,
            'total_amount': cart.total_amount
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ApplyPromoCode(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        promo_code = request.data.get('promo_code')

        try:
            promo = Promo.objects.get(title=promo_code)
        except Promo.DoesNotExist:
            return Response({'error': 'Promo code not found'}, status=status.HTTP_404_NOT_FOUND)

        # Проверка максимального количества использований промокода для текущего пользователя
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        if PromoUsage.objects.filter(user=user, promo=promo).count() >= promo.max_usage_count:
            return Response({'error': 'Maximum usage limit reached for this promo code'},
                            status=status.HTTP_403_FORBIDDEN)

        cart.promo = promo
        cart.save()
        return Response({'message': 'Promo code applied successfully'}, status=status.HTTP_200_OK)


class OrderCreateAPIView(CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        try:
            if user:
                cart = Cart.objects.get(user=user)
            else:
                session_id = request.session.session_key
                cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        payment_method = request.data.get('payment_method')
        if payment_method == 'online':
            return Response(
                {'error': 'Online payment method is temporarily unavailable. Please choose payment "to_courier".'},
                status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data,
                                         context={'user': user, 'session_key': request.session.session_key})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        order = serializer.instance

        for cart_item in cart.cartitem_set.all():
            price = cart_item.product.temporary_price if cart_item.product.temporary_price else cart_item.product.price
            OrderItem.objects.create(order=order, product=cart_item.product,
                                     quantity=cart_item.quantity, price=price)

        send_telegram_message(tg_token, order)
        send_email_message(order)

        #  if payment_method == 'online':
        #      return redirect()

        #  TODO: добавить последний адрес заказа, увеличить сумму заказов пользователя в поля User (тоже самое после ответа платежки)
        if user:
            user.address = serializer.validated_data.get('delivery_address')
            user.total_amount += order.order_amount

        if cart.promo:
            #  TODO: добавить использование промо в PromoUsage (тоже самое после ответа платежки)
            promo_usage, created = PromoUsage.objects.get_or_create(user=user, promo=cart.promo)
            promo_usage.usage_count += 1
            promo_usage.save()

            cart.promo.current_usage_count += 1
            cart.promo.save()

        cart.delete()

        return Response({'message': f'Order {order.id} placed successfully'})
