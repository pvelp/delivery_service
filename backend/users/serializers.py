from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer, UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()
# Здесь нам придется переопределить сериалайзер, который использует djoser
# для создания пользователя из за того, что у нас имеются нестандартные поля


class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'phone', 'date_of_birth')


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'total_amount')
