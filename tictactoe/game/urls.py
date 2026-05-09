from django.urls import path

from . import views

urlpatterns = [
    path("players/", views.PlayerListView.as_view(), name="players-list"),
    path("players/<str:username>/", views.PlayerListView.as_view(), name="players-detail"),
    path("games/", views.GameView.as_view(), name="games-list"),
    path("games/<int:game_id>/", views.GameDetailView.as_view(), name="games-detail"),
]
