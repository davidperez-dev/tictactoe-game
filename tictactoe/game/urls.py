from django.urls import path

from . import views

urlpatterns = [
    path("players/", views.PlayerScoreView.as_view(), name="players-list"),
    path("players/<str:username>/", views.PlayerScoreView.as_view(), name="players-detail"),
]

