#  TODO: Добавить тесты на все реальзованные эндпоинты

from decimal import Decimal
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from main.models import Category, Product, RecommendedProducts


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
            [
                {
                    "message": "Product removed from cart successfully"
                },
                {
                    "details": {
                        "cart_id": 4,
                        "product_id": self.product1.id,
                        "quantity": 0
                    }
                }
            ]
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
