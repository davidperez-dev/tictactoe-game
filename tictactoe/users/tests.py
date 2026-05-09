from io import StringIO

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.validators import CustomPasswordValidator

VALID_PASSWORD = "Abcdef1@gh"  # meets all policy rules


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(username="testuser", password="pass", role="user"):
    """Create a user and assign it to a role group (group must exist)."""
    Group.objects.get_or_create(name="user")
    Group.objects.get_or_create(name="admin")
    user = User.objects.create_user(username=username, password=password)
    group = Group.objects.get(name=role)
    user.groups.add(group)
    return user


def _auth_header(user):
    token = RefreshToken.for_user(user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------

class RegisterEndpointTests(APITestCase):

    def test_register_success(self):
        url = reverse("register")
        res = self.client.post(url, {"username": "david", "password": VALID_PASSWORD}, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_register_missing_username(self):
        url = reverse("register")
        res = self.client.post(url, {"password": VALID_PASSWORD}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_password(self):
        url = reverse("register")
        res = self.client.post(url, {"username": "david"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        url = reverse("register")
        res = self.client.post(url, {"username": "david", "password": "weak"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        _make_user("david")
        url = reverse("register")
        res = self.client.post(url, {"username": "david", "password": VALID_PASSWORD}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class LoginEndpointTests(APITestCase):

    def setUp(self):
        self.user = _make_user("steve", "password123")

    def test_login_success(self):
        url = reverse("login")
        res = self.client.post(url, {"username": "steve", "password": "password123"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_wrong_password(self):
        url = reverse("login")
        res = self.client.post(url, {"username": "steve", "password": "wrong"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_user(self):
        url = reverse("login")
        res = self.client.post(url, {"username": "nobody", "password": "x"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshEndpointTests(APITestCase):

    def setUp(self):
        self.user = _make_user("carol", "password123")

    def test_refresh_success(self):
        refresh = str(RefreshToken.for_user(self.user))
        url = reverse("token-refresh")
        res = self.client.post(url, {"refresh": refresh}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_refresh_invalid_token(self):
        url = reverse("token-refresh")
        res = self.client.post(url, {"refresh": "notavalidtoken"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class UserListEndpointTests(APITestCase):

    def setUp(self):
        self.user = _make_user("dave", "password123")

    def test_list_unauthenticated(self):
        url = reverse("users-list")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self):
        url = reverse("users-list")
        res = self.client.get(url, **_auth_header(self.user))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)
        usernames = [u["username"] for u in res.data]
        self.assertIn("dave", usernames)


class UserDetailEndpointTests(APITestCase):

    def setUp(self):
        self.user = _make_user("eve", "password123")

    def test_detail_unauthenticated(self):
        url = reverse("users-detail", kwargs={"username": "eve"})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_detail_found(self):
        url = reverse("users-detail", kwargs={"username": "eve"})
        res = self.client.get(url, **_auth_header(self.user))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "eve")
        self.assertIn("roles", res.data)

    def test_detail_not_found(self):
        url = reverse("users-detail", kwargs={"username": "nobody"})
        res = self.client.get(url, **_auth_header(self.user))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Password validator tests
# ---------------------------------------------------------------------------

class PasswordValidatorTests(TestCase):

    def setUp(self):
        self.validator = CustomPasswordValidator()

    def _assert_valid(self, password):
        try:
            self.validator.validate(password)
        except ValidationError as exc:
            self.fail(f"Expected valid password but got: {exc.messages}")

    def _assert_invalid(self, password):
        with self.assertRaises(ValidationError):
            self.validator.validate(password)

    def test_valid_password(self):
        self._assert_valid(VALID_PASSWORD)

    def test_too_short(self):
        self._assert_invalid("Ab1@xyz")  # 7 chars

    def test_no_uppercase(self):
        self._assert_invalid("abcdef1@gh")

    def test_no_lowercase(self):
        self._assert_invalid("ABCDEF1@GH")

    def test_no_digit(self):
        self._assert_invalid("Abcdefgh@i")

    def test_no_special(self):
        self._assert_invalid("Abcdef1234")

    def test_disallowed_special_char(self):
        self._assert_invalid("Abcdef1!gh")  # '!' not allowed

    def test_boundary_exactly_10_chars(self):
        self._assert_valid("Abcdef1@gh")  # exactly 10

    def test_all_allowed_specials(self):
        for ch in "@#%()_+-.":
            self._assert_valid(f"Abcdef1{ch}gh")

# ---------------------------------------------------------------------------
# Management command tests
# ---------------------------------------------------------------------------

class CreateRolesCommandTests(TestCase):

    def test_creates_roles(self):
        call_command("create_roles", stdout=StringIO())
        self.assertTrue(Group.objects.filter(name="admin").exists())
        self.assertTrue(Group.objects.filter(name="user").exists())

    def test_idempotent(self):
        call_command("create_roles", stdout=StringIO())
        call_command("create_roles", stdout=StringIO())
        self.assertEqual(Group.objects.filter(name__in=["admin", "user"]).count(), 2)


class CreateUserCommandTests(TestCase):

    def setUp(self):
        call_command("create_roles", stdout=StringIO())

    def test_create_user_role(self):
        call_command("create_user", "frank", VALID_PASSWORD, "user", stdout=StringIO())
        user = User.objects.get(username="frank")
        self.assertTrue(user.groups.filter(name="user").exists())
        self.assertFalse(user.is_staff)

    def test_create_admin_role(self):
        call_command("create_user", "grace", VALID_PASSWORD, "admin", stdout=StringIO())
        user = User.objects.get(username="grace")
        self.assertTrue(user.groups.filter(name="admin").exists())
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_duplicate_raises_error(self):
        call_command("create_user", "henry", VALID_PASSWORD, "user", stdout=StringIO())
        with self.assertRaises(CommandError):
            call_command("create_user", "henry", VALID_PASSWORD, "user", stdout=StringIO())


class ChangePasswordCommandTests(TestCase):

    def setUp(self):
        call_command("create_roles", stdout=StringIO())
        call_command("create_user", "ivan", VALID_PASSWORD, "user", stdout=StringIO())

    def test_change_password_success(self):
        new_password = "Newpass1@gh"
        call_command("change_password", "ivan", new_password, stdout=StringIO())
        user = User.objects.get(username="ivan")
        self.assertTrue(user.check_password(new_password))

    def test_change_password_unknown_user(self):
        with self.assertRaises(CommandError):
            call_command("change_password", "nobody", VALID_PASSWORD, stdout=StringIO())


class CreateAdminCommandTests(TestCase):

    def setUp(self):
        call_command("create_roles", stdout=StringIO())

    def test_creates_admin_from_env(self):
        with self.settings():
            import os
            os.environ["ADMIN_USERNAME"] = "superadmin"
            os.environ["ADMIN_PASSWORD"] = "adminpass"
            call_command("create_admin", stdout=StringIO())
            user = User.objects.get(username="superadmin")
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.groups.filter(name="admin").exists())

    def test_skips_without_password(self):
        import os
        os.environ.pop("ADMIN_PASSWORD", None)
        os.environ["ADMIN_USERNAME"] = "orphan"
        call_command("create_admin", stdout=StringIO())
        self.assertFalse(User.objects.filter(username="orphan").exists())

    def test_skips_existing_admin(self):
        import os
        os.environ["ADMIN_USERNAME"] = "superadmin"
        os.environ["ADMIN_PASSWORD"] = "adminpass"
        call_command("create_admin", stdout=StringIO())
        call_command("create_admin", stdout=StringIO())
        self.assertEqual(User.objects.filter(username="superadmin").count(), 1)
