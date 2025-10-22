"""NBA API data fetching utilities.

Encapsulates calls to `nba_api` for player lists, career stats, and awards.
Includes sample data and helpers for development without external API calls.
"""

import requests
import pandas as pd
import time
from nba_api.stats.endpoints import commonallplayers, playercareerstats, playerawards
from nba_api.stats.static import players
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NBADataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_all_players(self):
        """Get basic information for all NBA players"""
        try:
            logger.info("Fetching all players...")
            all_players = players.get_players()
            logger.info(f"Retrieved {len(all_players)} players")
            return all_players
        except Exception as e:
            logger.error(f"Error fetching players: {e}")
            return []

    def get_player_career_stats(self, player_id):
        """Get career statistics for a specific player"""
        try:
            time.sleep(0.6)  # Rate limiting
            career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
            return career_stats.get_data_frames()[0]  # Career totals regular season
        except Exception as e:
            logger.error(f"Error fetching career stats for player {player_id}: {e}")
            return None

    def get_player_awards(self, player_id):
        """Get awards and achievements for a specific player"""
        try:
            time.sleep(0.6)  # Rate limiting
            awards = playerawards.PlayerAwards(player_id=player_id)
            return awards.get_data_frames()[0]
        except Exception as e:
            logger.error(f"Error fetching awards for player {player_id}: {e}")
            return None

    def get_active_players(self):
        """Get list of currently active players"""
        try:
            active_players = commonallplayers.CommonAllPlayers(is_only_current_season=1)
            return active_players.get_data_frames()[0]
        except Exception as e:
            logger.error(f"Error fetching active players: {e}")
            return pd.DataFrame()

    def get_historical_players(self):
        """Get list of historical players"""
        try:
            all_players = commonallplayers.CommonAllPlayers(is_only_current_season=0)
            return all_players.get_data_frames()[0]
        except Exception as e:
            logger.error(f"Error fetching historical players: {e}")
            return pd.DataFrame()

# Sample data for testing without API calls
SAMPLE_PLAYERS_DATA = [
    {
        'id': 2544, 'full_name': 'LeBron James', 'first_name': 'LeBron', 'last_name': 'James',
        'is_active': True, 'position': 'F', 'height': '6-9', 'weight': 250,
        'from_year': 2003, 'to_year': 2024, 'teams': '["CLE", "MIA", "LAL"]',
        'career_stats': {
            'games_played': 1421, 'points_per_game': 27.2, 'rebounds_per_game': 7.5,
            'assists_per_game': 7.3, 'field_goal_percentage': 0.505, 'total_points': 38652
        },
        'achievements': {
            'championships': 4, 'mvp_awards': 4, 'finals_mvp_awards': 4,
            'all_star_selections': 19, 'all_nba_first_team': 13
        }
    },
    {
        'id': 1628369, 'full_name': 'Jayson Tatum', 'first_name': 'Jayson', 'last_name': 'Tatum',
        'is_active': True, 'position': 'F', 'height': '6-8', 'weight': 210,
        'from_year': 2017, 'to_year': 2024, 'teams': '["BOS"]',
        'career_stats': {
            'games_played': 513, 'points_per_game': 23.1, 'rebounds_per_game': 7.2,
            'assists_per_game': 3.5, 'field_goal_percentage': 0.457, 'total_points': 11854
        },
        'achievements': {
            'championships': 1, 'mvp_awards': 0, 'finals_mvp_awards': 0,
            'all_star_selections': 5, 'all_nba_first_team': 1
        }
    },
    {
        'id': 977, 'full_name': 'Michael Jordan', 'first_name': 'Michael', 'last_name': 'Jordan',
        'is_active': False, 'position': 'G', 'height': '6-6', 'weight': 218,
        'from_year': 1984, 'to_year': 2003, 'teams': '["CHI", "WAS"]',
        'career_stats': {
            'games_played': 1072, 'points_per_game': 30.1, 'rebounds_per_game': 6.2,
            'assists_per_game': 5.3, 'field_goal_percentage': 0.497, 'total_points': 32292
        },
        'achievements': {
            'championships': 6, 'mvp_awards': 5, 'finals_mvp_awards': 6,
            'all_star_selections': 14, 'all_nba_first_team': 10, 'hall_of_fame': True
        }
    },
    {
        'id': 76001, 'full_name': 'Kobe Bryant', 'first_name': 'Kobe', 'last_name': 'Bryant',
        'is_active': False, 'position': 'G', 'height': '6-6', 'weight': 212,
        'from_year': 1996, 'to_year': 2016, 'teams': '["LAL"]',
        'career_stats': {
            'games_played': 1346, 'points_per_game': 25.0, 'rebounds_per_game': 5.2,
            'assists_per_game': 4.7, 'field_goal_percentage': 0.447, 'total_points': 33643
        },
        'achievements': {
            'championships': 5, 'mvp_awards': 1, 'finals_mvp_awards': 2,
            'all_star_selections': 18, 'all_nba_first_team': 11, 'hall_of_fame': True
        }
    },
    {
        'id': 76003, 'full_name': 'Tim Duncan', 'first_name': 'Tim', 'last_name': 'Duncan',
        'is_active': False, 'position': 'F-C', 'height': '6-11', 'weight': 250,
        'from_year': 1997, 'to_year': 2016, 'teams': '["SAS"]',
        'career_stats': {
            'games_played': 1392, 'points_per_game': 19.0, 'rebounds_per_game': 10.8,
            'assists_per_game': 3.0, 'field_goal_percentage': 0.506, 'total_points': 26496
        },
        'achievements': {
            'championships': 5, 'mvp_awards': 2, 'finals_mvp_awards': 3,
            'all_star_selections': 15, 'all_nba_first_team': 10, 'hall_of_fame': True
        }
    }
]

def get_sample_data():
    """Returns sample data for testing purposes"""
    return SAMPLE_PLAYERS_DATA