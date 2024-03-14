import json
import tempfile

import requests
from django.contrib import admin
from django.core import files
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path

from main.models import Product, Category, Order, RecommendedProducts, Promo, Manager, OrderItem
from users.models import User
from admins.models import IikoAPIKey, ExternalMenu, Organization

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


#  Часть с админкой для iikoWeb

@admin.register(IikoAPIKey)
class IikoAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('key',)

    def get_token_and_fetch_menu(self, request):
        api_key = IikoAPIKey.objects.last()

        token_response = requests.post('https://api-ru.iiko.services/api/1/access_token',
                                       json={'apiLogin': api_key.key})
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

    def get_organizations(self, request):
        api_key = IikoAPIKey.objects.last()

        token_response = requests.post('https://api-ru.iiko.services/api/1/access_token',
                                       json={'apiLogin': api_key.key})
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

    def save_menu(self, request):
        if request.method == 'POST':
            menu_id = request.POST.get('menu_id')
            organization_id = request.POST.get('organization_id')
            organization_ids = [organization_id]

            api_key = IikoAPIKey.objects.last()

            token_response = requests.post('https://api-ru.iiko.services/api/1/access_token',
                                           json={'apiLogin': api_key.key})
            token_data = token_response.json()

            if token_response.status_code == 200:
                headers = {'Authorization': f'Bearer {token_data["token"]}'}
                menu_data = {
                    "externalMenuId": menu_id,
                    "organizationIds": organization_ids
                }
                menu_response = requests.post('https://api-ru.iiko.services/api/2/menu/by_id',
                                              headers=headers,
                                              json=menu_data)
                menu_json = menu_response.json()

                if menu_response.status_code == 200:
                    for category_data in menu_json.get('itemCategories', []):
                        category_id = category_data.get('id')
                        if not category_id:
                            return HttpResponse('Не найдено ни одной категории', status=404)
                        category_name = category_data.get('name', '')
                        category_description = category_data.get('description', '')
                        category_image_url = category_data.get('buttonImageUrl', '')

                        try:
                            category, created = Category.objects.update_or_create(category_id=category_id,
                                                                                  defaults={'title': category_name,
                                                                                            'description': category_description})
                            response = None
                            if category_image_url:
                                response = requests.get(category_image_url, stream=True)

                            if response and response.status_code == requests.codes.ok:
                                file_name = category_image_url.split('/')[-1]
                                lf = tempfile.NamedTemporaryFile()
                                for block in response.iter_content(1024 * 8):
                                    # If no more file then stop
                                    if not block:
                                        break
                                    # Write image block to temporary file
                                    lf.write(block)
                                category.image.save(file_name, files.File(lf))
                            else:
                                # Handle error or skip file
                                continue
                        except Exception as e:
                            return HttpResponse(f'Ошибка при обновлении/создании категории: {str(e)}', status=500)

                        for item_data in category_data.get('items', []):
                            product_id = item_data.get('itemId')
                            if not product_id:
                                return HttpResponse('Не найдено ни одного продукта', status=404)
                            product_title = item_data.get('name', '')
                            product_description = item_data.get('description', '')
                            product_image = item_data['itemSizes'][0].get('buttonImageUrl', '')
                            product_weight = item_data['itemSizes'][0].get('portionWeightGrams', 0)
                            product_price = item_data['itemSizes'][0]['prices'][0].get('price', 0)

                            product_defaults = {
                                'title': product_title,
                                'description': product_description,
                                'weight': product_weight,
                                'price': product_price,
                                'category': category
                            }

                            try:
                                product, created = Product.objects.update_or_create(product_id=product_id,
                                                                                    defaults=product_defaults)

                                response = None
                                if product_image:
                                    response = requests.get(product_image, stream=True)

                                if response and response.status_code == requests.codes.ok:
                                    file_name = product_image.split('/')[-1]
                                    lf = tempfile.NamedTemporaryFile()
                                    for block in response.iter_content(1024 * 8):
                                        if not block:
                                            break
                                        lf.write(block)
                                    product.image.save(file_name, files.File(lf))
                                else:
                                    continue
                            except Exception as e:
                                return HttpResponse(f'Ошибка при обновлении/создании продукта: {str(e)}', status=500)

                    return HttpResponse('Меню успешно получено и сохранено в базе данных.')
                else:
                    return HttpResponse('Ошибка при получении меню.')
            else:
                return HttpResponse('Ошибка при получении токена.')

        else:
            return render(request, 'admin/save_menu.html')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-token-and-fetch-menu/', self.get_token_and_fetch_menu),
            path('get-organizations/', self.get_organizations),
            path('save-menu/', self.save_menu, name='save-menu'),
        ]
        return custom_urls + urls


@admin.register(ExternalMenu)
class ExternalMenuAdmin(admin.ModelAdmin):
    list_display = ('menu_id', 'name')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('organization_id', 'name')
