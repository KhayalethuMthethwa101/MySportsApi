from django.http import Http404
import requests # Use the requests library to make HTTP calls

# The single, stable API endpoint for all FPL data
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

def _get_fpl_data():
    """
    Internal helper function to fetch the main FPL data.
    This single call gets all teams, players, and stats.
    """
    try:
        response = requests.get(FPL_API_URL)
        response.raise_for_status() # Raises an error for bad responses (4xx, 5xx)
        data = response.json()
        
        # Create a simple {team_id: team_name} map for easy lookups
        team_map = {team['id']: team['name'] for team in data.get('teams', [])}
        
        return data, team_map
        
    except requests.exceptions.RequestException as e:
        # This catches network errors, timeout, bad status codes
        raise Http404(f"Could not connect to FPL API. Error: {str(e)}")
    except Exception as e:
        # This catches JSON parsing errors or other unexpected issues
        raise Http404(f"An unexpected error occurred parsing FPL data. Error: {str(e)}")


def get_league_table_data(season: str):
    """
    Fetches the league table from the FPL API.
    Note: The FPL API only supports the *current* season.
    The 'season' argument is ignored but kept for compatibility.
    """
    # NOTE: The 'season' argument is now ignored, as the FPL API
    # only provides current-season data. This is why it failed
    # when you tried to get 2022-2023.
    
    data, _ = _get_fpl_data() # We only need the main data
    
    table_data = data.get('teams', [])
    if not table_data:
        raise Http404("No team data found in FPL API response.")
        
    # The data is already a clean list of dictionaries.
    # We just rename 'rank' to 'position' to match our serializer
    # and 'name' to 'team'.
    formatted_table = []
    for team in table_data:
        formatted_table.append({
            'position': team.get('rank'),
            'team': team.get('name'),
            'played': team.get('played'),
            'wins': team.get('win'),
            'draws': team.get('draw'),
            'losses': team.get('loss'),
            'points': team.get('points'),
            # The FPL API gives us goals for/against, which is great
            'goals_for': team.get('goals_for'),
            'goals_against': team.get('goals_against'),
            'goal_difference': team.get('goals_for', 0) - team.get('goals_against', 0)
        })
    
    # Sort by position
    formatted_table.sort(key=lambda x: x['position'] if x['position'] is not None else 99)
    return formatted_table


def get_player_stats_data(season: str, stat_type: str):
    """
    Fetches player stats (goals or assists) from the FPL API.
    Note: The FPL API only supports the *current* season.
    """
    # NOTE: The 'season' argument is now ignored.
    data, team_map = _get_fpl_data()
    
    player_data = data.get('elements', [])
    if not player_data:
        raise Http404("No player data found in FPL API response.")

    # Determine which stat to sort by
    sort_key = 'goals_scored' if stat_type == 'goals' else 'assists'

    # Sort players by the chosen stat
    # We use 'int()' to handle potential None values gracefully (treats None as 0)
    sorted_players = sorted(
        player_data, 
        key=lambda p: int(p.get(sort_key, 0)), 
        reverse=True
    )

    # Format the data to match our serializer
    formatted_stats = []
    for player in sorted_players[:20]: # Return top 20
        stat_value = int(player.get(sort_key, 0))
        
        # Only include players who have a non-zero stat
        if stat_value > 0:
            formatted_stats.append({
                'name': player.get('web_name'),
                'club': team_map.get(player.get('team'), 'Unknown'), # Map team ID to name
                'nationality': 'Unknown', # FPL API doesn't provide this here
                'stat': stat_value
            })
            
    return formatted_stats