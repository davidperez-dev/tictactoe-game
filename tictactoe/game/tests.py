from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.

from .models import Game, Player

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_player(username, password="pass"):
    user = User.objects.create_user(username=username, password=password)
    player = Player.objects.create(user=user)
    return player


def _auth_header(player):
    token = RefreshToken.for_user(player.user).access_token
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def _make_game(player_x, player_o):
    return Game.objects.create(
        player_x=player_x,
        player_o=player_o,
        current_turn=player_x,
    )

# ---------------------------------------------------------------------------
# Player endpoints
# ---------------------------------------------------------------------------

class PlayerListEndpointTests(APITestCase):

    def setUp(self):
        self.player = _make_player("alpha")

    def test_list_unauthenticated(self):
        res = self.client.get(reverse("players-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_authenticated(self):
        res = self.client.get(reverse("players-list"), **_auth_header(self.player))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)
        usernames = [p["username"] for p in res.data]
        self.assertIn("alpha", usernames)

    def test_detail_found(self):
        res = self.client.get(
            reverse("players-detail", kwargs={"username": "alpha"}),
            **_auth_header(self.player),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["username"], "alpha")
        self.assertIn("wins", res.data)
        self.assertIn("losses", res.data)
        self.assertIn("draws", res.data)
        self.assertIn("total_games", res.data)

    def test_detail_not_found(self):
        res = self.client.get(
            reverse("players-detail", kwargs={"username": "nobody"}),
            **_auth_header(self.player),
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Game CRUD endpoints
# ---------------------------------------------------------------------------

class GameCreateTests(APITestCase):

    def setUp(self):
        self.px = _make_player("creator")
        self.po = _make_player("opponent")

    def test_create_game_success(self):
        res = self.client.post(
            reverse("games-list"),
            {"opponent": "opponent"},
            format="json",
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["player_x"], "creator")
        self.assertEqual(res.data["player_o"], "opponent")
        self.assertEqual(res.data["current_turn"], "creator")
        self.assertEqual(res.data["status"], "active")

    def test_create_game_missing_opponent(self):
        res = self.client.post(
            reverse("games-list"), {}, format="json", **_auth_header(self.px)
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_game_unknown_opponent(self):
        res = self.client.post(
            reverse("games-list"),
            {"opponent": "ghost"},
            format="json",
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_game_against_yourself(self):
        res = self.client.post(
            reverse("games-list"),
            {"opponent": "creator"},
            format="json",
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_game_unauthenticated(self):
        res = self.client.post(
            reverse("games-list"), {"opponent": "opponent"}, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class GameListDetailTests(APITestCase):

    def setUp(self):
        self.px = _make_player("px2")
        self.po = _make_player("po2")
        self.game = _make_game(self.px, self.po)

    def test_list_own_games(self):
        res = self.client.get(reverse("games-list"), **_auth_header(self.px))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ids = [g["id"] for g in res.data]
        self.assertIn(self.game.id, ids)

    def test_detail_found(self):
        res = self.client.get(
            reverse("games-detail", kwargs={"game_id": self.game.id}),
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("board", res.data)
        self.assertIn("moves", res.data)

    def test_detail_not_found(self):
        res = self.client.get(
            reverse("games-detail", kwargs={"game_id": 99999}),
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
