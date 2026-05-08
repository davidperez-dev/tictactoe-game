import re

from django.core.exceptions import ValidationError


_ALLOWED_SPECIAL = set("@#%()_+-.")
_SPECIAL_RE = re.compile(r"[@#%()_+\-.]")
_ALLOWED_RE = re.compile(r"^[A-Za-z0-9@#%()_+\-.]+$")


class CustomPasswordValidator:
    """
    Custom password validator enforcing the following rules:
      - At least 10 characters
      - At least one uppercase letter
      - At least one lowercase letter
      - At least one digit
      - At least one special character: @ # % ( ) _ + - .
      - No characters outside the allowed set
    """

    def validate(self, password, user=None):
        errors = []

        if len(password) < 10:
            errors.append("at least 10 characters")
        if not re.search(r"[A-Z]", password):
            errors.append("one uppercase letter")
        if not re.search(r"[a-z]", password):
            errors.append("one lowercase letter")
        if not re.search(r"[0-9]", password):
            errors.append("one digit")
        if not _SPECIAL_RE.search(password):
            errors.append("one special character (@ # % ( ) _ + - .)")
        if not _ALLOWED_RE.match(password):
            errors.append("only allowed special characters: @ # % ( ) _ + - .")

        if errors:
            raise ValidationError(
                f"Password must contain: {', '.join(errors)}.",
                code="password_too_weak",
            )

    def get_help_text(self):
        return (
            "Your password must be at least 10 characters and contain an uppercase "
            "letter, a lowercase letter, a digit, and a special character (@ # % ( ) _ + - .). "
            "No other special characters are allowed."
        )
