import json

import requests
from django.contrib import admin
from django.http import HttpResponse
from asgiref.sync import async_to_sync
from django.shortcuts import render
from django.urls import path

from main.models import Product, Category, Order, RecommendedProducts, Promo, Manager, OrderItem, HappyHours
from users.models import User
from admins.models import IikoAPIKey, ExternalMenu, Organization, FetchMenu

from main.tasks import save_menu

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_id', 'title', 'description', 'price', 'category', 'is_hidden')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_id', 'title', 'description', 'is_hidden',)


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
    list_display = ('id', 'email', 'first_name', 'last_name', 'phone')
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
    list_display = ('id', 'buyer_phone_number', 'order_datetime', 'delivery_address', 'order_amount')
    readonly_fields = ('buyer_name', 'buyer_phone_number', 'order_datetime', 'delivery_address', 'order_amount', 'payment_method', 'promo')
    inlines = [OrderItemInline]

    def has_add_permission(self, request):
        return False  # отключаем возможность добавления заказов

    def has_delete_permission(self, request, obj=None):
        return False  # отключаем возможность удаления заказов


@admin.register(RecommendedProducts)
class RecommendedProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_1', 'product_2', 'product_3')


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'discount_percentage', 'promo_product', 'max_usage_count', 'current_usage_count')


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tg_id', 'email')


@admin.register(HappyHours)
class HappyHoursAdmin(admin.ModelAdmin):
    list_display = ('id', 'time_to_start', 'time_to_end', 'discount_percentage', 'is_active')


#  Часть с админкой для iikoWeb

@admin.action(description="Сохранить Внешние меню из Iikoweb в модель")
def get_token_and_fetch_menu(modeladmin, request, queryset):
    obj = queryset.first()
    api_key = obj.key

    token_response = requests.post('https://api-ru.iiko.services/api/1/access_token',
                                   json={'apiLogin': api_key})
    token_data = token_response.json()

    # Если токен успешно получен, делаем запрос на получение меню
    if token_response.status_code == 200:
        headers = {'Authorization': f'Bearer {token_data["token"]}'}
        menu_response = requests.post('https://api-ru.iiko.services/api/2/menu',
                                      headers=headers)

        try:
            menu_data = menu_response.json()
        except json.decoder.JSONDecodeError:
            # Если JSON не удалось разобрать, можно вывести информацию о полученном тексте
            print(menu_response.text)
            return HttpResponse('Ошибка при получении данных: JSON не удалось разобрать', status=500)

        # Сохраняем полученное меню и категории в базе данных
        if menu_response.status_code == 200:
            for menu in menu_data['externalMenus']:
                ExternalMenu.objects.get_or_create(menu_id=menu['id'], name=menu['name'])

            return HttpResponse('Меню успешно получено и сохранено в базе данных.')
        else:
            return HttpResponse('Ошибка при получении меню.')
    else:
        return HttpResponse('Ошибка при получении токена. Проверьте корректность сохраненного API ключа и внесите изменения.')


@admin.action(description="Сохранить организации из Iikoweb в модель")
def get_organizations(modeladmin, request, queryset):
    obj = queryset.first()
    api_key = obj.key

    token_response = requests.post('https://api-ru.iiko.services/api/1/access_token',
                                   json={'apiLogin': api_key})
    token_data = token_response.json()

    if token_response.status_code == 200:
        headers = {'Authorization': f'Bearer {token_data["token"]}'}
        organizations_response = requests.post('https://api-ru.iiko.services/api/1/organizations',
                                               headers=headers, json={})
        organizations_data = organizations_response.json()

        if organizations_response.status_code == 200:
            for org in organizations_data['organizations']:
                Organization.objects.get_or_create(organization_id=org['id'], name=org['name'])

            return HttpResponse('Организации успешно получены и сохранены в базе данных.')
        else:
            return HttpResponse('Ошибка при получении организаций.')
    else:
        return HttpResponse('Ошибка при получении токена. Проверьте корректность сохраненного API ключа и внесите изменения.')


@admin.register(IikoAPIKey)
class IikoAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('key',)
    actions = [get_token_and_fetch_menu, get_organizations]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-token-and-fetch-menu/', get_token_and_fetch_menu),
            path('get-organizations/', get_organizations),
        ]
        return custom_urls + urls


@admin.register(ExternalMenu)
class ExternalMenuAdmin(admin.ModelAdmin):
    list_display = ('menu_id', 'name')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'name')


@admin.action(description="Сохранить товары и категории выбранных организации и меню")
def fetch_menu(self, request, queryset):
    try:
        obj = queryset.first()
        menu_id = obj.menu.menu_id
        organization_id = [obj.organization.organization_id]

        save_menu(menu_id, organization_id)
        self.message_user(request, f"Сохранили меню: {obj.menu.name} для организации: {obj.organization.name}")
    except Exception as e:
        self.message_user(request, f"Произошла ошибка: {e}")


@admin.register(FetchMenu)
class FetchMenuAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'menu_id')
    actions = [fetch_menu]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('fetch-menu/', fetch_menu),
        ]
        return custom_urls + urls
