import tempfile
from django.core import files

import requests
from celery import shared_task
import logging

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.http import HttpResponse
from main.models import Manager, Category, Product
from admins.models import IikoAPIKey

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_message(bot_token, order):
    base_url = f'https://api.telegram.org/bot{bot_token}'

    managers = Manager.objects.filter(tg_id__isnull=False)

    if not managers.exists():
        logger.warning('No managers found in the database with tg_id specified')
        return

    product_info = ""
    for item in order.items.all():
        product_info += f"{item.product.title}: {item.quantity} шт., Цена за 1 ед.: {item.product.price} руб.\n"

    for manager in managers:
        chat_id = manager.tg_id
        message_text = f'''Заказ {order.id}
        Покупатель (если зарегистрирован): {order.buyer}
        Имя покупателя: {order.buyer_name}
        Номер телефона: {order.buyer_phone_number}
        Дата и время заказа: {order.order_datetime}
        Адрес доставки: {order.delivery_address}
        Состав заказа (Товар/количество): \n{product_info}
        Способ оплаты: {order.payment_method}
        Способ доставки: {order.delivery_method}
        Промокод: {order.promo}
        Скидка по акции "Счасливые часы": {order.is_happy_hours}
        
        Сумма заказа: {order.order_amount}'''

        url = f'{base_url}/sendMessage?chat_id={chat_id}&text={message_text}'

        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка статуса ответа
            logger.info(f'Message sent to manager with chat_id {chat_id}')
        except requests.RequestException as e:
            logger.error(f'Error sending message to manager with chat_id {chat_id}: {e}')


@shared_task
def send_email_message(order):
    managers = Manager.objects.filter(email__isnull=False)

    if not managers.exists():
        logger.warning('No managers found in the database with email specified')
        return

    users_email = [manager.email for manager in managers]

    product_info = ""
    for item in order.items.all():
        product_info += f"{item.product.title}: {item.quantity} шт., Цена за 1 ед.: {item.product.price} руб.\n"

    message = f'''Заказ {order.id}
        Покупатель (если зарегистрирован): {order.buyer}
        Имя: {order.buyer_name}
        Номер телефона: {order.buyer_phone_number}
        Дата и время заказа: {order.order_datetime}
        Адрес доставки: {order.delivery_address}
        Состав заказа (Товар/количество): \n{product_info}
        Метод оплаты: {order.payment_method}
        Доставка: {order.delivery_method}
        Промокод: {order.promo}
        
        Общая сумма заказа: {order.order_amount}'''

    email_message = EmailMultiAlternatives(
        subject=f'Новый заказ {order.id}',
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=users_email
    )

    try:
        email_message.send()
        logger.info(f'Email sent to managers: {", ".join(users_email)}')
    except Exception as e:
        logger.error(f'Error sending email to managers: {e}')


@shared_task
def save_menu(menu_id, organization_id):
    logger.info(f'меню: {menu_id}, орг: {organization_id}')
    api_key = IikoAPIKey.objects.last()

    token_response = requests.post('https://api-ru.iiko.services/api/1/access_token',
                                   json={'apiLogin': api_key.key})
    token_data = token_response.json()

    if token_response.status_code == 200:
        headers = {'Authorization': f'Bearer {token_data["token"]}'}
        menu_data = {
            "externalMenuId": menu_id,
            "organizationIds": organization_id
        }
        menu_response = requests.post('https://api-ru.iiko.services/api/2/menu/by_id',
                                      headers=headers,
                                      json=menu_data)
        menu_json = menu_response.json()

        if menu_response.status_code == 200:
            tasks = []
            for category_data in menu_json.get('itemCategories', []):
                category_id = category_data.get('id')
                if not category_id:
                    logger.info('Не найдено ни одной категории')
                    return HttpResponse('Не найдено ни одной категории', status=404)
                category_name = category_data.get('name', '')
                category_description = category_data.get('description', '')
                category_image_url = category_data.get('buttonImageUrl', '')

                try:
                    category, created = Category.objects.update_or_create(category_id=category_id,
                                                                          defaults={'title': category_name,
                                                                                    'description': category_description})
                    logger.info(f'Категория: {category.title} успешно добавлена в БД')
                    response = None
                    if category_image_url:
                        response = requests.get(category_image_url, stream=True)
                        if response.status_code == requests.codes.ok:
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
                    logger.info(f'Ошибка при обновлении/создании категории: {str(e)}')
                    return HttpResponse(f'Ошибка при обновлении/создании категории: {str(e)}', status=500)

                for item_data in category_data.get('items', []):
                    product_id = item_data.get('itemId')
                    if not product_id:
                        logger.info('Не найдено ни одного продукта')
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
                        logger.info(f'Товар: {product.title} успешно добавлен в БД')

                        response = None
                        if product_image:
                            response = requests.get(product_image, stream=True)
                            if response.status_code == requests.codes.ok:
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
