#!/usr/bin/env python3
"""Fetch and populate season-by-season stats for all players."""

import sys
import os
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, SeasonStats
from nba_api.stats.endpoints import playercareerstats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_season_stats():
    app = create_app()
    with app.app_context():
        players = Player.query.all()
        updated = failed = seasons_added = 0

        for i, player in enumerate(players, 1):
            if SeasonStats.query.filter_by(player_id=player.id).first():
                logger.info(f"[{i}/{len(players)}] {player.full_name} already has season stats, skipping")
                continue

            try:
                time.sleep(0.6)
                career = playercareerstats.PlayerCareerStats(
                    player_id=player.nba_id,
                    per_mode36='PerGame'
                )
                season_df = career.get_data_frames()[0]

                if len(season_df) == 0:
                    failed += 1
                    logger.warning(f"✗ [{i}/{len(players)}] No season data for {player.full_name}")
                    continue

                for _, row in season_df.iterrows():
                    db.session.add(SeasonStats(
                        player_id=player.id,
                        season=row['SEASON_ID'],
                        team_id=row.get('TEAM_ID'),
                        team_abbreviation=row.get('TEAM_ABBREVIATION'),
                        games_played=int(row['GP']) if row['GP'] else 0,
                        games_started=int(row['GS']) if row['GS'] else 0,
                        minutes_per_game=float(row['MIN']) if row['MIN'] else 0.0,
                        points_per_game=float(row['PTS']) if row['PTS'] else 0.0,
                        rebounds_per_game=float(row['REB']) if row['REB'] else 0.0,
                        assists_per_game=float(row['AST']) if row['AST'] else 0.0,
                        field_goal_percentage=float(row['FG_PCT']) if row['FG_PCT'] else 0.0,
                        three_point_percentage=float(row['FG3_PCT']) if row['FG3_PCT'] else 0.0,
                        free_throw_percentage=float(row['FT_PCT']) if row['FT_PCT'] else 0.0,
                    ))
                    seasons_added += 1

                updated += 1
                logger.info(f"✓ [{i}/{len(players)}] Added {len(season_df)} seasons for {player.full_name}")

                if i % 5 == 0:
                    db.session.commit()

            except Exception as e:
                failed += 1
                logger.error(f"✗ [{i}/{len(players)}] Error processing {player.full_name}: {e}")

        db.session.commit()
        logger.info(f"Done. Updated: {updated}, seasons added: {seasons_added}, failed: {failed}")


if __name__ == '__main__':
    populate_season_stats()
