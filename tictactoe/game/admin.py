from django.contrib import admin

# Register your models here.

from .models import Player, Game, Move


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ["user", "wins", "losses", "draws", "total_games"]


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player_x",
        "player_o",
        "current_turn",
        "winner",
        "status",
        "updated_at",
        "created_at",
    ]


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    list_display = ["id", "game", "player", "position", "symbol", "created_at"]
