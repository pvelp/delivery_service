from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from users.managers import UserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

NULLABLE = {'blank': True, 'null': True}


class UserRoles(models.TextChoices):
    user = 'user', _('user')
    admin = 'admin', _('admin')


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True, verbose_name='Электронная почта')

    role = models.CharField(max_length=9, choices=UserRoles.choices,
                            default=UserRoles.user, verbose_name='Роль')

    first_name = models.CharField(max_length=20, verbose_name='Имя', **NULLABLE)
    last_name = models.CharField(max_length=35, verbose_name='Фамилия', **NULLABLE)
    phone = PhoneNumberField(verbose_name='Номер телефона', unique=True, **NULLABLE)
    date_of_birth = models.DateField(verbose_name='Дата рождения', **NULLABLE)
    address = models.TextField(verbose_name='Последний адрес доставки', **NULLABLE)
    total_amount = models.DecimalField(max_digits=9, decimal_places=2,
                                       verbose_name='Общая сумма заказов',
                                       default=0.00)

    is_active = models.BooleanField(verbose_name='Статус', default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def is_superuser(self):
        return self.role == UserRoles.admin

    @property
    def is_staff(self):
        return self.role == UserRoles.admin

    @property
    def is_user(self):
        return self.role == UserRoles.user

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
