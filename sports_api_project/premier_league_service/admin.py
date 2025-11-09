from django.contrib import admin
from .models import Club, LeagueTable, Player, Fixture, PlayerStat

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('club_name', 'short_name', 'abbr', 'club_id')
    search_fields = ('club_name', 'short_name')

@admin.register(LeagueTable)
class LeagueTableAdmin(admin.ModelAdmin):
    # --- CHANGED ---
    # Added 'season' to the display and filters
    list_display = ('season', 'club', 'position', 'played', 'won', 'drawn', 'lost', 'points')
    search_fields = ('club__club_name', 'season')
    list_filter = ('season', 'club__club_name')
    ordering = ('season', 'position')
    # --- END CHANGE ---

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'club', 'position', 'nationality')
    search_fields = ('first_name', 'last_name', 'club__club_name')
    list_filter = ('club', 'position', 'nationality')

@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ('kickoff_time', 'home_club', 'away_club', 'status', 'home_score', 'away_score')
    search_fields = ('home_club__club_name', 'away_club__club_name', 'venue')
    list_filter = ('status', 'venue', 'home_club', 'away_club')

@admin.register(PlayerStat)
class PlayerStatAdmin(admin.ModelAdmin):
    list_display = ('player', 'season', 'goals', 'assists', 'minutes_played', 'clean_sheets')
    search_fields = ('player__first_name', 'player__last_name', 'season')
    list_filter = ('season', 'player__club')