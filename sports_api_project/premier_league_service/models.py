from django.db import models

class Club(models.Model):
    """
    Stores a single Premier League club.
    Data is sourced from the API's 'standings' or 'teams' endpoint.
    """
    club_id = models.FloatField(primary_key=True)
    club_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    abbr = models.CharField(max_length=10)

    def __str__(self):
        return self.club_name

class LeagueTable(models.Model):
    """
    Stores a single team's league table position FOR A SPECIFIC SEASON.
    """
    # --- CHANGED ---
    # We no longer use a OneToOneField. Instead, we link to the club
    # and add a season field.
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    season = models.CharField(max_length=10) # e.g., "2024-2025"
    # --- END CHANGE ---

    position = models.IntegerField(default=0)
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    drawn = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    goals_for = models.IntegerField(default=0)
    goals_against = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)
    form = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        # --- NEW ---
        # This ensures we can't have two entries for the same club in the same season.
        unique_together = ('club', 'season')

    def __str__(self):
        return f"{self.season} - {self.club.club_name} (Pos: {self.position})"


class Player(models.Model):
    """
    Stores a single player.
    """
    player_id = models.FloatField(primary_key=True)
    # A player might not belong to a PL club (e.g., on loan, left the league)
    # so we use null=True, blank=True.
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

class Fixture(models.Model):
    """
    Stores an upcoming or completed fixture (match).
    """
    fixture_id = models.FloatField(primary_key=True)
    kickoff_time = models.DateTimeField(null=True, blank=True) # <-- CHANGED
    home_club = models.ForeignKey(Club, related_name='home_fixtures', on_delete=models.CASCADE)
    away_club = models.ForeignKey(Club, related_name='away_fixtures', on_delete=models.CASCADE)
    venue = models.CharField(max_length=100, null=True, blank=True)

    # Fields for completed matches (results)
    status = models.CharField(max_length=20, default='SCHEDULED') # e.g., SCHEDULED, LIVE, COMPLETED
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.home_club.abbr} vs {self.away_club.abbr} ({self.kickoff_time.date()})"


class PlayerStat(models.Model):
    """
    Stores detailed stats for a player for a specific season.
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    season = models.CharField(max_length=10) # e.g., "2024-2025"
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    clean_sheets = models.IntegerField(default=0)
    minutes_played = models.IntegerField(default=0)
    passes = models.IntegerField(default=0)
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'season') # One stat line per player per season

    def __str__(self):
        return f"Stats for {self.player} ({self.season})"