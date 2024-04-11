from django.http import HttpResponseRedirect
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from config.settings import tg_token

from main.services import calculate_cart
from main.serializers import ProductSerializer, ProductRetrieveSerializer, OrderSerializer, CategorySerializer
from main.filters import ProductFilter
from main.models import Product, RecommendedProducts, Cart, CartItem, Promo, PromoUsage, Order, OrderItem, HappyHours, Category
from main.tasks import send_telegram_message, send_email_message
from main.pagination import ProductPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class ProductListAPIView(ListAPIView):
    #  TODO: список категорий
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        context['categories'] = serializer.data
        return context


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
    """
    Контроллер отвечает за добавление товара в корзину
    """

    @swagger_auto_schema(
        operation_description="Добавляет товар в корзину",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID продукта'),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара (по умолчанию 1)'),
            }
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Сообщение об успешном добавлении'),
                        'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID корзины'),
                        'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID продукта в корзине'),
                        'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара в корзине'),
                    }
                )
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Ошибка при добавлении товара'),
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Продукт не найден'),
                }
            ),
        }
    )
    def post(self, request):
        """
        Добавляет товар в корзину
        """
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

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
    """
        Контроллер отвечает за удаление товара из корзины.
        """

    @swagger_auto_schema(
        operation_description="Удаляет товар из корзины",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                             description='ID продукта, который нужно удалить из корзины.')
            }
        ),
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING,
                                                  description='Сообщение об успешном удалении товара из корзины'),
                        'details': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'cart_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID корзины'),
                                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                             description='ID удаленного продукта из корзины'),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                           description='Количество товара в корзине после удаления')
                            }
                        )
                    }
                )
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Продукт не найден в корзине'),
                }
            )
        }
    )
    def post(self, request):
        """
        Удаляет одну единицу товара из корзины.

        """
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
    """
        Контроллер для просмотра содержимого корзины.
        Считается корзина - обязательный контроллерр
        """

    @swagger_auto_schema(
        operation_description="Получение содержимого корзины",
        responses={
            status.HTTP_200_OK: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'cart_items': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID продукта'),
                                'title': openapi.Schema(type=openapi.TYPE_STRING, description='Название продукта'),
                                'image': openapi.Schema(type=openapi.TYPE_STRING, description='URL картинки'),
                                'weight': openapi.Schema(type=openapi.TYPE_INTEGER, description='Вес продукта'),
                                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Количество товара'),
                                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Цена товара'),
                                'total_price': openapi.Schema(type=openapi.TYPE_NUMBER,
                                                              description='Общая стоимость товара'),
                            }
                        )
                    ),
                    'total_amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Общая стоимость корзины'),
                    'total_amount_with_discount': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description='Общая стоимость корзины с учетом скидки (если применяется, если нет None)'
                    ),
                    'happy_hours': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Акция счастливые часы')
                }
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Корзина не найдена'),
                }
            )
        }
    )
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

        response_data = calculate_cart(cart)

        return Response(response_data, status=status.HTTP_200_OK)


class ApplyPromoCode(APIView):
    """
       Контроллер для применения промокодов к корзине.
       """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Применение промокода к корзине",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'promo_code': openapi.Schema(type=openapi.TYPE_STRING, description='Промокод'),
            }
        ),
        responses={
            status.HTTP_302_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
            ),
            status.HTTP_404_NOT_FOUND: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, description='Промокод не найден'),
                }
            ),
            status.HTTP_403_FORBIDDEN: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING,
                                            description='Достигнут предел использования этого промокода'),
                }
            ),
        }
    )
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
        # return Response({'message': 'Promo code applied successfully'}, status=status.HTTP_200_OK)  # TODO: или редирект
        return HttpResponseRedirect(reverse('main:cart'))


class OrderCreateAPIView(CreateAPIView):
    serializer_class = OrderSerializer
    #  TODO: Добавить пересчет страницы как на гет к корзине

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

        calculate_cart(cart)  # пересчитываем корзину, если пользователь вносил изменению на странице с корзиной без обновления

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
            user.address = order.delivery_address
            user.total_amount += order.order_amount

        if cart.promo:
            #  TODO: добавить использование промо в PromoUsage (тоже самое после ответа платежки)
            promo_usage, created = PromoUsage.objects.get_or_create(user=user, promo=cart.promo)
            promo_usage.usage_count += 1
            promo_usage.save()

            cart.promo.current_usage_count += 1
            cart.promo.save()

        cart.delete()

        return Response({'message': f'Order {order.id} placed successfully'}, status=status.HTTP_201_CREATED)
