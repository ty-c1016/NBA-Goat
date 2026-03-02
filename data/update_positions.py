#!/usr/bin/env python3
"""Update position, height, weight, and year data for all players."""

import sys
import os
import time
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app import create_app
from models import db, Player
from nba_api.stats.endpoints import commonplayerinfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_player_positions():
    app = create_app()
    with app.app_context():
        players = Player.query.all()
        updated = failed = skipped = 0

        for i, player in enumerate(players, 1):
            if player.position and player.height and player.from_year and player.to_year:
                skipped += 1
                continue

            try:
                time.sleep(0.6)
                info = commonplayerinfo.CommonPlayerInfo(player_id=player.nba_id)
                df = info.get_data_frames()[0]

                if len(df) == 0:
                    failed += 1
                    logger.warning(f"✗ [{i}/{len(players)}] No data for {player.full_name}")
                    continue

                row = df.iloc[0]
                player.position = row['POSITION'] if pd.notna(row['POSITION']) else None
                player.height = row['HEIGHT'] if pd.notna(row['HEIGHT']) else None
                player.weight = int(row['WEIGHT']) if pd.notna(row['WEIGHT']) and row['WEIGHT'] else None
                player.from_year = int(row['FROM_YEAR']) if pd.notna(row['FROM_YEAR']) else None
                player.to_year = int(row['TO_YEAR']) if pd.notna(row['TO_YEAR']) else None

                if pd.notna(row['BIRTHDATE']):
                    try:
                        player.birth_date = datetime.strptime(row['BIRTHDATE'][:10], '%Y-%m-%d').date()
                    except Exception:
                        pass

                updated += 1
                logger.info(f"✓ [{i}/{len(players)}] {player.full_name}: {player.position}, {player.height}, {player.weight} lbs")

                if i % 10 == 0:
                    db.session.commit()

            except Exception as e:
                failed += 1
                logger.error(f"✗ [{i}/{len(players)}] Error updating {player.full_name}: {e}")

        db.session.commit()
        logger.info(f"Done. Updated: {updated}, skipped: {skipped}, failed: {failed}")


if __name__ == '__main__':
    update_player_positions()
