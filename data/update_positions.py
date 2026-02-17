#!/usr/bin/env python3
"""Script to populate position data for all players using NBA API.

Uses the CommonPlayerInfo endpoint to fetch position, height, and weight data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player
from nba_api.stats.endpoints import commonplayerinfo
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_player_positions():
    """Fetch and update position data for all players"""
    app = create_app()

    with app.app_context():
        players = Player.query.all()

        updated_count = 0
        failed_count = 0
        skipped_count = 0

        logger.info(f"Found {len(players)} players to update")

        for i, player in enumerate(players, 1):
            # Skip if already has all data (position, height, weight, years)
            if player.position and player.height and player.from_year and player.to_year:
                skipped_count += 1
                if i % 50 == 0:
                    logger.info(f"Progress: {i}/{len(players)} - {player.full_name} (already has all data)")
                continue

            try:
                # Rate limiting - NBA API is sensitive
                time.sleep(0.6)

                # Fetch player info
                info = commonplayerinfo.CommonPlayerInfo(player_id=player.nba_id)
                df = info.get_data_frames()[0]

                if len(df) > 0:
                    row = df.iloc[0]

                    # Update player data
                    player.position = row['POSITION'] if pd.notna(row['POSITION']) else None
                    player.height = row['HEIGHT'] if pd.notna(row['HEIGHT']) else None
                    player.weight = int(row['WEIGHT']) if pd.notna(row['WEIGHT']) and row['WEIGHT'] else None
                    player.from_year = int(row['FROM_YEAR']) if pd.notna(row['FROM_YEAR']) else None
                    player.to_year = int(row['TO_YEAR']) if pd.notna(row['TO_YEAR']) else None

                    # Update birth_date if available
                    if pd.notna(row['BIRTHDATE']):
                        from datetime import datetime
                        try:
                            player.birth_date = datetime.strptime(row['BIRTHDATE'][:10], '%Y-%m-%d').date()
                        except:
                            pass

                    updated_count += 1
                    logger.info(f"✓ [{i}/{len(players)}] Updated {player.full_name}: {player.position}, {player.height}, {player.weight} lbs")
                else:
                    failed_count += 1
                    logger.warning(f"✗ [{i}/{len(players)}] No data found for {player.full_name}")

                # Commit every 10 players to avoid losing progress
                if i % 10 == 0:
                    db.session.commit()
                    logger.info(f"--- Checkpoint: {i}/{len(players)} processed ---")

            except Exception as e:
                failed_count += 1
                logger.error(f"✗ [{i}/{len(players)}] Error updating {player.full_name}: {e}")
                continue

        # Final commit
        db.session.commit()

        logger.info(f"\n{'='*60}")
        logger.info(f"Position Update Summary:")
        logger.info(f"  Updated: {updated_count} players")
        logger.info(f"  Skipped (already had data): {skipped_count} players")
        logger.info(f"  Failed: {failed_count} players")
        logger.info(f"  Total: {len(players)} players")
        logger.info(f"{'='*60}")

if __name__ == '__main__':
    import pandas as pd
    update_player_positions()
