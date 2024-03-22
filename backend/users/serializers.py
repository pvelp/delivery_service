from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer, UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from phonenumber_field.validators import validate_international_phonenumber

from users.validators import (
    FirstNameValidator, LastNameValidator, PhoneNumberValidator, DateOfBirthValidator,
    CommonPasswordValidator, NumericPasswordValidator, MinimumLengthValidator,
)

User = get_user_model()


# Здесь нам придется переопределить сериалайзер, который использует djoser
# для создания пользователя из за того, что у нас имеются нестандартные поля


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    first_name = serializers.CharField(validators=[FirstNameValidator('first_name')])
    last_name = serializers.CharField(validators=[LastNameValidator('last_name')])
    phone = serializers.CharField(validators=[PhoneNumberValidator('phone')])
    date_of_birth = serializers.DateField(validators=[DateOfBirthValidator('date_of_birth')])
    password = (serializers.CharField(validators=[CommonPasswordValidator('password'),
                                                  NumericPasswordValidator('password'),
                                                  MinimumLengthValidator('password')]))

    def validate(self, data):
        validate_international_phonenumber(data['phone'])
        return data

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone', 'date_of_birth')


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'total_amount')
