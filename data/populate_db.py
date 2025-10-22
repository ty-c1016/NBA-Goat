#!/usr/bin/env python3
"""Database population script.

Provides two modes:
- sample: loads `SAMPLE_PLAYERS_DATA` for quick local testing
- api: fetches a subset of real data using `nba_api`

Run:
    python data/populate_db.py --mode sample
    python data/populate_db.py --mode api
"""

import sys
import os

# Add the parent directory to the path so we can import from the models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, CareerStats, AdvancedStats, Achievement
from data.nba_fetcher import NBADataFetcher, get_sample_data
import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_sample_data():
    """Populate database with sample data for testing"""
    logger.info("Starting database population with sample data...")

    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        logger.info("Database tables created")

        # Clear existing data
        db.session.query(Achievement).delete()
        db.session.query(AdvancedStats).delete()
        db.session.query(CareerStats).delete()
        db.session.query(Player).delete()
        db.session.commit()
        logger.info("Existing data cleared")

        sample_data = get_sample_data()

        for player_data in sample_data:
            try:
                # Create Player record
                player = Player(
                    nba_id=player_data['id'],
                    full_name=player_data['full_name'],
                    first_name=player_data['first_name'],
                    last_name=player_data['last_name'],
                    position=player_data['position'],
                    height=player_data['height'],
                    weight=player_data['weight'],
                    from_year=player_data['from_year'],
                    to_year=player_data['to_year'],
                    is_active=player_data['is_active'],
                    teams=player_data['teams']
                )
                db.session.add(player)
                db.session.flush()  # Get the player ID

                # Create CareerStats record
                career_stats_data = player_data['career_stats']
                career_stats = CareerStats(
                    player_id=player.id,
                    games_played=career_stats_data['games_played'],
                    points_per_game=career_stats_data['points_per_game'],
                    rebounds_per_game=career_stats_data['rebounds_per_game'],
                    assists_per_game=career_stats_data['assists_per_game'],
                    field_goal_percentage=career_stats_data['field_goal_percentage'],
                    total_points=career_stats_data['total_points']
                )
                db.session.add(career_stats)

                # Create Achievement record
                achievements_data = player_data['achievements']
                achievements = Achievement(
                    player_id=player.id,
                    championships=achievements_data.get('championships', 0),
                    mvp_awards=achievements_data.get('mvp_awards', 0),
                    finals_mvp_awards=achievements_data.get('finals_mvp_awards', 0),
                    all_star_selections=achievements_data.get('all_star_selections', 0),
                    all_nba_first_team=achievements_data.get('all_nba_first_team', 0),
                    hall_of_fame=achievements_data.get('hall_of_fame', False)
                )
                db.session.add(achievements)

                logger.info(f"Added player: {player.full_name}")

            except Exception as e:
                logger.error(f"Error adding player {player_data['full_name']}: {e}")
                db.session.rollback()
                continue

        # Commit all changes
        db.session.commit()
        logger.info(f"Successfully populated database with {len(sample_data)} players")

        # Verify the data
        player_count = Player.query.count()
        logger.info(f"Total players in database: {player_count}")

