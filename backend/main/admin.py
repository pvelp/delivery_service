from django.contrib import admin
from django.db.models import Max
from django.utils.html import format_html

from main.models import Product, Category, Order, RecommendedProducts, Promo, Manager, OrderItem
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
    readonly_fields = ['order_datetime', 'delivery_address', 'order_amount', 'payment_method', 'promo']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'total_amount',)
    readonly_fields = ('last_order_info', 'total_amount')
    inlines = [OrderInline]

    def last_order_info(self, obj):
        last_order = obj.order_set.last()
        if last_order:
            items_info = "\n".join([f'{item.product.title} (количество: {item.quantity})' for item in last_order.items.all()])
            return (f'Дата и время: {last_order.order_datetime},\n'
                    f'Адрес: {last_order.delivery_address},\n'
                    f'Сумма заказа: {last_order.order_amount} руб.\n'
                    f'Способ оплаты: {last_order.payment_method}\n'
                    f'Товары в заказе: {items_info}')
        return 'Пользователь еще не сделал заказов'

    last_order_info.short_description = 'Последний заказ'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderReadOnlyAdmin(admin.ModelAdmin):
    list_display = ('buyer_name', 'buyer_phone_number', 'order_datetime', 'delivery_address', 'order_amount', 'payment_method', 'promo')
    readonly_fields = ('buyer_name', 'buyer_phone_number', 'order_datetime', 'delivery_address', 'order_amount', 'payment_method', 'promo')
    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False  # отключаем возможность добавления заказов

    def has_delete_permission(self, request, obj=None):
        return False  # отключаем возможность удаления заказов


@admin.register(RecommendedProducts)
class RecommendedProductsAdmin(admin.ModelAdmin):
    list_display = ('product_1', 'product_2', 'product_3')


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'promo_product', 'max_usage_count', 'current_usage_count')


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('name', 'tg_id', 'email')
