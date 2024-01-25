from django.db import models

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
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена',
                                default=0.00)
    promotional_price = models.DecimalField(max_digits=9, decimal_places=2,
                                            verbose_name='Цена с введенным  промокодом', default=0.00)
    discount = models.IntegerField(verbose_name='Скидка в процентах', **NULLABLE)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория',
                                 **NULLABLE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Покупатель', **NULLABLE)
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

    def __str__(self):
        return f'Заказ №{self.id} от {self.order_datetime} для {self.buyer}'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
