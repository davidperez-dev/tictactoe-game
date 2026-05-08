import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = "Create the default admin user from ADMIN_USERNAME / ADMIN_PASSWORD env vars"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_PASSWORD not set — skipping default admin creation."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"Admin user '{username}' already exists — skipped."))
            return

        user = User.objects.create_superuser(username=username, password=password)
        group = Group.objects.get(name="admin")
        user.groups.add(group)

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin user '{username}' created with Django Admin access."
            )
        )
