#!/usr/bin/env python3
"""Update 30+ PPG seasons count for all players."""

import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, Achievement
from data.nba_fetcher import NBADataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_30ppg_seasons():
    app = create_app()
    fetcher = NBADataFetcher()

    with app.app_context():
        players = Player.query.join(Achievement).all()
        updated = 0

        for i, player in enumerate(players):
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i+1}/{len(players)}")

            try:
                career_stats_df = fetcher.get_player_career_stats(player.nba_id)
                if career_stats_df is None or career_stats_df.empty:
                    continue

                career_stats_df['PPG'] = career_stats_df['PTS'] / career_stats_df['GP']
                seasons_30ppg = len(career_stats_df[career_stats_df['PPG'] >= 30.0])

                if seasons_30ppg > 0:
                    player.achievements.seasons_30ppg = seasons_30ppg
                    db.session.commit()
                    updated += 1
                    logger.info(f"✓ {player.full_name}: {seasons_30ppg} seasons with 30+ PPG")

            except Exception as e:
                logger.error(f"Error updating {player.full_name}: {e}")
                db.session.rollback()

        logger.info(f"Done. {updated} players with 30+ PPG seasons.")


if __name__ == "__main__":
    update_30ppg_seasons()
