import logging

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)

VALID_ROLES = ["admin", "user"]


class Command(BaseCommand):
    help = "Create a user and assign a role: admin | user"

    def add_arguments(self, parser):
        parser.add_argument("username", help="Login username")
        parser.add_argument("password", help="Initial password")
        parser.add_argument(
            "role",
            choices=VALID_ROLES,
            help="Role to assign: admin | user",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        role     = options["role"]

        if User.objects.filter(username=username).exists():
            log_msg = f"user '{username}' already exists"
            logger.error(f"create_user: {log_msg}")
            raise CommandError(log_msg)

        try:
            validate_password(password)
        except Exception as e:
            log_msg = f"invalid password for '{username}': {e}"
            logger.error(f"create_user: {log_msg}")
            raise CommandError(f"Invalid password: {e}")

        is_staff     = role == "admin"
        is_superuser = role == "admin"
        user = User.objects.create_user(
            username=username,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )
        group = Group.objects.get(name=role)
        user.groups.add(group)

        log_msg = f"user '{username}' created with role '{role}'"
        logger.info(f"create_user: {log_msg}")
        self.stdout.write(self.style.SUCCESS(log_msg))
