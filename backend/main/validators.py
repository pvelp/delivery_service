import phonenumbers
from rest_framework import serializers


class PhoneNumberValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "phone" is required'
                }
            )
        try:
            parsed_number = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise serializers.ValidationError(
                    {
                        'detail': 'Invalid phone number format'
                    }
                )
        except phonenumbers.phonenumberutil.NumberParseException as e:
            raise serializers.ValidationError(
                {
                    'detail': 'Invalid phone number format'
                }
            )


class AddressValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "delivery_address" is required'
                }
            )


class BuyerNameValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "buyer_name" is required'
                }
            )


class PaymentMethodValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "payment_method" is required'
                }
            )
        elif value != 'to_courier' and value != 'online':
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "payment_method" must be chosen from "to_courier" or "online"'
                }
            )


class DeliveryMethodValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "delivery_method" is required'
                }
            )
        elif value != 'courier' and value != 'pickup':
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "delivery_method" must be chosen from "courier" or "pickup"'
                }
            )
