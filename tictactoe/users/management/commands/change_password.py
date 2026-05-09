from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class Command(BaseCommand):
    help = "Change the password of an existing user"

    def add_arguments(self, parser):
        parser.add_argument("username", help="Login username")
        parser.add_argument("password", help="New password")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]

        try:
            validate_password(password)
        except Exception as e:
            raise CommandError(f"Invalid password: {e}")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist.")

        user.set_password(password)
        user.save()

        self.stdout.write(
            self.style.SUCCESS(f"Password for '{username}' updated successfully.")
        )
