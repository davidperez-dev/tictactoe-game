import logging
import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from game.models import Player

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create the default admin user from ADMIN_USERNAME / ADMIN_PASSWORD env vars"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD")

        if not password:
            log_msg = "ADMIN_PASSWORD not set — skipping default admin creation"
            logger.warning(f"create_admin: {log_msg}")
            self.stdout.write(self.style.WARNING(log_msg))
            return

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
