from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage

from djoser import email
from djoser import utils
from djoser.conf import settings


class ConfirmationEmail(email.ConfirmationEmail):
    template_name = "confirmation.html"

    def get_context_data(self):
        # PConfirmationEmail can be deleted
        pass

