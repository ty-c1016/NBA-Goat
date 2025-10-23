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

def populate_from_api(min_games=400, min_seasons=10, min_ppg=10.0):
    """Populate database from NBA API with qualified GOAT candidates

    Args:
        min_games: Minimum games played to be considered (default 400)
        min_seasons: Minimum seasons played (default 10)
        min_ppg: Minimum career points per game (default 10.0)
    """
    logger.info("Starting database population from NBA API...")
    logger.info(f"GOAT Candidate Criteria:")
    logger.info(f"  - At least {min_games} games played")
    logger.info(f"  - At least {min_seasons} seasons")
    logger.info(f"  - At least {min_ppg} PPG career average")

    app = create_app()
    fetcher = NBADataFetcher()

    with app.app_context():
        db.create_all()

        # Don't clear existing data - we'll skip players that already exist
        existing_count = Player.query.count()
        logger.info(f"Database has {existing_count} existing players - will skip duplicates")

        # Get all players from NBA API
        all_players = fetcher.get_all_players()
        logger.info(f"Found {len(all_players)} total players from NBA API")

        # Process all players, but only save those meeting criteria
        logger.info("Processing NBA players and filtering for GOAT candidates...")
        qualified_count = 0
        for i, player_data in enumerate(all_players):
            try:
                if (i + 1) % 100 == 0:
                    logger.info(f"Progress: {i+1}/{len(all_players)} players checked, {qualified_count} qualified so far")

                # Skip if player already exists
                existing_player = Player.query.filter_by(nba_id=player_data['id']).first()
                if existing_player:
                    continue

                # Create Player record (we'll add to DB only if they qualify)
                player = Player(
                    nba_id=player_data['id'],
                    full_name=player_data['full_name'],
                    first_name=player_data.get('first_name', ''),
                    last_name=player_data.get('last_name', ''),
                    is_active=player_data.get('is_active', False)
                )
                db.session.add(player)
                db.session.flush()

                # Get career stats - NBA API returns multiple rows (one per season)
                career_stats_df = fetcher.get_player_career_stats(player_data['id'])
                if career_stats_df is None or career_stats_df.empty:
                    logger.debug(f"No career stats found for {player_data['full_name']}, skipping...")
                    continue

                # Calculate career totals and averages for filtering
                num_seasons = len(career_stats_df)
                total_games = int(career_stats_df['GP'].sum())
                total_points = int(career_stats_df['PTS'].sum())
                career_ppg = total_points / total_games if total_games > 0 else 0

                # Apply all filters
                if total_games < min_games:
                    logger.debug(f"Skip {player_data['full_name']}: {total_games} games < {min_games}")
                    continue

                if num_seasons < min_seasons:
                    logger.debug(f"Skip {player_data['full_name']}: {num_seasons} seasons < {min_seasons}")
                    continue

                if career_ppg < min_ppg:
                    logger.debug(f"Skip {player_data['full_name']}: {career_ppg:.1f} PPG < {min_ppg}")
                    continue

                logger.info(f"✓ {player_data['full_name']}: {num_seasons} seasons, {total_games} games, {career_ppg:.1f} PPG - QUALIFIED")
                qualified_count += 1

                if career_stats_df is not None and not career_stats_df.empty:
                    # Aggregate all seasons to get true career totals
                    import math

                    def to_python_type(value):
                        """Convert numpy types to Python native types for PostgreSQL compatibility"""
                        if value is None:
                            return 0
                        try:
                            # Handle NaN values
                            if hasattr(value, 'dtype'):
                                # It's a numpy type
                                float_val = float(value)
                                return 0 if math.isnan(float_val) else float_val
                            return value or 0
                        except (TypeError, ValueError):
                            return 0

                    # Sum totals across all seasons
                    total_games = int(career_stats_df['GP'].sum())
                    total_points = int(career_stats_df['PTS'].sum())
                    total_rebounds = int(career_stats_df['REB'].sum())
                    total_assists = int(career_stats_df['AST'].sum())
                    total_steals = int(career_stats_df['STL'].sum() if 'STL' in career_stats_df.columns else 0)
                    total_blocks = int(career_stats_df['BLK'].sum() if 'BLK' in career_stats_df.columns else 0)

                    # Calculate weighted averages for percentages
                    total_fgm = career_stats_df['FGM'].sum() if 'FGM' in career_stats_df.columns else 0
                    total_fga = career_stats_df['FGA'].sum() if 'FGA' in career_stats_df.columns else 0
                    total_fg3m = career_stats_df['FG3M'].sum() if 'FG3M' in career_stats_df.columns else 0
                    total_fg3a = career_stats_df['FG3A'].sum() if 'FG3A' in career_stats_df.columns else 0
                    total_ftm = career_stats_df['FTM'].sum() if 'FTM' in career_stats_df.columns else 0
                    total_fta = career_stats_df['FTA'].sum() if 'FTA' in career_stats_df.columns else 0

                    # Avoid division by zero
                    games_played = max(total_games, 1)

                    # Calculate true career averages
                    ppg = float(total_points / games_played)
                    rpg = float(total_rebounds / games_played)
                    apg = float(total_assists / games_played)
                    spg = float(total_steals / games_played)
                    bpg = float(total_blocks / games_played)

                    # Calculate shooting percentages from totals (more accurate than averaging percentages)
                    fg_pct = float(total_fgm / total_fga) if total_fga > 0 else 0.0
                    fg3_pct = float(total_fg3m / total_fg3a) if total_fg3a > 0 else 0.0
                    ft_pct = float(total_ftm / total_fta) if total_fta > 0 else 0.0

                    career_stats = CareerStats(
                        player_id=player.id,
                        games_played=total_games,
                        points_per_game=to_python_type(ppg),
                        rebounds_per_game=to_python_type(rpg),
                        assists_per_game=to_python_type(apg),
                        steals_per_game=to_python_type(spg),
                        blocks_per_game=to_python_type(bpg),
                        field_goal_percentage=to_python_type(fg_pct),
                        three_point_percentage=to_python_type(fg3_pct),
                        free_throw_percentage=to_python_type(ft_pct),
                        total_points=total_points,
                        total_rebounds=total_rebounds,
                        total_assists=total_assists
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

            except Exception as e:
                logger.error(f"Error processing player {player_data.get('full_name', 'Unknown')}: {e}")
                db.session.rollback()
                continue

        # Final summary
        final_count = Player.query.count()
        logger.info("=" * 60)
        logger.info(f"DATABASE POPULATION COMPLETED")
        logger.info(f"Total players checked: {len(all_players)}")
        logger.info(f"Players with {min_games}+ games: {qualified_count}")
        logger.info(f"Successfully added to database: {final_count}")
        logger.info("=" * 60)

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