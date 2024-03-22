import requests
from celery import shared_task
import logging

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from main.models import Manager

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
