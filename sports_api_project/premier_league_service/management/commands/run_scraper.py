import requests
import sys
import time
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
# --- NEW ---
from django.core import management # Import the management module
# --- END NEW ---
from premier_league_service.models import Club, LeagueTable, Player, Fixture, PlayerStat

# --- Constants ---
API_BASE_URL = "https://footballapi.pulselive.com/football"
HEADERS = {'Origin': 'https://www.premierleague.com'}

# This map is crucial for fetching historical data
# We map our clean "YYYY-YYYY" season label to the API's internal ID
SEASON_ID_MAP = {
    '2017-2018': 12,
    '2018-2019': 21,
    '2019-2020': 22,
    '2020-2021': 42,
    '2021-2022': 79,
    '2022-2023': 418,
    '2023-2024': 578,
    '2024-2025': 1064, # API ID for the current season
    '2025-2026': 1184, # API ID for the next season
}
# This tells the league table scraper to use a fallback endpoint
CURRENT_SEASON_LABEL = '2024-2025'

PARAMS_CLUBS = {'page': 0, 'pageSize': 100}
PARAMS_FIXTURES = {'comps': 1, 'page': 0, 'pageSize': 100, 'sort': 'asc', 'statuses': 'U,L'} # Increased page size for fixtures

# Removed PARAMS_RESULTS, as we will now loop by season.
# We'll create params for historical results dynamically.

# The /players endpoint seems to reject the 2024-2025 season ID.
# We will call it with just comps=1, which should return all players.
PARAMS_PLAYERS = {'page': 0, 'pageSize': 100, 'comps': 1}


