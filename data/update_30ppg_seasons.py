#!/usr/bin/env python3
"""Update 30+ PPG seasons data for existing players.

This script fetches season-by-season stats and counts how many seasons
each player averaged 30+ PPG.

Run:
    python data/update_30ppg_seasons.py
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

def update_30ppg_seasons():
    """Update 30+ PPG seasons count for all existing players"""
    logger.info("Starting 30+ PPG seasons data update for existing players...")

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

                # Get season-by-season career stats
                career_stats_df = fetcher.get_player_career_stats(player.nba_id)

                if career_stats_df is None or career_stats_df.empty:
                    logger.debug(f"No career stats found for {player.full_name}")
                    continue

                # Count seasons with 30+ PPG
                # The dataframe has a 'PTS' column for total points and 'GP' for games played
                # Calculate PPG for each season and count those >= 30
                career_stats_df['PPG'] = career_stats_df['PTS'] / career_stats_df['GP']
                seasons_30ppg = len(career_stats_df[career_stats_df['PPG'] >= 30.0])

                if seasons_30ppg > 0:
                    player.achievements.seasons_30ppg = seasons_30ppg
                    db.session.commit()
                    updated_count += 1

                    logger.info(f"✓ Updated {player.full_name}: {seasons_30ppg} seasons with 30+ PPG")

            except Exception as e:
                logger.error(f"Error updating player {player.full_name}: {e}")
                db.session.rollback()
                continue

        logger.info("=" * 60)
        logger.info(f"30+ PPG SEASONS DATA UPDATE COMPLETED")
        logger.info(f"Total players processed: {total_players}")
        logger.info(f"Players with 30+ PPG seasons: {updated_count}")
        logger.info("=" * 60)

if __name__ == "__main__":
    update_30ppg_seasons()
