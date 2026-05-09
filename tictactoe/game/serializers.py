from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    total_games = serializers.IntegerField(read_only=True)

    class Meta:
        model = Player
        fields = ["id", "username", "wins", "losses", "draws", "total_games"]
