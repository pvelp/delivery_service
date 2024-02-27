from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from config.settings import tg_token

from main.serializers import ProductSerializer, CartItemSerializer
from main.filters import ProductFilter
from main.models import Product, RecommendedProducts, Cart, CartItem, Promo, PromoUsage, Order
from main.tasks import send_telegram_message, send_email_message
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    filterset_fields = ['category']
    pagination_class = PageNumberPagination
    pagination_class.page_size = 12

    def get_queryset(self):
        category_ids = self.request.query_params.getlist('categories', [])
        if category_ids:
            return Product.objects.filter(category_id__in=category_ids)
        return Product.objects.all()


class ProductRetrieveAPIView(RetrieveAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recommended_products'] = self.get_recommended_products()
        return context

    def get_recommended_products(self):
        product_id = self.kwargs.get('pk')
        try:
            recommended_products = RecommendedProducts.objects.get(pk=product_id)
            return {
                'product_1': recommended_products.product_1,
                'product_2': recommended_products.product_2,
                'product_3': recommended_products.product_3
            }
        except RecommendedProducts.DoesNotExist:
            return {}


class AddToCart(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)  # Если количество не указано, то по умолчанию 1, предполагается нажатие на "+"

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
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.quantity += quantity
            cart_item.save()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

        # Удаление товара из корзины
        try:
            product = Product.objects.get(pk=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            return Response({"message": "Product removed from cart successfully"}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({"error": "Product is not in the cart"}, status=status.HTTP_404_NOT_FOUND)


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
            return Response({"error": "Maximum usage limit reached for this promo code"}, status=status.HTTP_403_FORBIDDEN)

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
