import logging
import os

from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import UserRegistrationSerializer, UserSerializer

# Create your views here.

logger = logging.getLogger(__name__)

# User management
class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        token = TokenObtainPairSerializer.get_token(user)
        logger.info(f"New user registered: {user.username}")

        return Response(
            {"username": user.username, "token": str(token.access_token)},
            status=status.HTTP_201_CREATED,
        )

class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Login a user and return a JWT token"""
        serializer =TokenObtainPairSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username is None:
            """Get a list of all users"""
            users = User.objects.all().prefetch_related("groups").order_by("username")
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)

        try:
            user = User.objects.prefetch_related("groups").get(username=username)
        except User.DoesNotExist:
            return Response({"error": "user not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)