def populate_from_api():
    """Populate database from NBA API (for production use)"""
    logger.info("Starting database population from NBA API...")

    app = create_app()
    fetcher = NBADataFetcher()

    with app.app_context():
        db.create_all()

        # Get all players from NBA API
        all_players = fetcher.get_all_players()
        logger.info(f"Found {len(all_players)} players to process")

        # Process all players
        logger.info("Processing all NBA players from API...")
        for i, player_data in enumerate(all_players):
            try:
                logger.info(f"Processing player {i+1}/{len(all_players)}: {player_data['full_name']}")

                # Check if player already exists
                existing_player = Player.query.filter_by(nba_id=player_data['id']).first()
                if existing_player:
                    logger.info(f"Player {player_data['full_name']} already exists, skipping...")
                    continue

                # Create Player record
                player = Player(
                    nba_id=player_data['id'],
                    full_name=player_data['full_name'],
                    first_name=player_data.get('first_name', ''),
                    last_name=player_data.get('last_name', ''),
                    is_active=player_data.get('is_active', False)
                )
                db.session.add(player)
                db.session.flush()

                # Get career stats
                career_stats_df = fetcher.get_player_career_stats(player_data['id'])
                if career_stats_df is not None and not career_stats_df.empty:
                    stats_row = career_stats_df.iloc[0]  # Get career totals

                    games_played = max(stats_row.get('GP', 1) or 1, 1)  # Avoid division by zero

                    # Convert numpy types to Python native types for PostgreSQL compatibility
                    def to_python_type(value):
                        if value is None:
                            return 0
                        try:
                            # Handle NaN values
                            import math
                            if hasattr(value, 'dtype'):
                                # It's a numpy type
                                float_val = float(value)
                                return 0 if math.isnan(float_val) else float_val
                            return value or 0
                        except (TypeError, ValueError):
                            return 0

                    career_stats = CareerStats(
                        player_id=player.id,
                        games_played=int(to_python_type(stats_row.get('GP', 0))),
                        points_per_game=float(to_python_type(stats_row.get('PTS', 0)) / games_played),
                        rebounds_per_game=float(to_python_type(stats_row.get('REB', 0)) / games_played),
                        assists_per_game=float(to_python_type(stats_row.get('AST', 0)) / games_played),
                        steals_per_game=float(to_python_type(stats_row.get('STL', 0)) / games_played),
                        blocks_per_game=float(to_python_type(stats_row.get('BLK', 0)) / games_played),
                        field_goal_percentage=float(to_python_type(stats_row.get('FG_PCT', 0))),
                        three_point_percentage=float(to_python_type(stats_row.get('FG3_PCT', 0))),
                        free_throw_percentage=float(to_python_type(stats_row.get('FT_PCT', 0))),
                        total_points=int(to_python_type(stats_row.get('PTS', 0))),
                        total_rebounds=int(to_python_type(stats_row.get('REB', 0))),
                        total_assists=int(to_python_type(stats_row.get('AST', 0)))
                    )
                    db.session.add(career_stats)

                # Get awards and achievements from API
                awards_df = fetcher.get_player_awards(player_data['id'])
                championships = 0
                finals_appearances = 0
                mvp_awards = 0
                finals_mvp_awards = 0
                all_star_selections = 0

                if awards_df is not None and not awards_df.empty:
                    # Count championships (NBA Finals wins)
                    championships = len(awards_df[awards_df['DESCRIPTION'].str.contains('NBA Champion', case=False, na=False)])

                    # Count finals appearances (estimate as championships + runner-up mentions)
                    finals_appearances = championships + len(awards_df[awards_df['DESCRIPTION'].str.contains('Finals|Runner-up', case=False, na=False)])

                    # Count MVP awards
                    mvp_awards = len(awards_df[awards_df['DESCRIPTION'].str.contains('Most Valuable Player', case=False, na=False)])

                    # Count Finals MVP awards
                    finals_mvp_awards = len(awards_df[awards_df['DESCRIPTION'].str.contains('Finals MVP', case=False, na=False)])

                    # Count All-Star selections
                    all_star_selections = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-Star', case=False, na=False)])

                achievements = Achievement(
                    player_id=player.id,
                    championships=championships,
                    finals_appearances=finals_appearances,
                    mvp_awards=mvp_awards,
                    finals_mvp_awards=finals_mvp_awards,
                    all_star_selections=all_star_selections
                )
                db.session.add(achievements)

                db.session.commit()
                logger.info(f"Successfully added {player_data['full_name']}")

            except Exception as e:
                logger.error(f"Error processing player {player_data.get('full_name', 'Unknown')}: {e}")
                db.session.rollback()
                continue

        logger.info("Database population completed")

def main():
    """Main function to run the population script"""
    import argparse

    parser = argparse.ArgumentParser(description='Populate NBA database')
    parser.add_argument('--mode', choices=['sample', 'api'], default='sample',
                       help='Mode for populating data: sample (test data) or api (real NBA data)')

    args = parser.parse_args()

    if args.mode == 'sample':
        populate_sample_data()
    elif args.mode == 'api':
        populate_from_api()

if __name__ == "__main__":
    main()