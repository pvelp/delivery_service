from datetime import datetime
from decimal import Decimal

from main.models import CartItem, HappyHours
from pytz import timezone


def calculate_cart(cart):
    cart_items = CartItem.objects.filter(cart=cart.id)
    cart_data = []
    total_amount = 0
    is_happy_hours = False

    moscow_timezone = timezone('Europe/Moscow')
    current_time = datetime.now(moscow_timezone).time()

    try:
        happy_hours = HappyHours.objects.get(is_active=True)
    except HappyHours.DoesNotExist:
        happy_hours = None

    is_weekday = datetime.now().weekday() < 5

    for cart_item in cart_items:
        price = cart_item.product.temporary_price if cart_item.product.temporary_price else cart_item.product.price

        if cart_item.product.image:
            image = cart_item.product.image.url
        else:
            image = None

        if cart_item.product.category.title.lower() == 'напитки':
            total_price = cart_item.quantity * price
        elif happy_hours and is_weekday and happy_hours.time_to_start <= current_time <= happy_hours.time_to_end:
            discount_percentage = happy_hours.discount_percentage
            total_price = (cart_item.quantity * price) * (100 - discount_percentage) / 100
            is_happy_hours = True
        else:
            total_price = cart_item.quantity * price

        item_data = {
            'product_id': cart_item.product.id,
            'title': cart_item.product.title,
            'image': image,
            'weight': cart_item.product.weight,
            'quantity': cart_item.quantity,
            'price': price,
            'total_price': total_price
        }
        cart_data.append(item_data)
        total_amount += total_price

    cart.total_amount = total_amount
    cart.is_happy_hours = is_happy_hours
    cart.save()

    # Применение скидки к общей сумме корзины, если есть промокод
    if cart.promo:
        promo = cart.promo
        if promo.discount_percentage:
            discount_amount = total_amount * (Decimal(promo.discount_percentage) / 100)
            total_amount_with_discount = total_amount - discount_amount
            cart.total_amount = total_amount_with_discount
            cart.save()
            response_data = {
                'cart_items': cart_data,
                'total_amount': total_amount,
                'total_amount_with_discount': total_amount_with_discount,
                'happy_hours': is_happy_hours
            }
            return response_data
        elif promo.promo_product:
            if promo.promo_product.image:
                image = promo.promo_product.image
            else:
                image = None

            promo_product_data = {
                'product_id': promo.promo_product.id,
                'title': promo.promo_product.title,
                'image': image,
                'weight': promo.promo_product.weight,
                'quantity': 1,
                'price': 0,
                'total_price': 0
            }
            cart_data.append(promo_product_data)

    response_data = {
        'cart_items': cart_data,
        'total_amount': cart.total_amount,
        'total_amount_with_discount': None,
        'happy_hours': is_happy_hours
    }
    return response_data
