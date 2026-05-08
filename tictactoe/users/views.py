import os

from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView as _BaseObtainView

from .serializers import RoleTokenObtainPairSerializer

# Create your views here.


# Token endpoint
class RoleTokenObtainPairView(_BaseObtainView):
    """Role-based JWT token obtain pair view"""
    serializer_class = RoleTokenObtainPairSerializer


# User management
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user"""
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        role     = "user"

        if not username or not password:
            return Response(
                {"error": "username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(password)
        except ValidationError as exc:
            return Response(
                {"error": exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "username already exists"},
                status=status.HTTP_409_CONFLICT,
            )

        user = User.objects.create_user(username=username, password=password)

        if role:
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        return Response(
            {"username": user.username, "roles": [role] if role else []},
            status=status.HTTP_201_CREATED,
        )


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username is None:
            """Get a list of all users"""
            users = User.objects.all().prefetch_related("groups").order_by("username")
            data = [
                {
                    "username": u.username,
                    "email":    u.email,
                    "roles":    list(u.groups.values_list("name", flat=True)),
                    "is_active": u.is_active,
                }
                for u in users
            ]
            return Response(data)

        try:
            user = User.objects.prefetch_related("groups").get(username=username)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "username": user.username,
            "email":    user.email,
            "roles":    list(user.groups.values_list("name", flat=True)),
            "is_active": user.is_active,
        }
        return Response(data)
