from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

ROLES = ["admin", "user"]


class Command(BaseCommand):
    help = "Create the application roles (Groups)"

    def handle(self, *args, **options):
        for role in ROLES:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Role '{role}' created"))

            else:
                self.stdout.write(self.style.WARNING(f"Role '{role}' already exists"))
