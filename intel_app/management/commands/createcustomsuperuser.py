import getpass

from django.contrib.auth.management.commands.createsuperuser import Command as BaseCommand
from django.core.management import CommandError
from django.contrib.auth import get_user_model
from django.utils.text import capfirst


from django.core.management import CommandError


class Command(BaseCommand):
    help = 'Create a superuser with all required fields.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--first_name', dest='first_name', default=None, help='Specifies the first name.')
        parser.add_argument('--last_name', dest='last_name', default=None, help='Specifies the last name.')
        parser.add_argument('--phone', dest='phone', default=None, help='Specifies the phone number.')

    def handle(self, *args, **options):
        print("Custom createsuperuser command is being used.")
        username = options.get('username')
        email = options.get('email')
        database = options.get('database')
        password = options.get('password')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        phone = options.get('phone')

        UserModel = get_user_model()

        # Prompt for required fields if not provided
        if not username:
            username = input('Username: ')
        if not email:
            email = input('Email address: ')
        if not first_name:
            first_name = input('First name: ')
        if not last_name:
            last_name = input('Last name: ')
        if not phone:
            phone = input('Phone number: ')
        if not password:
            password = getpass.getpass()

        user_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'password': password,
        }

        try:
            # Create the superuser
            UserModel._default_manager.db_manager(database).create_superuser(**user_data)
            self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
        except Exception as e:
            raise CommandError(f'Error: {e}')