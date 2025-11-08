from rest_framework import serializers

# These are "non-model" serializers. They define the shape of our API output
# without being tied to a database model. This is perfect for proxying an external API.

class LeagueTableEntrySerializer(serializers.Serializer):
    """
    Serializes the data for a single team in the league table.
    The field names (e.g., 'position', 'team') must match the keys
    created in our services.py file.
    """
    position = serializers.IntegerField()
    team = serializers.CharField(max_length=100)
    played = serializers.IntegerField()
    wins = serializers.IntegerField()
    draws = serializers.IntegerField()
    losses = serializers.IntegerField()
    goal_difference = serializers.CharField(max_length=10) # e.g., "+15"
    points = serializers.IntegerField()
    # We can add more fields if the library provides them and we map them in services.py


class PlayerStatSerializer(serializers.Serializer):
    """
    Serializes the data for a single player's stats.
    """
    name = serializers.CharField(max_length=100)
    club = serializers.CharField(max_length=100)
    nationality = serializers.CharField(max_length=100)
    stat = serializers.IntegerField()