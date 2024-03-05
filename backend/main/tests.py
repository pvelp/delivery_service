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
