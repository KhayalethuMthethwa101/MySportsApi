from django.http import Http404
from .models import LeagueTable, PlayerStat, Player
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat

def get_league_table_data(season: str):
    """
    Fetches the league table from our database for a specific season.
    """
    # --- CHANGED ---
    # We now filter by the provided season and select related club info
    table_data = LeagueTable.objects.filter(season=season).select_related('club').order_by('position')

    if not table_data:
        raise Http404(f"No league table data found for season: {season}")

    # Format the data for the serializer
    formatted_table = []
    for entry in table_data:
        formatted_table.append({
            'position': entry.position,
            'team': entry.club.club_name, # Get name from related club
            'played': entry.played,
            'wins': entry.won,
            'draws': entry.drawn,
            'losses': entry.lost,
            'goals_for': entry.goals_for,
            'goals_against': entry.goals_against,
            'points': entry.points,
            'goal_difference': entry.goal_difference,
            'form': entry.form
        })
    
    return formatted_table


def get_player_stats_data(season: str, stat_type: str):
    """
    Fetches player stats (goals or assists) from our database
    for a specific season.
    """
    # Determine which database field to sort by
    if stat_type == 'goals':
        sort_key = '-goals' # Note the '-' for descending order
        stat_field = 'goals'
    elif stat_type == 'assists':
        sort_key = '-assists'
        stat_field = 'assists'
    else:
        raise Http404("Invalid stat type. Use 'goals' or 'assists'.")

    # --- CHANGED ---
    # Query our PlayerStat model, filter by season, and get related Player/Club info
    player_stats = PlayerStat.objects.filter(
        season=season,
        **{f'{stat_field}__gt': 0} # Only get players with stat > 0
    ).select_related('player', 'player__club').order_by(sort_key)[:20] # Get top 20

    if not player_stats:
        raise Http404(f"No player stats found for {stat_type} in season {season}")

    # Format the data for the serializer
    formatted_stats = []
    for stat_line in player_stats:
        formatted_stats.append({
            'name': f"{stat_line.player.first_name or ''} {stat_line.player.last_name or ''}".strip(),
            'club': stat_line.player.club.club_name if stat_line.player.club else 'Unknown',
            'nationality': stat_line.player.nationality,
            'stat': getattr(stat_line, stat_field) # Get the specific stat value (goals or assists)
        })
            
    return formatted_stats