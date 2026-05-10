from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.

from .models import Game, Move, Player

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


def _play_moves(client, game, player, moves):
    """Post a sequence of (player, position) moves."""
    for player, position in moves:
        client.post(
            reverse("games-move", kwargs={"game_id": game.id}),
            {"position": position},
            format="json",
            **_auth_header(player),
        )


# ---------------------------------------------------------------------------
# Game logic unit tests
# ---------------------------------------------------------------------------

class GameLogicTests(TestCase):

    def setUp(self):
        self.px = _make_player("px")
        self.po = _make_player("po")
        self.game = _make_game(self.px, self.po)

    def test_initial_board_is_empty(self):
        self.assertEqual(self.game.board_state, "---------")

    def test_initial_turn_is_player_x(self):
        self.assertEqual(self.game.current_turn, self.px)

    def test_get_symbol(self):
        self.assertEqual(self.game.get_symbol(self.px), "X")
        self.assertEqual(self.game.get_symbol(self.po), "O")

    def test_apply_move_updates_board(self):
        self.game.apply_move(self.px, 0)
        self.game.refresh_from_db()
        self.assertEqual(self.game.board_state[0], "X")

    def test_apply_move_switches_turn(self):
        self.game.apply_move(self.px, 0)
        self.game.refresh_from_db()
        self.assertEqual(self.game.current_turn, self.po)

    def test_winner_row(self):
        # X wins top row: 0, 1, 2
        self.game.apply_move(self.px, 0)
        self.game.apply_move(self.po, 3)
        self.game.apply_move(self.px, 1)
        self.game.apply_move(self.po, 4)
        winner, is_draw = self.game.apply_move(self.px, 2)
        self.assertEqual(winner, self.px)
        self.assertFalse(is_draw)

    def test_winner_column(self):
        # X wins left column: 0, 3, 6
        self.game.apply_move(self.px, 0)
        self.game.apply_move(self.po, 1)
        self.game.apply_move(self.px, 3)
        self.game.apply_move(self.po, 2)
        winner, is_draw = self.game.apply_move(self.px, 6)
        self.assertEqual(winner, self.px)

    def test_winner_diagonal(self):
        # X wins diagonal: 0, 4, 8
        self.game.apply_move(self.px, 0)
        self.game.apply_move(self.po, 1)
        self.game.apply_move(self.px, 4)
        self.game.apply_move(self.po, 2)
        winner, is_draw = self.game.apply_move(self.px, 8)
        self.assertEqual(winner, self.px)

    def test_draw(self):
        # X: 0,2,5,6,7  O: 1,3,4,8  → draw
        moves = [0, 1, 2, 3, 5, 4, 6, 8, 7]
        players = [self.px, self.po] * 5
        for player, pos in zip(players, moves):
            winner, is_draw = self.game.apply_move(player, pos)
        self.assertIsNone(winner)
        self.assertTrue(is_draw)

    def test_finish_updates_winner_stats(self):
        self.game.apply_move(self.px, 0)
        self.game.apply_move(self.po, 3)
        self.game.apply_move(self.px, 1)
        self.game.apply_move(self.po, 4)
        self.game.apply_move(self.px, 2)
        self.px.refresh_from_db()
        self.po.refresh_from_db()
        self.assertEqual(self.px.wins, 1)
        self.assertEqual(self.po.losses, 1)

    def test_finish_updates_draw_stats(self):
        moves = [0, 1, 2, 3, 5, 4, 6, 8, 7]
        players = [self.px, self.po] * 5
        for player, pos in zip(players, moves):
            self.game.apply_move(player, pos)
        self.px.refresh_from_db()
        self.po.refresh_from_db()
        self.assertEqual(self.px.draws, 1)
        self.assertEqual(self.po.draws, 1)

    def test_game_finished_after_win(self):
        self.game.apply_move(self.px, 0)
        self.game.apply_move(self.po, 3)
        self.game.apply_move(self.px, 1)
        self.game.apply_move(self.po, 4)
        self.game.apply_move(self.px, 2)
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.STATUS_FINISHED)
        self.assertEqual(self.game.winner, self.px)


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


# ---------------------------------------------------------------------------
# Move endpoint
# ---------------------------------------------------------------------------

class MoveEndpointTests(APITestCase):

    def setUp(self):
        self.px = _make_player("mpx")
        self.po = _make_player("mpo")
        self.game = _make_game(self.px, self.po)

    def _move(self, player, position):
        return self.client.post(
            reverse("games-move", kwargs={"game_id": self.game.id}),
            {"position": position},
            format="json",
            **_auth_header(player),
        )

    def test_move_success(self):
        res = self._move(self.px, 0)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["board"][1], "X")  # first char of board line

    def test_move_unauthenticated(self):
        res = self.client.post(
            reverse("games-move", kwargs={"game_id": self.game.id}),
            {"position": 0},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_move_wrong_turn(self):
        res = self._move(self.po, 0)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not your turn", res.data["error"])

    def test_move_invalid_position_out_of_range(self):
        res = self._move(self.px, 9)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_move_invalid_position_type(self):
        res = self.client.post(
            reverse("games-move", kwargs={"game_id": self.game.id}),
            {"position": "abc"},
            format="json",
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_move_missing_position(self):
        res = self.client.post(
            reverse("games-move", kwargs={"game_id": self.game.id}),
            {},
            format="json",
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_move_position_already_taken(self):
        self._move(self.px, 4)
        self._move(self.po, 0)
        res = self._move(self.px, 4)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already taken", res.data["error"])

    def test_move_on_finished_game(self):
        # X wins: 0,1,2
        self._move(self.px, 0)
        self._move(self.po, 3)
        self._move(self.px, 1)
        self._move(self.po, 4)
        self._move(self.px, 2)
        res = self._move(self.po, 5)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already finished", res.data["error"])

    def test_move_game_not_found(self):
        res = self.client.post(
            reverse("games-move", kwargs={"game_id": 99999}),
            {"position": 0},
            format="json",
            **_auth_header(self.px),
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_game_x_wins(self):
        # X: 0,1,2 / O: 3,4
        self._move(self.px, 0)
        self._move(self.po, 3)
        self._move(self.px, 1)
        self._move(self.po, 4)
        res = self._move(self.px, 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "finished")
        self.assertEqual(res.data["winner"], "mpx")
        self.px.refresh_from_db()
        self.po.refresh_from_db()
        self.assertEqual(self.px.wins, 1)
        self.assertEqual(self.po.losses, 1)

    def test_full_game_draw(self):
        # X: 0,2,5,6,7 / O: 1,3,4,8
        moves = [(self.px, 0), (self.po, 1), (self.px, 2), (self.po, 3),
                 (self.px, 5), (self.po, 4), (self.px, 6), (self.po, 8), (self.px, 7)]
        for player, pos in moves:
            self._move(player, pos)
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, Game.STATUS_FINISHED)
        self.assertIsNone(self.game.winner)
        self.px.refresh_from_db()
        self.po.refresh_from_db()
        self.assertEqual(self.px.draws, 1)
        self.assertEqual(self.po.draws, 1)

    def test_move_creates_move_record(self):
        self._move(self.px, 4)
        self.assertEqual(Move.objects.filter(game=self.game).count(), 1)
        move = Move.objects.get(game=self.game)
        self.assertEqual(move.position, 4)
        self.assertEqual(move.symbol, "X")
