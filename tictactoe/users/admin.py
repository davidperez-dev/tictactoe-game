from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

# Register your models here.

admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ("username", "email", "is_active", "is_staff", "get_roles")
    list_filter   = ("is_active", "groups")
    search_fields = ("username", "email")

    def get_roles(self, obj):
        return ", ".join(obj.groups.values_list("name", flat=True)) or "—"

    get_roles.short_description = "Roles"
