from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from config.settings import tg_token

from main.serializers import ProductSerializer, CartItemSerializer, ProductRetrieveSerializer
from main.filters import ProductFilter
from main.models import Product, RecommendedProducts, Cart, CartItem, Promo, PromoUsage, Order
from main.tasks import send_telegram_message, send_email_message
from main.pagination import ProductPagination
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
                {"message": "Product added to cart successfully"},
                {
                    'cart_id': cart.id,
                    'product_id': cart_item.product.id,
                    'quantity': cart_item.quantity
                }
            ]
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


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
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            product = Product.objects.get(pk=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if cart_item.quantity >= 1:
                cart_item.quantity -= 1
                cart_item.save()
                return Response([
                    {"message": "Product removed from cart successfully"},
                    {'details':
                        {
                            'cart_id': cart.id,
                            'product_id': cart_item.product.id,
                            'quantity': cart_item.quantity
                        }}
                    ],
                    status=status.HTTP_200_OK)
            else:
                return Response({"error": "Product is not in the cart"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


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
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        cart_items = cart.cartitem_set.all()
        cart_data = []
        total_amount = 0

        for cart_item in cart_items:
            item_data = CartItemSerializer(cart_item).data
            item_data['total_price'] = cart_item.quantity * cart_item.product.price
            total_amount += item_data['total_price']
            cart_data.append(item_data)

        cart.total_amount = total_amount
        cart.save()

        # Применение скидки к общей сумме корзины, если есть промокод
        if cart.promo:
            promo = cart.promo
            if promo.discount_percentage:
                discount_amount = total_amount * (promo.discount_percentage / 100)
                total_amount -= discount_amount
            elif promo.promo_product:
                # Добавление товара из промоакции со стоимостью 0
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=promo.promo_product)
                if created:
                    cart_item.quantity = 1
                    cart_item.save()
                total_amount += 0  # Не учитываем стоимость товара из промоакции

        # Добавление общей суммы корзины с учетом скидки в ответ
        response_data = {
            "cart_items": cart_data,
            "total_amount": total_amount
        }
        return Response(response_data, status=status.HTTP_200_OK)


class ApplyPromoCode(APIView):
    @login_required
    def post(self, request):
        promo_code = request.data.get('promo_code')

        # Проверка наличия промокода в базе данных
        try:
            promo = Promo.objects.get(title=promo_code)
        except Promo.DoesNotExist:
            return Response({"error": "Promo code not found"}, status=status.HTTP_404_NOT_FOUND)

        # Проверка максимального количества использований промокода для текущего пользователя
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)
        if PromoUsage.objects.filter(user=user, promo=promo).count() >= promo.max_usage_count:
            return Response({"error": "Maximum usage limit reached for this promo code"},
                            status=status.HTTP_403_FORBIDDEN)

        cart.promo = promo
        cart.save()
        return Response({"success": "Promo code applied successfully"}, status=status.HTTP_200_OK)


class PlaceOrder(APIView):
    def post(self, request):
        payment_method = request.data.get('payment_method')
        delivery_method = request.data.get('delivery_method')
        buyer_name = request.data.get('name')
        buyer_phone = request.data.get('phone')
        address = request.data.get('address')

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
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.create(
            buyer=user,
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            delivery_address=address,
            order_amount=cart.total_amount,
            payment_method=payment_method,
            delivery_method=delivery_method,
            promo=cart.promo
        )

        for cart_item in cart.cartitem_set.all():
            order.products.add(cart_item)

        send_telegram_message(tg_token, order)
        send_email_message(order)

        #  if payment_method == 'online':
        #      return redirect()

        cart.total_amount = 0
        if cart.promo:
            cart.promo = None
        cart.save()
        cart.cartitem_set.all().delete()

        return Response({'success': f'Order {order.id} placed successfully'})
