from rest_framework import serializers
from .models import LeagueTable, PlayerStat, Club, Player

# These serializers are now based on our models, but the
# services.py file pre-formats the data, so we can
# keep them as simple Serializers.

class LeagueTableEntrySerializer(serializers.Serializer):
    """
    Serializes the data for a single team in the league table.
    """
    position = serializers.IntegerField()
    team = serializers.CharField(max_length=100)
    played = serializers.IntegerField()
    wins = serializers.IntegerField()
    draws = serializers.IntegerField()
    losses = serializers.IntegerField()
    # --- New Fields Below ---
    goals_for = serializers.IntegerField()
    goals_against = serializers.IntegerField()
    # --- End New Fields ---
    goal_difference = serializers.IntegerField()
    points = serializers.IntegerField()
    form = serializers.CharField(max_length=10, allow_blank=True, allow_null=True)


class PlayerStatSerializer(serializers.Serializer):
    """
    Serializes the data for a single player's stats.
    """
    name = serializers.CharField(max_length=200)
    club = serializers.CharField(max_length=100)
    nationality = serializers.CharField(max_length=100, allow_blank=True, allow_null=True)
    stat = serializers.IntegerField()