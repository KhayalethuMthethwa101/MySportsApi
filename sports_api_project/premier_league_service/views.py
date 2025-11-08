from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from . import services
from . import serializers

class LeagueTableView(APIView):
    """
    API View to get the Premier League table.
    
    Query Params:
    - ?season=YYYY-YYYY (e.g., 2023-2024)
    """
    
    def get(self, request):
        # Get season from query param, default to a recent one
        season = request.GET.get('season', '2024-2025')
        
        try:
            # 1. Call the service layer to get the data
            table_data = services.get_league_table_data(season)
            
            # 2. Serialize the data
            serializer = serializers.LeagueTableEntrySerializer(table_data, many=True)
            
            # 3. Return the response
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PlayerStatsView(APIView):
    """
    API View to get player stats.
    
    Query Params:
    - ?season=YYYY-YYYY (e.g., 2023-2024)
    - ?stat=goals (default) or 'assists'
    - ?team=Arsenal (optional team name)
    """
    
    def get(self, request):
        season = request.GET.get('season', '2024-2025')
        stat_type = request.GET.get('stat', 'goals').lower()
        team_filter = request.GET.get('team', None)
        
        try:
            # 1. Validate stat_type
            if stat_type not in ['goals', 'assists']:
                return Response({"error": "Invalid 'stat' parameter. Use 'goals' or 'assists'."}, status=status.HTTP_400_BAD_REQUEST)
                
            # 2. Call the service layer
            player_data = services.get_player_stats_data(season, stat_type)
            
            # 3. (Optional) Filter the data by team
            if team_filter:
                team_filter_lower = team_filter.lower()
                player_data = [
                    player for player in player_data
                    if player.get('club', '').lower() == team_filter_lower
                ]
            
            # 4. Serialize the data
            serializer = serializers.PlayerStatSerializer(player_data, many=True)
            
            # 5. Return the response
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404 as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)