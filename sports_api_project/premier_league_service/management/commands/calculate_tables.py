import sys
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import F, Q
from premier_league_service.models import Club, LeagueTable, Fixture
# We import the season map from the scraper to know which seasons to process
from premier_league_service.management.commands.run_scraper import SEASON_ID_MAP

class Command(BaseCommand):
    help = 'Calculates league table standings based on completed fixtures stored in the database.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting league table calculation from results...")

        # Get all season labels from the scraper's map
        seasons = SEASON_ID_MAP.keys()
        
        for season in seasons:
            self.stdout.write(f"\n--- Calculating table for {season} ---")
            
            # 1. Get all completed fixtures for this season.
            # We filter by kickoff time to approximate the season's matches.
            try:
                start_year = int(season.split('-')[0])
                end_year = int(season.split('-')[1])
            except (ValueError, IndexError):
                self.stderr.write(self.style.ERROR(f"Invalid season format: {season}. Skipping."))
                continue

            season_fixtures = Fixture.objects.filter(
                status='COMPLETED',
                kickoff_time__year__gte=start_year,
                kickoff_time__year__lte=end_year
            ).select_related('home_club', 'away_club')

            if not season_fixtures.exists():
                self.stdout.write(self.style.WARNING(f"No completed fixtures found for {season}. Skipping."))
                continue

            # 2. Initialize a stats dictionary for each club
            # Get all clubs that participated in this season's fixtures
            club_ids = set(season_fixtures.values_list('home_club_id', flat=True)) | \
                       set(season_fixtures.values_list('away_club_id', flat=True))
            
            # Use defaultdict to automatically create a new stat dict for each club
            table_stats = defaultdict(lambda: defaultdict(int))

            # 3. Iterate over each match and update stats
            for fixture in season_fixtures:
                home_id = fixture.home_club_id
                away_id = fixture.away_club_id
                
                # Ensure scores are not None
                home_goals = fixture.home_score or 0
                away_goals = fixture.away_score or 0

                # Update common stats for both teams
                table_stats[home_id]['played'] += 1
                table_stats[away_id]['played'] += 1
                table_stats[home_id]['goals_for'] += home_goals
                table_stats[away_id]['goals_for'] += away_goals
                table_stats[home_id]['goals_against'] += away_goals
                table_stats[away_id]['goals_against'] += home_goals

                # Determine Win/Draw/Loss and assign points
                if home_goals > away_goals:
                    # Home win
                    table_stats[home_id]['won'] += 1
                    table_stats[home_id]['points'] += 3
                    table_stats[away_id]['lost'] += 1
                elif home_goals < away_goals:
                    # Away win
                    table_stats[away_id]['won'] += 1
                    table_stats[away_id]['points'] += 3
                    table_stats[home_id]['lost'] += 1
                else:
                    # Draw
                    table_stats[home_id]['drawn'] += 1
                    table_stats[home_id]['points'] += 1
                    table_stats[away_id]['drawn'] += 1
                    table_stats[away_id]['points'] += 1

            # 4. Calculate GD and create a sorted list for position
            calculated_table = []
            for club_id, stats in table_stats.items():
                stats['goal_difference'] = stats['goals_for'] - stats['goals_against']
                stats['club_id'] = club_id # Add club_id for sorting
                calculated_table.append(stats)
            
            # 5. Sort the table to determine position
            # Sort by points (desc), then GD (desc), then GF (desc)
            calculated_table.sort(
                key=lambda x: (x['points'], x['goal_difference'], x['goals_for']),
                reverse=True
            )

            # 6. Upsert the calculated data into the LeagueTable model
            update_count = 0
            for i, stats in enumerate(calculated_table):
                position = i + 1
                
                # This will overwrite the data from the scraper with our
                # more accurate, calculated data.
                _, created = LeagueTable.objects.update_or_create(
                    club_id=stats['club_id'],
                    season=season,
                    defaults={
                        'position': position,
                        'played': stats['played'],
                        'won': stats['won'],
                        'drawn': stats['drawn'],
                        'lost': stats['lost'],
                        'goals_for': stats['goals_for'],
                        'goals_against': stats['goals_against'],
                        'points': stats['points'],
                        'goal_difference': stats['goal_difference'],
                        'form': '' # We don't calculate form, so we leave it blank
                    }
                )
                if not created:
                    update_count += 1

            self.stdout.write(f"Processed {len(season_fixtures)} fixtures for {len(calculated_table)} clubs.")
            self.stdout.write(f"Updated {update_count} and created {len(calculated_table) - update_count} league table entries for {season}.")

        self.stdout.write(self.style.SUCCESS("\n--- League table calculation complete! ---"))