import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Game, Move, Player
from .serializers import GameSerializer, PlayerSerializer

logger = logging.getLogger(__name__)


class PlayerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username=None):
        if username is None:
            players = Player.objects.select_related("user").order_by("-wins", "user__username")
            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data)

        try:
            player = Player.objects.select_related("user").get(user__username=username)
        except Player.DoesNotExist:
            return Response({"error": "player not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlayerSerializer(player)
        return Response(serializer.data)


class GameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List all games the authenticated player is part of."""
        player = request.user.player
        games = (
            Game.objects.filter(player_x=player)
            | Game.objects.filter(player_o=player)
        ).order_by("-created_at").prefetch_related("moves")
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new game. Body: { "opponent": "<username>" }"""
        opponent_username = request.data.get("opponent")
        if not opponent_username:
            return Response({"error": "opponent is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player_x = request.user.player
        except Player.DoesNotExist:
            return Response({"error": "requesting user has no player profile"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player_o = Player.objects.select_related("user").get(user__username=opponent_username)
        except Player.DoesNotExist:
            return Response({"error": f"opponent '{opponent_username}' not found"}, status=status.HTTP_404_NOT_FOUND)

        if player_x == player_o:
            return Response({"error": "cannot play against yourself"}, status=status.HTTP_400_BAD_REQUEST)

        game = Game.objects.create(
            player_x=player_x,
            player_o=player_o,
            current_turn=player_x,
        )
        logger.info("Game %d created: %s (X) vs %s (O)", game.id, player_x, player_o)
        serializer = GameSerializer(game)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GameDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        try:
            game = Game.objects.prefetch_related("moves").get(pk=game_id)
        except Game.DoesNotExist:
            return Response({"error": "game not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GameSerializer(game)
        return Response(serializer.data)


class MoveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, game_id):
        """Make a move. Body: { "position": 0-8 }"""
        try:
            game = Game.objects.prefetch_related("moves").get(pk=game_id)
        except Game.DoesNotExist:
            return Response({"error": "game not found"}, status=status.HTTP_404_NOT_FOUND)

        if not game.is_active:
            return Response({"error": "game is already finished"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            player = request.user.player
        except Player.DoesNotExist:
            return Response({"error": "user has no player profile"}, status=status.HTTP_400_BAD_REQUEST)

        if game.current_turn != player:
            return Response({"error": "it is not your turn"}, status=status.HTTP_400_BAD_REQUEST)

        position = request.data.get("position")
        if position is None:
            return Response({"error": "position is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            position = int(position)
        except (TypeError, ValueError):
            return Response({"error": "position must be an integer 0-8"}, status=status.HTTP_400_BAD_REQUEST)

        if position < 0 or position > 8:
            return Response({"error": "position must be between 0 and 8"}, status=status.HTTP_400_BAD_REQUEST)

        if game.board_state[position] != "-":
            return Response({"error": "position is already taken"}, status=status.HTTP_400_BAD_REQUEST)

        symbol = game.get_symbol(player)
        winner, is_draw = game.apply_move(player, position)

        Move.objects.create(game=game, player=player, position=position, symbol=symbol)

        if winner:
            logger.info("Game %d finished: %s wins", game.id, winner)
        elif is_draw:
            logger.info("Game %d finished: draw", game.id)
        else:
            logger.info("Game %d: %s played position %d", game.id, player, position)

        game.refresh_from_db()
        serializer = GameSerializer(game)
        return Response(serializer.data)
