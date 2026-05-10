import logging
import os

from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from game.models import Player

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Create an admin user. "
        "If USERNAME and PASSWORD arguments are provided they are used directly. "
        "Otherwise falls back to ADMIN_USERNAME / ADMIN_PASSWORD env vars."
    )

    def add_arguments(self, parser):
        parser.add_argument("username", nargs="?", help="Admin username")
        parser.add_argument("password", nargs="?", help="Admin password")

    def handle(self, *args, **options):
        username = options.get("username") or os.environ.get("ADMIN_USERNAME", "admin")
        password = options.get("password") or os.environ.get("ADMIN_PASSWORD")

        if not password:
            log_msg = "ADMIN_PASSWORD not set — skipping default admin creation"
            logger.warning(f"create_admin: {log_msg}")
            self.stdout.write(self.style.WARNING(log_msg))
            return

        try:
            validate_password(password)
        except ValidationError as e:
            raise CommandError(f"Invalid password: {'; '.join(e.messages)}")

        if User.objects.filter(username=username).exists():
            log_msg = f"admin user '{username}' already exists — skipped"
            logger.warning(f"create_admin: {log_msg}")
            self.stdout.write(self.style.WARNING(log_msg))
            return

        user = User.objects.create_superuser(username=username, password=password)
        group = Group.objects.get(name="admin")
        user.groups.add(group)
        Player.objects.get_or_create(user=user)
        log_msg = f"admin user '{username}' created"
        logger.info(f"create_admin: {log_msg}")
        self.stdout.write(self.style.SUCCESS(log_msg))
