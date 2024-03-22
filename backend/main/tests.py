#  TODO: Добавить тесты на все реальзованные эндпоинты (остался 1 - создание заказа)

from decimal import Decimal
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from main.models import Category, Product, RecommendedProducts, Promo, CartItem, Cart, PromoUsage, HappyHours
from users.models import User


class ProductListTestCase(APITestCase):

    def setUp(self):
        self.products_url = 'http://localhost:8000/products/'
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.category2 = Category.objects.create(
            title='Напитки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            title='шашлык2',
            price=600,
            category=self.category1
        )
        self.product3 = Product.objects.create(
            title='шашлык3',
            price=400,
            category=self.category1,
            is_hidden=True
        )
        self.product4 = Product.objects.create(
            title='шашлык4',
            price=700,
            category=self.category1
        )
        self.product5 = Product.objects.create(
            title='шашлык5',
            category=self.category1,
            is_hidden=True
        )
        self.product6 = Product.objects.create(
            title='вода',
            price=100,
            category=self.category2
        )
        self.product7 = Product.objects.create(
            title='вода0',
            price=100,
            category=self.category2,
            is_hidden=True
        )
        self.product8 = Product.objects.create(
            title='пепси',
            price=100,
            category=self.category2
        )

    def test_products_200(self):
        response = self.client.get(reverse('main:products'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.maxDiff = None
        self.assertEqual(
            len(response.json()['results']),  # вывод всего списка продуктов, не считая спрятанных товаров
            5
        )

    def test_products_filter_200(self):
        response = self.client.get(self.products_url + '?title=шашлык1')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json()['results'][0]['title'],
            'шашлык1'
        )


class ProductRetrieveTestCase(APITestCase):

    def setUp(self):
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.category2 = Category.objects.create(
            title='Напитки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1,
            temporary_price=200
        )
        self.product2 = Product.objects.create(
            title='шашлык2',
            price=600,
            category=self.category1
        )
        self.product3 = Product.objects.create(
            title='шашлык3',
            price=400,
            category=self.category1,
            is_hidden=True
        )
        self.product4 = Product.objects.create(
            title='шашлык4',
            price=700,
            category=self.category1
        )
        self.product5 = Product.objects.create(
            title='шашлык5',
            category=self.category1,
            is_hidden=True
        )
        self.product6 = Product.objects.create(
            title='вода',
            price=100,
            category=self.category2
        )
        self.product7 = Product.objects.create(
            title='вода0',
            price=100,
            category=self.category2,
            is_hidden=True
        )
        self.product8 = Product.objects.create(
            title='пепси',
            price=100,
            category=self.category2
        )
        self.recommended_products = RecommendedProducts.objects.create(
            product_1=self.product1,
            product_2=self.product2,
            product_3=self.product8,
        )

    def test_get_200(self):
        response = self.client.get(reverse('main:product', kwargs={'pk': self.product1.pk}))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json()['id'],
            self.product1.pk
        )

        self.assertEqual(
            response.json()['price'],
            self.product1.temporary_price
        )

        self.assertEqual(
            response.json()['recommended_products']['product_2']['title'],
            self.product2.title
        )

    def test_not_available_404(self):
        response = self.client.get(reverse('main:product', kwargs={'pk': self.product5.pk}))

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {'detail': 'Product is not available'}
        )


class AddToCartTestCase(APITestCase):

    def setUp(self):
        self.add_to_cart_url = 'http://localhost:8000/add-to-cart/'
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.category2 = Category.objects.create(
            title='Напитки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            title='шашлык3',
            price=400,
            category=self.category1,
            is_hidden=True
        )
        self.product_1_response = {
            'product_id': self.product1.id
        }
        self.product_2_response = {
            'product_id': self.product2.id
        }
        self.product_404_response = {
            'product_id': 10
        }

    def test_add_to_cart_201(self):
        response = self.client.post(
            self.add_to_cart_url,
            self.product_1_response,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.json(),
            [
                {
                    "message": "Product added to cart successfully"
                },
                {
                    "cart_id": 1,
                    "product_id": self.product1.id,
                    "quantity": 1
                }
            ]
        )

    def test_add_to_cart_400(self):
        response = self.client.post(
            self.add_to_cart_url,
            self.product_2_response,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Cannot added hidden product"
            }
        )

    def test_add_to_cart_404(self):
        response = self.client.post(
            self.add_to_cart_url,
            self.product_404_response,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Product not found"
            }
        )


