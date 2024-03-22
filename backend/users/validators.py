import gzip
from pathlib import Path

from django.utils.functional import cached_property
from django.utils.translation import ngettext
from rest_framework import serializers


class FirstNameValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "first_name" is required'
                }
            )


class LastNameValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "last_name" is required'
                }
            )


class LastNameValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "last_name" is required'
                }
            )


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


class DateOfBirthValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if not value:
            raise serializers.ValidationError(
                {
                    'detail':
                        'Field "date_of_birth" is required'
                }
            )


class NumericPasswordValidator:
    """
    Validate that the password is not entirely numeric.
    """
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                'This password is entirely numeric.'
            )


class CommonPasswordValidator:
    """
    Validate that the password is not a common password.

    The password is rejected if it occurs in a provided list of passwords,
    which may be gzipped. The list Django ships with contains 20000 common
    passwords (lowercased and deduplicated), created by Royce Williams:
    https://gist.github.com/roycewilliams/226886fd01572964e1431ac8afc999ce
    The password list must be lowercased to match the comparison in validate().
    """

    @cached_property
    def DEFAULT_PASSWORD_LIST_PATH(self):
        return Path(__file__).resolve().parent / "common-passwords.txt.gz"

    def __init__(self, field, password_list_path=DEFAULT_PASSWORD_LIST_PATH):
        if password_list_path is CommonPasswordValidator.DEFAULT_PASSWORD_LIST_PATH:
            password_list_path = self.DEFAULT_PASSWORD_LIST_PATH
        try:
            with gzip.open(password_list_path, "rt", encoding="utf-8") as f:
                self.passwords = {x.strip() for x in f}
        except OSError:
            with open(password_list_path) as f:
                self.passwords = {x.strip() for x in f}
        self.field = field

    def __call__(self, password):
        if password.lower().strip() in self.passwords:
            raise serializers.ValidationError(
                {
                    'detail':
                        'This password is too common.'
                }
            )


class MinimumLengthValidator:
    """
    Validate that the password is of a minimum length.
    """

    def __init__(self, field, min_length=8):
        self.min_length = min_length
        self.field = field

    def __call__(self, password):
        if len(password) < self.min_length:
            raise serializers.ValidationError(
                ngettext(
                    (
                        f'This password is too short. It must contain at least {self.min_length}d character.'
                    ),
                    (
                        f'This password is too short. It must contain at least {self.min_length}d characters.'
                    ),
                    self.min_length,
                ),
            )
