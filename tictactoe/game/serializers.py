from rest_framework import serializers

from .models import Game, Move, Player


class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    total_games = serializers.IntegerField(read_only=True)

    class Meta:
        model = Player
        fields = ["id", "username", "wins", "losses", "draws", "total_games"]


class MoveSerializer(serializers.ModelSerializer):
    player = serializers.CharField(source="player.user.username", read_only=True)

    class Meta:
        model = Move
        fields = ["id", "player", "symbol", "position", "created_at"]


class GameSerializer(serializers.ModelSerializer):
    player_x = serializers.CharField(source="player_x.user.username", read_only=True)
    player_o = serializers.CharField(source="player_o.user.username", read_only=True)
    current_turn = serializers.CharField(source="current_turn.user.username", read_only=True)
    winner = serializers.CharField(source="winner.user.username", read_only=True, default=None)
    board = serializers.SerializerMethodField()
    moves = MoveSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            "id", "player_x", "player_o", "current_turn", "winner",
            "status", "board", "moves", "created_at", "updated_at",
        ]

    def get_board(self, obj):
        s = obj.board_state
        row = lambda i: f" {s[i]} | {s[i+1]} | {s[i+2]} "
        sep = "-----------"
        return "\n".join([row(0), sep, row(3), sep, row(6)])
