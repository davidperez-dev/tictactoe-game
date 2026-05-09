import logging

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

ROLES = ["admin", "user"]


class Command(BaseCommand):
    help = "Create the application roles (Groups)"

    def handle(self, *args, **options):
        for role in ROLES:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                log_msg = f"role '{role}' created"
                logger.info(f"create_roles: {log_msg}")
                self.stdout.write(self.style.SUCCESS(log_msg))
            else:
                log_msg = f"role '{role}' already exists"
                logger.debug(f"create_roles: {log_msg}")
                self.stdout.write(self.style.WARNING(log_msg))
