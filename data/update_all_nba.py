#!/usr/bin/env python3
"""Update All-NBA, All-Defensive, and scoring title data for all players."""

import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, Achievement
from data.nba_fetcher import NBADataFetcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_all_nba_data():
    app = create_app()
    fetcher = NBADataFetcher()

    with app.app_context():
        players = Player.query.join(Achievement).all()
        updated = 0

        for i, player in enumerate(players):
            if (i + 1) % 50 == 0:
                logger.info(f"Progress: {i+1}/{len(players)}")

            try:
                awards_df = fetcher.get_player_awards(player.nba_id)
                if awards_df is None or awards_df.empty:
                    continue

                all_nba_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA', case=False, na=False)]
                all_nba_first = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '1'])
                all_nba_second = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '2'])
                all_nba_third = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '3'])
                all_defensive_first = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-Defensive', case=False, na=False)])
                scoring_titles = len(awards_df[awards_df['DESCRIPTION'].str.contains('Scoring Champion|Scoring Title', case=False, na=False)])

                total = all_nba_first + all_nba_second + all_nba_third + all_defensive_first + scoring_titles
                if total > 0:
                    player.achievements.all_nba_first_team = all_nba_first
                    player.achievements.all_nba_second_team = all_nba_second
                    player.achievements.all_nba_third_team = all_nba_third
                    player.achievements.all_defensive_first_team = all_defensive_first
                    player.achievements.all_defensive_second_team = 0
                    player.achievements.scoring_titles = scoring_titles
                    db.session.commit()
                    updated += 1
                    logger.info(f"✓ {player.full_name}: {all_nba_first}/{all_nba_second}/{all_nba_third} All-NBA, {scoring_titles} scoring titles")

            except Exception as e:
                logger.error(f"Error updating {player.full_name}: {e}")
                db.session.rollback()

        logger.info(f"Done. Updated {updated}/{len(players)} players.")


if __name__ == "__main__":
    update_all_nba_data()
