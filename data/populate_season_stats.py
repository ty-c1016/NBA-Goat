#!/usr/bin/env python3
"""Script to populate season-by-season stats for all players.

Fetches detailed season stats from NBA API to enable longevity scoring
based on PPG thresholds.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, SeasonStats
from nba_api.stats.endpoints import playercareerstats
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def populate_season_stats():
    """Fetch and populate season stats for all players"""
    app = create_app()

    with app.app_context():
        players = Player.query.all()

        updated_count = 0
        failed_count = 0
        seasons_added = 0

        logger.info(f"Found {len(players)} players to process")

        for i, player in enumerate(players, 1):
            try:
                # Check if player already has season stats
                existing = SeasonStats.query.filter_by(player_id=player.id).first()
                if existing:
                    logger.info(f"[{i}/{len(players)}] {player.full_name} already has season stats, skipping")
                    continue

                # Rate limiting - NBA API is sensitive
                time.sleep(0.6)

                # Fetch career stats (includes season-by-season)
                career = playercareerstats.PlayerCareerStats(
                    player_id=player.nba_id,
                    per_mode36='PerGame'
                )

                # Get season-by-season dataframe (index 0)
                season_df = career.get_data_frames()[0]

                if len(season_df) > 0:
                    player_seasons_added = 0

                    for _, row in season_df.iterrows():
                        # Create season stats record
                        season_stat = SeasonStats(
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
                        )
                        db.session.add(season_stat)
                        player_seasons_added += 1

                    updated_count += 1
                    seasons_added += player_seasons_added
                    logger.info(f"✓ [{i}/{len(players)}] Added {player_seasons_added} seasons for {player.full_name}")

                    # Commit every 5 players to avoid losing progress
                    if i % 5 == 0:
                        db.session.commit()
                        logger.info(f"--- Checkpoint: {i}/{len(players)} processed, {seasons_added} seasons added ---")
                else:
                    failed_count += 1
                    logger.warning(f"✗ [{i}/{len(players)}] No season data for {player.full_name}")

            except Exception as e:
                failed_count += 1
                logger.error(f"✗ [{i}/{len(players)}] Error processing {player.full_name}: {e}")
                continue

        # Final commit
        db.session.commit()

        logger.info(f"\n{'='*60}")
        logger.info(f"Season Stats Population Summary:")
        logger.info(f"  Players processed: {updated_count}")
        logger.info(f"  Total seasons added: {seasons_added}")
        logger.info(f"  Failed: {failed_count}")
        logger.info(f"  Total players: {len(players)}")
        logger.info(f"{'='*60}")

if __name__ == '__main__':
    populate_season_stats()
