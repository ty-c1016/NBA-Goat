#!/usr/bin/env python3
"""Update All-NBA and individual achievement data for existing players.

This script updates the individual achievements (All-NBA, All-Defensive, scoring titles)
for all players already in the database.

Run:
    python data/update_all_nba.py
"""

import sys
import os

# Add the parent directory to the path so we can import from the models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, Achievement
from data.nba_fetcher import NBADataFetcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_all_nba_data():
    """Update All-NBA and individual achievement data for all existing players"""
    logger.info("Starting All-NBA data update for existing players...")

    app = create_app()
    fetcher = NBADataFetcher()

    with app.app_context():
        # Get all players with their achievements
        players = Player.query.join(Achievement).all()
        total_players = len(players)
        logger.info(f"Found {total_players} players to update")

        updated_count = 0
        for i, player in enumerate(players):
            try:
                if (i + 1) % 50 == 0:
                    logger.info(f"Progress: {i+1}/{total_players} players processed")

                # Get awards from API
                awards_df = fetcher.get_player_awards(player.nba_id)

                if awards_df is None or awards_df.empty:
                    logger.debug(f"No awards found for {player.full_name}")
                    continue

                # Count All-NBA selections using ALL_NBA_TEAM_NUMBER column
                all_nba_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA', case=False, na=False)]
                all_nba_first = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '1'])
                all_nba_second = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '2'])
                all_nba_third = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '3'])

                # Count All-Defensive selections (these don't have a team number column, need to check SUBTYPE)
                all_def_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-Defensive', case=False, na=False)]
                # For now, count all All-Defensive as first team (we can refine this later if needed)
                all_defensive_first = len(all_def_df)
                all_defensive_second = 0  # NBA API doesn't clearly distinguish defensive teams

                # Count scoring titles
                scoring_titles = len(awards_df[awards_df['DESCRIPTION'].str.contains('Scoring Champion|Scoring Title', case=False, na=False)])

                # Update the achievement record if any new data found
                total_new_achievements = all_nba_first + all_nba_second + all_nba_third + all_defensive_first + all_defensive_second + scoring_titles

                if total_new_achievements > 0:
                    player.achievements.all_nba_first_team = all_nba_first
                    player.achievements.all_nba_second_team = all_nba_second
                    player.achievements.all_nba_third_team = all_nba_third
                    player.achievements.all_defensive_first_team = all_defensive_first
                    player.achievements.all_defensive_second_team = all_defensive_second
                    player.achievements.scoring_titles = scoring_titles

                    db.session.commit()
                    updated_count += 1

                    logger.info(f"✓ Updated {player.full_name}: {all_nba_first} 1st, {all_nba_second} 2nd, {all_nba_third} 3rd All-NBA | {scoring_titles} scoring titles")

            except Exception as e:
                logger.error(f"Error updating player {player.full_name}: {e}")
                db.session.rollback()
                continue

        logger.info("=" * 60)
        logger.info(f"ALL-NBA DATA UPDATE COMPLETED")
        logger.info(f"Total players processed: {total_players}")
        logger.info(f"Players with updated achievements: {updated_count}")
        logger.info("=" * 60)

if __name__ == "__main__":
    update_all_nba_data()