class RemoveFromCartTestCase(APITestCase):

    def setUp(self):
        self.add_to_cart_url = 'http://localhost:8000/add-to-cart/'
        self.remove_from_cart_url = 'http://localhost:8000/remove-from-cart/'
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.category2 = Category.objects.create(
            title='Напитки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            title='шашлык3',
            price=400,
            category=self.category1,
            is_hidden=True
        )
        self.product_1_response = {
            'product_id': self.product1.id
        }
        self.product_2_response = {
            'product_id': self.product2.id
        }
        self.product_404_response = {
            'product_id': 10
        }

    def test_remove_from_cart_200(self):
        self.client.post(
            self.add_to_cart_url,
            self.product_1_response,
        )

        response = self.client.post(
            self.remove_from_cart_url,
            self.product_1_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {
                "message": "Product deleted from cart"
            }
        )

    def test_remove_from_cart_404(self):
        """
        Test remove from cart, but product not in cart. Product's quantity = 0
        """

        self.client.post(
            self.add_to_cart_url,
            self.product_1_response,
        )

        self.client.post(
            self.remove_from_cart_url,
            self.product_1_response
        )

        response = self.client.post(
            self.remove_from_cart_url,
            self.product_1_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Product is not in the cart"
            }
        )

    def test_remove_from_cart_404_not_found(self):
        """
        Test remove from cart, but product doesn't exist
        """

        #  Добавляю любой товар, чтобы создать коризну для пользователя

        self.client.post(
            self.add_to_cart_url,
            self.product_1_response
        )

        response = self.client.post(
            self.remove_from_cart_url,
            self.product_404_response,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Product not found"
            }
        )

    def test_remove_from_cart_not_found(self):
        """
        Test remove from cart, but cart doesn't exist
        """

        response = self.client.post(
            self.remove_from_cart_url,
            self.product_404_response,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Cart not found"
            }
        )


