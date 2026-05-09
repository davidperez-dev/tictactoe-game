from django.db import models
from django.contrib.auth.models import User

# Create your models here.

WINNING_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # cols
    (0, 4, 8), (2, 4, 6),              # diagonals
]


class Player(models.Model):
    user = models.OneToOneField(User, related_name="player", on_delete=models.CASCADE)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    draws = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username

    @property
    def total_games(self):
        return self.wins + self.losses + self.draws


class Game(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_FINISHED = "finished"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_FINISHED, "Finished"),
    ]

    player_x = models.ForeignKey(
        Player, related_name="player_as_x", on_delete=models.CASCADE
    )
    player_o = models.ForeignKey(
        Player, related_name="player_as_o", on_delete=models.CASCADE
    )
    current_turn = models.ForeignKey(
        Player, related_name="player_as_current", on_delete=models.CASCADE
    )
    winner = models.ForeignKey(
        Player,
        related_name="player_as_winner",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE
    )
    board_state = models.CharField(max_length=9, default="-" * 9)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.id}: (X) {self.player_x} vs (O) {self.player_o}"

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def get_symbol(self, player):
        return "X" if player == self.player_x else "O"

    def _check_winner(self):
        b = self.board_state
        for a, c, d in WINNING_LINES:
            if b[a] != "-" and b[a] == b[c] == b[d]:
                return b[a]
        return None

    def _finish(self, winner):
        self.status = self.STATUS_FINISHED
        self.winner = winner
        self.save()

        if winner:
            loser = self.player_o if winner == self.player_x else self.player_x
            winner.wins += 1
            loser.losses += 1
            winner.save()
            loser.save()
        else:
            self.player_x.draws += 1
            self.player_o.draws += 1
            self.player_x.save()
            self.player_o.save()
