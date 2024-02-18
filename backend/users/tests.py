from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class PostUserTestCase(APITestCase):

    def setUp(self):
        self.users_url = 'http://localhost:8000/users/'
        self.default_user = User.objects.create(
            email='test0@mail.com',
            password='123qwe456rty',
            first_name='Name',
            last_name='Last Name',
            phone='+79778538693',
            date_of_birth='2022-10-01'
        )
        self.new_user = {
            'email': 'test@mail.com',
            'password': '123qwe456rty',
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '+79778538694',
            'date_of_birth': '2022-10-01'
        }
        self.user_email_failed = {
            'email': 'test0@mail.com',
            'password': '123qwe456rty',
            're_password': '123qwe456rty',
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '+79778538695',
            'date_of_birth': '2022-10-01'
        }
        self.user_simple_password = {
            'email': 'test1@mail.com',
            'password': '123',
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '+79778538696',
            'date_of_birth': '2022-10-01'
        }
        self.user_email_not_valid = {
            'email': 'zxc.zxc',
            'password': '123qwe456rty',
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '+79778538692',
            'date_of_birth': '2022-10-01'
        }
        self.phone_not_valid = {
            'email': 'test@mail.com',
            'password': '123qwe456rty',
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '342534',  # при вводе букв такой же ответ
            'date_of_birth': '2022-10-01'
        }
        self.validate_required_fields = {
        }
        self.date_of_birth_not_valid = {
            'email': 'test@mail.com',
            'password': '123qwe456rty',
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '+79778538691',
            'date_of_birth': 'asjkdkj'
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
                'email': ['User with this Email already exists.']
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
                    'This password is entirely numeric.',
                    'This password is too short. It must contain at least 8d '
                    'characters.'
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

    def test_phone_not_valid(self):
        response = self.client.post(
            self.users_url,
            self.phone_not_valid
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                "non_field_errors": [
                    "The phone number entered is not valid."
                ]
            }
        )

    def test_required_fields_not_entry(self):
        response = self.client.post(
            self.users_url,
            self.validate_required_fields
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                "email": ["This field is required."],
                "password": ["This field is required."],
                "first_name": ["This field is required."],
                "last_name": ["This field is required."],
                "phone": ["This field is required."],
                "date_of_birth": ["This field is required."]
            }
        )

    def test_date_of_birth_not_valid(self):
        response = self.client.post(
            self.users_url,
            self.date_of_birth_not_valid
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            response.json(),
            {
                "date_of_birth": [
                    "Date has wrong format. Use one of these formats instead: YYYY-MM-DD."
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
            'first_name': 'Name',
            'last_name': 'Last Name',
            'phone': '+79778538694',
            'date_of_birth': '2022-10-01'
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
