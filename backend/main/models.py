from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from users.models import User

NULLABLE = {'blank': True, 'null': True}


class MeasureChoices(models.TextChoices):
    gram = 'гр.'
    kilogram = 'кг.'
    milliliter = 'мл.'
    liter = 'л.'


class Category(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название категории', **NULLABLE)
    image = models.ImageField(upload_to='category_images', verbose_name='Картинка', **NULLABLE)
    description = models.TextField(verbose_name='Описание', **NULLABLE)
    is_hidden = models.BooleanField(default=False, verbose_name='Скрыт из показа', **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    title = models.CharField(max_length=30, verbose_name='Название блюда', **NULLABLE)
    image = models.ImageField(upload_to='product_images', verbose_name='Картинка', **NULLABLE)
    description = models.TextField(verbose_name='Состав', **NULLABLE)
    weight = models.IntegerField(verbose_name='Вес', **NULLABLE)
    measure = models.CharField(max_length=3, choices=MeasureChoices.choices,
                               default=MeasureChoices.gram, verbose_name='Единица измерения')
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Текущая цена',
                                default=0.00)
    temporary_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Временная цена',
                                    **NULLABLE)
    is_hidden = models.BooleanField(default=False, verbose_name='Скрыт из показа', **NULLABLE)
    # promotional_price = models.DecimalField(max_digits=9, decimal_places=2,
    #                                         verbose_name='Цена с введенным  промокодом', default=0.00)
    # discount = models.IntegerField(verbose_name='Скидка в процентах', **NULLABLE)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория',
                                 **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Promo(models.Model):
    title = models.CharField(max_length=40, verbose_name='Название промо', **NULLABLE)
    discount_percentage = models.SmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)],
                                                   verbose_name='Процент скидки', **NULLABLE)
    promo_product = models.ForeignKey(Product, on_delete=models.SET_NULL, verbose_name='Товар в подарок',
                                      **NULLABLE)
    max_usage_count = models.SmallIntegerField(verbose_name='Максимально кол-во использований для одного клиента', default=1)
    current_usage_count = models.SmallIntegerField(verbose_name='Текущее кол-во использований',
                                                   default=0)


class PromoUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Покупатель')
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, verbose_name='Промо')
    usage_count = models.IntegerField(verbose_name='Количество использований', default=0)


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Покупатель', **NULLABLE)
    buyer_name = models.CharField(max_length=20, verbose_name='Имя покупателя', **NULLABLE)
    buyer_phone_number = PhoneNumberField(verbose_name='Номер телефона', unique=True, **NULLABLE)
    order_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время заказа', **NULLABLE)
    delivery_address = models.CharField(max_length=255, verbose_name='Адрес доставки', **NULLABLE)
    order_amount = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Сумма заказа',
                                       default=0.00)
    products = models.ManyToManyField(Product, verbose_name='Товары в заказе')

    class PaymentChoices(models.TextChoices):
        cash = 'Оплата курьеру'
        online = 'Оплата онлайн'

    payment_method = models.CharField(max_length=14, choices=PaymentChoices.choices,
                                      default=PaymentChoices.online, verbose_name='Способ оплаты')
    promo = models.ForeignKey(Promo, on_delete=models.SET_NULL, verbose_name='Промокод', **NULLABLE)  # пользователь вводит промокод, после нажатия применить, промокод сравнивается с промокодами в модели промокодов и применятся или нет

    def __str__(self):
        return f'Заказ №{self.id} от {self.order_datetime} для {self.buyer_name}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    products = models.ManyToManyField(Product, through='CartItem')
    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, verbose_name='Промокод', **NULLABLE)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class RecommendedProducts(models.Model):
    product_1 = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='recommended_product_1',
                                  **NULLABLE, verbose_name='Рекомендуемый товар 1')
    product_2 = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='recommended_product_2',
                                  **NULLABLE, verbose_name='Рекомендуемый товар 2')
    product_3 = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='recommended_product_3',
                                  **NULLABLE, verbose_name='Рекомендуемый товар 3')
