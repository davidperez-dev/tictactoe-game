import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)

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
            msg_log = f"invalid password for '{username}': {e}"
            logger.error(f"change_password: {msg_log}")
            raise CommandError(f"Invalid password: {e}")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            msg_log = f"user '{username}' does not exist"
            logger.error(f"change_password: {msg_log}")
            raise CommandError(f"User '{username}' does not exist.")

        user.set_password(password)
        user.save()
        msg_log = f"password updated for user '{username}'"
        logger.info(f"change_password: {msg_log}")

        self.stdout.write(
            self.style.SUCCESS(msg_log)
        )
