from django.urls import path
from . import views

# These URLs are all prefixed with 'api/premier-league/' (from the project's urls.py)
urlpatterns = [
    path('table/', views.LeagueTableView.as_view(), name='league-table'),
    path('player-stats/', views.PlayerStatsView.as_view(), name='player-stats'),
]