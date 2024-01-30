from django.contrib import admin
from django.db.models import Max
from django.utils.html import format_html

from main.models import Product, Category, Order
from users.models import User

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'weight', 'measure', 'price', 'category',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'image', 'description', 'is_hidden',)


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    readonly_fields = ['order_datetime', 'delivery_address', 'order_amount', 'payment_method']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'total_amount',)
    readonly_fields = ('last_order_info',)
    inlines = [OrderInline]

    def last_order_info(self, obj):
        last_order = obj.order_set.last()
        if last_order:
            products_info = "\n".join([product.title for product in last_order.products.all()])
            return (f'Дата и время: {last_order.order_datetime},\n'
                    f'Адрес: {last_order.delivery_address},\n'
                    f'Сумма заказа: {last_order.order_amount} руб.\n'
                    f'Способ оплаты: {last_order.payment_method}\n'
                    f'Товары в заказе: {products_info}')
        return 'Пользователь еще не сделал заказов'

    last_order_info.short_description = 'Последний заказ'
