from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class PostUserTestCase(APITestCase):

    def setUp(self):
        self.users_url = 'http://localhost:8000/users/'
        self.default_user = User.objects.create(
            email='test0@mail.com',
            password='123qwe456rty'
        )
        self.new_user = {
            'email': 'test@mail.com',
            'password': '123qwe456rty',
            're_password': '123qwe456rty'
        }
        self.user_email_failed = {
            'email': 'test0@mail.com',
            'password': '123qwe456rty',
            're_password': '123qwe456rty'
        }
        self.user_simple_password = {
            'email': 'test1@mail.com',
            'password': '12345678',
            're_password': '12345678'
        }
        self.user_email_not_valid = {
            'email': 'zxc.zxc',
            'password': '123qwe456rty',
            're_password': '123qwe456rty'
        }
        self.user_password_not_match = {
            'email': 'test@mail.com',
            'password': '123qwe456rt',
            're_password': '123qwe456rty'
        }

    def test_create_201(self):
        response = self.client.post(
            self.users_url,
            self.new_user
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_user_already_exists(self):
        response = self.client.post(
            self.users_url,
            self.user_email_failed
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                'email': ['user with this Электронная почта already exists.']  # TODO: Добавить валидацию здесь и для доп полей и переименовать на англ яз
            }
        )

    def test_password_is_simple(self):
        response = self.client.post(
            self.users_url,
            self.user_simple_password
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                'password': [
                    'This password is too common.',
                    'This password is entirely numeric.'
                ]
            }
        )

    def test_email_not_valid(self):
        response = self.client.post(
            self.users_url,
            self.user_email_not_valid
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                'email': [
                    'Enter a valid email address.'
                ]
            }
        )

    def test_not_matching_password(self):
        response = self.client.post(
            self.users_url,
            self.user_password_not_match
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                'non_field_errors': [
                    "The two password fields didn't match."
                ]
            }
        )


class ActivateUserTestCase(APITestCase):
    def setUp(self):
        self.users_url = 'http://localhost:8000/users/'
        self.activation_url = 'http://localhost:8000/users/activation/'
        # self.user_jwt_create = 'http://localhost:8000/jwt/create/'
        self.user = {
            'email': 'test@mail.com',
            'password': '123qwe456rty',
            're_password': '123qwe456rty'
        }
        # self.user_login = {
        #     'email': 'test@mail.com',
        #     'password': '123qwe456rty'
        # }

    def test_activate(self):
        response = self.client.post(
            self.users_url,
            self.user
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(len(mail.outbox), 1)

        email_lines = mail.outbox[0].body.splitlines()
        activation_link = [l for l in email_lines if '/activate/' in l][0]
        uid, token = activation_link.split('/')[-2:]

        data = {
            'uid': uid,
            'token': token
        }
        response = self.client.post(
            self.activation_url,
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )
