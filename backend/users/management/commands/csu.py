from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@admin.com',
            first_name='admin',
            last_name='django',
            role='admin'
        )

        user.set_password('123456')
        user.save()
