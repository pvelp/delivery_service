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