class Command(BaseCommand):
    help = 'Scrapes Premier League data and populates the database.'

    def fetch_api_data(self, endpoint, params={}):
        """Helper function to fetch data from the API."""
        try:
            url = f"{API_BASE_URL}/{endpoint}"
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            
            if not response.content:
                # Log an empty response but don't crash
                self.stderr.write(f"Empty response from {url} with params {params}")
                return None
            return response.json()
        
        except requests.exceptions.RequestException as e:
            self.stderr.write(f"Error fetching {e.request.url}: {e}")
            return None
        except requests.exceptions.JSONDecodeError as e:
            self.stderr.write(f"Error decoding JSON from {e.request.url}: {e}")
            return None

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting Premier League data scrape...")

        # 1. Fetch and process Clubs
        self.stdout.write("\n--- Fetching Clubs ---")
        club_data = self.fetch_api_data("clubs", params=PARAMS_CLUBS)
        if club_data:
            self.process_clubs(club_data)

        # 2. Fetch Historical League Tables
        self.stdout.write("\n--- Fetching Historical League Tables ---")
        for season_label in SEASON_ID_MAP.keys():
            self.process_league_table(season_label)
            time.sleep(0.1) # Be nice to the API

        # 3. Fetch and process Fixtures
        self.stdout.write("\n--- Fetching Fixtures ---")
        fixture_data = self.fetch_api_data("fixtures", params=PARAMS_FIXTURES)
        if fixture_data:
            self.process_fixtures(fixture_data)

        # 4. Fetch ALL historical results by season
        self.stdout.write("\n--- Fetching Historical Results ---")
        
        for season_label, season_id in SEASON_ID_MAP.items():
            self.stdout.write(f"Fetching results for {season_label} (API ID: {season_id})...")
            
            # A season has 380 matches. pageSize=400 should get all in one page.
            result_params = {
                'comps': 1,
                'compSeasons': season_id,
                'page': 0,
                'pageSize': 400, # Get all 380 matches in one go
                'sort': 'desc',
                'statuses': 'C' # 'C' for Completed
            }
            
            result_data = self.fetch_api_data("fixtures", params=result_params)
            if result_data:
                # We can reuse the same process_results function
                self.process_results(result_data, season_label) 
            
            time.sleep(0.1) # Be nice to the API

        # 5. Fetch and process Players
        self.stdout.write("\n--- Fetching Players ---")
        all_player_ids = self.process_players()
        
        # 6. Fetch Player Stats
        self.stdout.write("\n--- Fetching Player Stats (Example: First 5) ---")
        if all_player_ids:
            # Test with a known *good* season ID ('2023-2024')
            TEST_SEASON_LABEL = '2023-2024'
            self.stdout.write(self.style.WARNING(f"Fetching stats for season: {TEST_SEASON_LABEL}"))
            
            player_ids_to_fetch = [pid for pid in all_player_ids[:5] if pid]
            for i, player_id in enumerate(player_ids_to_fetch):
                player_id_int = int(player_id)
                self.stdout.write(f"Fetching stats for player {i+1}/{len(player_ids_to_fetch)} (ID: {player_id_int})...")
                self.process_player_stats(player_id_int, TEST_SEASON_LABEL) 
                time.sleep(0.2)
        else:
            self.stdout.write(self.style.WARNING("No players were fetched, skipping stats example."))

        self.stdout.write(self.style.SUCCESS("\n--- Scraping complete! ---"))

        # --- NEW: Call the calculation command ---
        self.stdout.write(self.style.WARNING("\n--- Calling table calculation module ---"))
        try:
            # This programmatically runs the 'calculate_tables' command
            management.call_command('calculate_tables')
            self.stdout.write(self.style.SUCCESS("--- Table calculation finished. ---"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error during table calculation: {e}"))
        # --- END NEW ---

    def process_clubs(self, data):
        """Processes club data from the 'clubs' endpoint."""
        if not data or 'content' not in data:
            self.stderr.write("No club data found.")
            return

        clubs = data['content']
        club_objects = []
        for club in clubs:
            # Use .get() to safely access keys
            club_name = club.get('name', 'Unknown Club')
            club_objects.append(Club(
                club_id=club['id'], # 'id' is mandatory, fine to access directly
                club_name=club_name,
                short_name=club.get('shortName', club_name), # Fallback to full name
                abbr=club.get('abbr', 'N/A') # FallBback to N/A
            ))

        Club.objects.bulk_create(
            club_objects,
            update_conflicts=True,
            unique_fields=['club_id'],
            update_fields=['club_name', 'short_name', 'abbr']
        )
        self.stdout.write(f"Upserted {len(club_objects)} clubs.")

    def process_league_table(self, season_label):
        """Fetches and upserts the league table for a *specific season*."""
        
        season_id = SEASON_ID_MAP.get(season_label)
        if not season_id:
            self.stderr.write(f"No API ID found for season {season_label}. Skipping.")
            return

        self.stdout.write(f"Fetching table for {season_label} (API ID: {season_id})...")
        
        # --- FIX: Fallback logic for current season ---
        # The 'standings/current' endpoint returns the current table.
        # The 'standings' endpoint *with* compSeasons returns historical tables.
        
        if season_label == CURRENT_SEASON_LABEL:
            # Use the 'standings/current' endpoint for the current season
            # It doesn't need any params.
            data = self.fetch_api_data("standings/current", params={})
        else:
            # Use the season-specific endpoint for all others
            params = {'page': 0, 'compSeasons': season_id}
            data = self.fetch_api_data("standings", params=params)
        # --- END FIX ---

        if not data or 'tables' not in data or not data['tables']:
            self.stderr.write(f"No table data found for season {season_label}.")
            return

        table_entries = data['tables'][0]['entries']
        table_objects = []

        for entry in table_entries:
            team = entry['team']
            club_id = team['id']

            table_objects.append(LeagueTable(
                club_id=club_id,
                season=season_label, # Add the season label
                position=entry.get('position', 0),
                played=entry.get('played', 0),
                won=entry.get('won', 0),
                drawn=entry.get('drawn', 0),
                lost=entry.get('lost', 0),
                goals_for=entry.get('goalsFor', 0),
                goals_against=entry.get('goalsAgainst', 0),
                points=entry.get('points', 0),
                goal_difference=entry.get('goalDifference', 0),
                form=entry.get('form', 'N/A')[:10]
            ))

        LeagueTable.objects.bulk_create(
            table_objects,
            update_conflicts=True,
            unique_fields=['club', 'season'], # Use the composite key
            update_fields=['position', 'played', 'won', 'drawn', 'lost',
                           'goals_for', 'goals_against', 'points', 'goal_difference', 'form']
        )
        self.stdout.write(f"Upserted {len(table_objects)} league table entries for {season_label}.")

    def process_fixtures(self, data):
        """Processes upcoming fixtures and saves them."""
        if not data or 'content' not in data:
            self.stderr.write("No fixture data found.")
            return

        fixtures = data['content']
        fixture_objects = []

        for fix in fixtures:
            try:
                millis = fix['kickoff']['millis']
                kickoff_dt = datetime.datetime.fromtimestamp(millis / 1000, tz=datetime.timezone.utc)
            except (KeyError, TypeError, ValueError):
                kickoff_dt = None 
            
            fixture_objects.append(Fixture(
                fixture_id=fix['id'],
                kickoff_time=kickoff_dt,
                home_club_id=fix['teams'][0]['team']['id'],
                away_club_id=fix['teams'][1]['team']['id'],
                venue=fix['ground']['name'],
                status='SCHEDULED' # All fixtures from this endpoint are scheduled
            ))

        Fixture.objects.bulk_create(
            fixture_objects,
            update_conflicts=True,
            unique_fields=['fixture_id'],
            update_fields=['kickoff_time', 'home_club', 'away_club', 'venue', 'status']
        )
        self.stdout.write(f"Upserted {len(fixture_objects)} fixtures.")

    def process_results(self, data, season_label=""):
        """Processes completed results and upserts them into the Fixture table."""
        if not data or 'content' not in data:
            self.stderr.write(f"No result data found {('for ' + season_label) if season_label else ''}.")
            return

        results = data['content']
        result_objects = []

        for res in results:
            try:
                home_score = res['teams'][0].get('score')
                away_score = res['teams'][1].get('score')
            except (KeyError, IndexError, TypeError):
                self.stderr.write(f"Skipping result {res.get('id')}: Malformed 'teams' data.")
                continue

            if home_score is None or away_score is None:
                self.stderr.write(f"Skipping result {res.get('id')}: 'score' key not found.")
                continue
            
            try:
                millis = res['kickoff']['millis']
                kickoff_dt = datetime.datetime.fromtimestamp(millis / 1000, tz=datetime.timezone.utc)
            except (KeyError, TypeError, ValueError):
                kickoff_dt = None

            result_objects.append(Fixture(
                fixture_id=res['id'],
                kickoff_time=kickoff_dt,
                home_club_id=res['teams'][0]['team']['id'],
                away_club_id=res['teams'][1]['team']['id'],
                venue=res['ground']['name'],
                status='COMPLETED', # All results from this endpoint are completed
                home_score=home_score,
                away_score=away_score
            ))

        Fixture.objects.bulk_create(
            result_objects,
            update_conflicts=True,
            unique_fields=['fixture_id'],
            update_fields=['kickoff_time', 'home_club', 'away_club', 'venue', 'status', 'home_score', 'away_score']
        )
        self.stdout.write(f"Upserted {len(result_objects)} results {('for ' + season_label) if season_label else ''}.")

    def process_players(self):
        """Fetches all players using pagination and upserts them."""
        known_club_ids = set(Club.objects.values_list('club_id', flat=True))
        all_player_ids = []
        current_page = 0
        total_pages = 1

        while current_page < total_pages:
            self.stdout.write(f"Fetching player page {current_page + 1}/{total_pages}...")
            
            player_params = PARAMS_PLAYERS.copy()
            player_params['page'] = current_page
            
            player_page_data = self.fetch_api_data("players", params=player_params)
            
            if not player_page_data or 'content' not in player_page_data:
                self.stderr.write("No player data on this page. Stopping player fetch.")
                break

            players = player_page_data['content']
            player_objects = []
            
            for p in players:
                player_id = p['id']
                all_player_ids.append(player_id)
                
                nationality = p.get('nationality', {}).get('country', 'Unknown')
                position = p.get('info', {}).get('position', 'Unknown')
                
                current_team = p.get('currentTeam')
                club_id = current_team['id'] if current_team else None
                
                if club_id not in known_club_ids:
                    club_id = None
                
                player_objects.append(Player(
                    player_id=player_id,
                    first_name=p['name']['first'],
                    last_name=p['name']['last'],
                    position=position,
                    nationality=nationality,
                    club_id=club_id
                ))
            
            Player.objects.bulk_create(
                player_objects,
                update_conflicts=True,
                unique_fields=['player_id'],
                update_fields=['first_name', 'last_name', 'position', 'nationality', 'club']
            )

            page_info = player_page_data.get('pageInfo', {})
            total_pages = page_info.get('numPages', current_page + 1)
            current_page += 1
            time.sleep(0.1)

        self.stdout.write(f"Upserted {len(all_player_ids)} players from {total_pages} pages.")
        return all_player_ids

    def process_player_stats(self, player_id, season_label):
        """Fetches and upserts stats for a single player for a specific season."""
        season_id = SEASON_ID_MAP.get(season_label)
        if not season_id:
            return # No season to fetch for

        # Revert to the original stats endpoint
        endpoint = f"stats/player/{player_id}"
        
        # We pass the *correct* season_id now (e.g., 578 for 2023-24)
        params = {'compSeasons': season_id, 'comps': 1} 
        data = self.fetch_api_data(endpoint, params=params)

        if not data or 'stats' not in data:
            # This is expected if a player has no stats for that season
            self.stdout.write(self.style.WARNING(f"No stats found for player {player_id} for {season_label}."))
            return

        stats = {}
        for stat in data['stats']:
            stats[stat['name']] = stat.get('value', 0)
        
        PlayerStat.objects.update_or_create(
            player_id=player_id,
            season=season_label,
            defaults={
                'goals': stats.get('goals', 0),
                'assists': stats.get('goal_assist', 0),
                'clean_sheets': stats.get('clean_sheet', 0),
                'minutes_played': stats.get('mins_played', 0),
                'passes': stats.get('pass_acc', 0), 
                'yellow_cards': stats.get('yellow_card', 0),
                'red_cards': stats.get('red_card', 0)
            }
        )
        self.stdout.write(f"Upserted stats for player {player_id} for {season_label}.")