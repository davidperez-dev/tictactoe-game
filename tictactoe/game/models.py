from django.db import models
from django.contrib.auth.models import User

# Create your models here.


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


class Move(models.Model):
    game = models.ForeignKey(Game, related_name="moves", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    symbol = models.CharField(max_length=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Move by {self.player} at position {self.position} in Game {self.game.id}"
        )