class CartTestCase(APITestCase):

    def setUp(self):
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.category2 = Category.objects.create(
            title='Напитки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            title='шашлык3',
            price=400,
            category=self.category1,
            is_hidden=True
        )
        self.product3 = Product.objects.create(
            title='курица',
            price=200,
            category=self.category2
        )
        self.promo_1 = Promo.objects.create(
            title='2020',
            discount_percentage=10,
            max_usage_count=2,
        )
        self.promo_2 = Promo.objects.create(
            title='1010',
            promo_product=self.product3,
            max_usage_count=1,
        )
        self.user_1 = User.objects.create(
            email='user@example.com',
        )
        self.user_2 = User.objects.create(
            email='user2@example.com',
        )
        self.user_3 = User.objects.create(
            email='user3@example.com'
        )
        self.user_4 = User.objects.create(
            email='user4@example.com'
        )
        self.cart_1 = Cart.objects.create(
            user=self.user_1,
            promo=self.promo_1,
        )
        self.cart_2 = Cart.objects.create(
            user=self.user_2,
            promo=self.promo_2,
        )
        self.cart_3 = Cart.objects.create(
            user=self.user_3,
        )
        self.cart_item_1_1 = CartItem.objects.create(
            cart=self.cart_1,
            product=self.product1,
            quantity=1
        )
        self.cart_item_1_2 = CartItem.objects.create(
            cart=self.cart_1,
            product=self.product3,
            quantity=1
        )
        self.cart_item_2_1 = CartItem.objects.create(
            cart=self.cart_2,
            product=self.product1,
            quantity=2
        )
        self.cart_item_3 = CartItem.objects.create(
            cart=self.cart_3,
            product=self.product3,
            quantity=5
        )
        self.happy_hours = HappyHours.objects.create(
            time_to_start='00:00:00',
            time_to_end='23:59:59',
            discount_percentage=10,
            is_active=False
        )
        #  - поставил статус False, можно вынести в отдельный тест, видно, что скидка работает - реагирует именно на московское время
        #  категорию "Напитки" игнорирует, всё как и ожидалось для этой акции

    def test_cart_not_found(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.get(reverse('main:cart'))

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {'error': 'Cart not found'}
        )

    def test_pure_cart_200(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.get(reverse('main:cart'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.maxDiff = None
        self.assertEqual(
            response.json(),
            {
                'cart_items': [{
                    'price': self.cart_item_3.product.price,
                    'product_id': self.cart_item_3.product.id,
                    'quantity': self.cart_item_3.quantity,
                    'title': self.cart_item_3.product.title,
                    'total_price': self.cart_item_3.quantity * self.cart_item_3.product.price
                }],
                'total_amount': self.cart_item_3.quantity * self.cart_item_3.product.price
            }
        )

    def test_cart_discount_promo_200(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.get(reverse('main:cart'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.maxDiff = None
        self.assertEqual(
            response.json(),
            {
                'cart_items': [
                    {
                        'price': self.cart_item_1_1.product.price,
                        'product_id': self.cart_item_1_1.product.id,
                        'quantity': self.cart_item_1_1.quantity,
                        'title': self.cart_item_1_1.product.title,
                        'total_price': self.cart_item_1_1.quantity * self.cart_item_1_1.product.price
                    },
                    {
                        'price': self.cart_item_1_2.product.price,
                        'product_id': self.cart_item_1_2.product.id,
                        'quantity': self.cart_item_1_2.quantity,
                        'title': self.cart_item_1_2.product.title,
                        'total_price': self.cart_item_1_2.quantity * self.cart_item_1_2.product.price
                    }
                ],
                'total_amount': (self.cart_item_1_1.quantity * self.cart_item_1_1.product.price +
                                 self.cart_item_1_2.quantity * self.cart_item_1_2.product.price),
                'total_amount_with_discount': (self.cart_item_1_1.quantity * self.cart_item_1_1.product.price +
                                               self.cart_item_1_2.quantity * self.cart_item_1_2.product.price) *
                                              (100 - self.cart_1.promo.discount_percentage) / 100
            }
        )

    def test_cart_promo_product_200(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.get(reverse('main:cart'))

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.maxDiff = None
        self.assertEqual(
            response.json(),
            {
                'cart_items': [
                    {
                        'price': self.cart_item_2_1.product.price,
                        'product_id': self.cart_item_2_1.product.id,
                        'quantity': self.cart_item_2_1.quantity,
                        'title': self.cart_item_2_1.product.title,
                        'total_price': self.cart_item_2_1.quantity * self.cart_item_2_1.product.price
                    },
                    {
                        'product_id': self.promo_2.promo_product.id,
                        'title': self.promo_2.promo_product.title,
                        'quantity': 1,
                        'price': 0,
                        'total_price': 0
                    }
                ],
                'total_amount': self.cart_item_2_1.quantity * self.cart_item_2_1.product.price
            }
        )


class PromoTestCase(APITestCase):

    def setUp(self):
        self.promo_url = 'http://localhost:8000/apply-promo-code/'
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1
        )
        self.product3 = Product.objects.create(
            title='курица',
            price=200,
            category=self.category1
        )
        self.promo_1 = Promo.objects.create(
            title='2020',
            discount_percentage=10,
            max_usage_count=2,
        )
        self.promo_2 = Promo.objects.create(
            title='1010',
            promo_product=self.product3,
            max_usage_count=1,
        )
        self.user_1 = User.objects.create(
            email='user@example.com',
        )
        self.user_2 = User.objects.create(
            email='user2@example.com',
        )
        self.user_3 = User.objects.create(
            email='user3@example.com',
        )
        self.cart_1 = Cart.objects.create(
            user=self.user_1,
        )
        self.cart_2 = Cart.objects.create(
            user=self.user_2,
            promo=self.promo_2
        )
        self.cart_3 = Cart.objects.create(
            user=self.user_3,
        )
        self.cart_item_1_1 = CartItem.objects.create(
            cart=self.cart_1,
            product=self.product1,
            quantity=1
        )
        self.cart_item_2_1 = CartItem.objects.create(
            cart=self.cart_2,
            product=self.product1,
            quantity=2
        )
        self.promo_1_response = {
            'promo_code': self.promo_1.title
        }
        self.promo_2_response = {
            'promo_code': self.promo_2.title
        }
        self.fake_promo_response = {
            'promo_code': 'fake'
        }
        self.promo_usage = PromoUsage.objects.create(
            user=self.user_3,
            promo=self.promo_2,
            usage_count=1
        )

    def test_non_authenticated_user(self):
        response = self.client.post(
            self.promo_url,
            self.promo_1_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_apply_discount_promo(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(
            self.promo_url,
            self.promo_1_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'message': 'Promo code applied successfully'}
        )

    def test_apply_product_promo(self):
        self.client.force_authenticate(user=self.user_1)

        response = self.client.post(
            self.promo_url,
            self.promo_2_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'message': 'Promo code applied successfully'}
        )

    def test_apply_another_promo(self):
        self.client.force_authenticate(user=self.user_2)

        response = self.client.post(
            self.promo_url,
            self.promo_1_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json(),
            {'message': 'Promo code applied successfully'}
        )

    def test_max_of_usage(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(
            self.promo_url,
            self.promo_2_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertEqual(
            response.json(),
            {'error': 'Maximum usage limit reached for this promo code'}
        )

    def test_promo_not_found(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(
            self.promo_url,
            self.fake_promo_response
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertEqual(
            response.json(),
            {'error': 'Promo code not found'}
        )


class OrderCreateTestCase(APITestCase):

    def setUp(self):
        self.order_url = 'http://localhost:8000/order/'
        self.category1 = Category.objects.create(
            title='Шашлыки'
        )
        self.category2 = Category.objects.create(
            title='Напитки'
        )
        self.product1 = Product.objects.create(
            title='шашлык1',
            price=500,
            category=self.category1
        )
        self.product2 = Product.objects.create(
            title='шашлык3',
            price=400,
            category=self.category1,
            is_hidden=True
        )
        self.product3 = Product.objects.create(
            title='курица',
            price=200,
            category=self.category1
        )
        self.promo_1 = Promo.objects.create(
            title='2020',
            discount_percentage=10,
            max_usage_count=2,
        )
        self.promo_2 = Promo.objects.create(
            title='1010',
            promo_product=self.product3,
            max_usage_count=1,
        )
        self.user_1 = User.objects.create(
            email='user@example.com',
        )
        self.user_2 = User.objects.create(
            email='user2@example.com',
        )
        self.user_3 = User.objects.create(
            email='user3@example.com'
        )
        self.user_4 = User.objects.create(
            email='user4@example.com'
        )
        self.cart_1 = Cart.objects.create(
            user=self.user_1,
            promo=self.promo_1,
        )
        self.cart_2 = Cart.objects.create(
            user=self.user_2,
            promo=self.promo_2,
        )
        self.cart_3 = Cart.objects.create(
            user=self.user_3,
            total_amount=1000
        )
        self.cart_item_1_1 = CartItem.objects.create(
            cart=self.cart_1,
            product=self.product1,
            quantity=1
        )
        self.cart_item_1_2 = CartItem.objects.create(
            cart=self.cart_1,
            product=self.product3,
            quantity=1
        )
        self.cart_item_2_1 = CartItem.objects.create(
            cart=self.cart_2,
            product=self.product1,
            quantity=2
        )
        self.cart_item_3 = CartItem.objects.create(
            cart=self.cart_3,
            product=self.product3,
            quantity=5
        )
        self.parameters_0 = {}
        self.parameters_1 = {
            'buyer_name': 'Test',
            'buyer_phone_number': '+79771111111',
            'delivery_address': 'Test_address',
            'payment_method': 'to_courier',
            'delivery_method': 'pickup'
        }
        self.parameters_2 = {
            'buyer_name': 'Test',
            'buyer_phone_number': '+79771111111',
            'delivery_address': 'Test_address',
            'payment_method': 'bla',
            'delivery_method': 'vla'
        }
        self.parameters_3 = {
            'buyer_name': 'Test',
            'buyer_phone_number': '+79771111111',
            'delivery_address': 'Test_address',
            'payment_method': 'online',
            'delivery_method': 'pickup'
        }

    def test_order_200(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(
            self.order_url,
            self.parameters_1
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_order_400(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(
            self.order_url,
            self.parameters_0
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.maxDiff = None
        self.assertEqual(
            response.json(),
            {'buyer_name': ['This field is required.'],
             'buyer_phone_number': ['This field is required.'],
             'delivery_address': ['This field is required.'],
             'delivery_method': ['This field is required.'],
             'payment_method': ['This field is required.']}
        )

    def test_order_400_wrong_choice(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(
            self.order_url,
            self.parameters_2
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'delivery_method':
                {'detail': 'Field "delivery_method" must be chosen from "courier" or "pickup"'},
             'payment_method':
                 {'detail': 'Field "payment_method" must be chosen from "to_courier" or "online"'}}

        )

    def test_cart_not_found(self):
        self.client.force_authenticate(user=self.user_4)

        response = self.client.post(
            self.order_url,
            self.parameters_1
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_online_not_available(self):
        self.client.force_authenticate(user=self.user_3)

        response = self.client.post(
            self.order_url,
            self.parameters_3
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {'error': 'Online payment method is temporarily unavailable. Please choose payment "to_courier".'}
        )
