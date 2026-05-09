import logging

from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Player
from .serializers import PlayerSerializer

logger = logging.getLogger(__name__)


class PlayerScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username is None:
            players = Player.objects.select_related("user").order_by("-wins", "username")
            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data)

        try:
            player = Player.objects.select_related("user").get(user__username=username)
        except Player.DoesNotExist:
            return Response({"error": "player not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlayerSerializer(player)
        return Response(serializer.data)
