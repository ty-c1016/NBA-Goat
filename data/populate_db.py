#!/usr/bin/env python3
"""Populate the database with player data.

Usage:
    python data/populate_db.py --mode sample   # quick test data
    python data/populate_db.py --mode api      # real NBA API data
"""

import sys
import os
import logging
import math
import argparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, CareerStats, AdvancedStats, Achievement
from data.nba_fetcher import NBADataFetcher, get_sample_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def populate_sample_data():
    app = create_app()
    with app.app_context():
        db.create_all()

        db.session.query(Achievement).delete()
        db.session.query(AdvancedStats).delete()
        db.session.query(CareerStats).delete()
        db.session.query(Player).delete()
        db.session.commit()

        for player_data in get_sample_data():
            try:
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
                db.session.flush()

                cs = player_data['career_stats']
                db.session.add(CareerStats(
                    player_id=player.id,
                    games_played=cs['games_played'],
                    points_per_game=cs['points_per_game'],
                    rebounds_per_game=cs['rebounds_per_game'],
                    assists_per_game=cs['assists_per_game'],
                    field_goal_percentage=cs['field_goal_percentage'],
                    total_points=cs['total_points']
                ))

                ach = player_data['achievements']
                db.session.add(Achievement(
                    player_id=player.id,
                    championships=ach.get('championships', 0),
                    mvp_awards=ach.get('mvp_awards', 0),
                    finals_mvp_awards=ach.get('finals_mvp_awards', 0),
                    all_star_selections=ach.get('all_star_selections', 0),
                    all_nba_first_team=ach.get('all_nba_first_team', 0),
                    hall_of_fame=ach.get('hall_of_fame', False)
                ))

                logger.info(f"Added {player.full_name}")
            except Exception as e:
                logger.error(f"Error adding {player_data['full_name']}: {e}")
                db.session.rollback()

        db.session.commit()
        logger.info(f"Done. Total players: {Player.query.count()}")


def populate_from_api(min_games=400, min_seasons=10, min_ppg=10.0):
    app = create_app()
    fetcher = NBADataFetcher()

    def to_python_type(value):
        if value is None:
            return 0
        try:
            if hasattr(value, 'dtype'):
                float_val = float(value)
                return 0 if math.isnan(float_val) else float_val
            return value or 0
        except (TypeError, ValueError):
            return 0

    with app.app_context():
        db.create_all()
        all_players = fetcher.get_all_players()
        logger.info(f"Found {len(all_players)} total players from NBA API")

        qualified_count = 0
        for i, player_data in enumerate(all_players):
            try:
                if (i + 1) % 100 == 0:
                    logger.info(f"Progress: {i+1}/{len(all_players)}, {qualified_count} qualified")

                if Player.query.filter_by(nba_id=player_data['id']).first():
                    continue

                player = Player(
                    nba_id=player_data['id'],
                    full_name=player_data['full_name'],
                    first_name=player_data.get('first_name', ''),
                    last_name=player_data.get('last_name', ''),
                    is_active=player_data.get('is_active', False)
                )
                db.session.add(player)
                db.session.flush()

                career_stats_df = fetcher.get_player_career_stats(player_data['id'])
                if career_stats_df is None or career_stats_df.empty:
                    continue

                num_seasons = len(career_stats_df)
                total_games = int(career_stats_df['GP'].sum())
                total_points = int(career_stats_df['PTS'].sum())
                career_ppg = total_points / total_games if total_games > 0 else 0

                if total_games < min_games or num_seasons < min_seasons or career_ppg < min_ppg:
                    continue

                logger.info(f"✓ {player_data['full_name']}: {num_seasons} seasons, {total_games} games, {career_ppg:.1f} PPG")
                qualified_count += 1

                total_rebounds = int(career_stats_df['REB'].sum())
                total_assists = int(career_stats_df['AST'].sum())
                total_steals = int(career_stats_df['STL'].sum() if 'STL' in career_stats_df.columns else 0)
                total_blocks = int(career_stats_df['BLK'].sum() if 'BLK' in career_stats_df.columns else 0)
                total_fgm = career_stats_df['FGM'].sum() if 'FGM' in career_stats_df.columns else 0
                total_fga = career_stats_df['FGA'].sum() if 'FGA' in career_stats_df.columns else 0
                total_fg3m = career_stats_df['FG3M'].sum() if 'FG3M' in career_stats_df.columns else 0
                total_fg3a = career_stats_df['FG3A'].sum() if 'FG3A' in career_stats_df.columns else 0
                total_ftm = career_stats_df['FTM'].sum() if 'FTM' in career_stats_df.columns else 0
                total_fta = career_stats_df['FTA'].sum() if 'FTA' in career_stats_df.columns else 0

                gp = max(total_games, 1)
                db.session.add(CareerStats(
                    player_id=player.id,
                    games_played=total_games,
                    points_per_game=to_python_type(total_points / gp),
                    rebounds_per_game=to_python_type(total_rebounds / gp),
                    assists_per_game=to_python_type(total_assists / gp),
                    steals_per_game=to_python_type(total_steals / gp),
                    blocks_per_game=to_python_type(total_blocks / gp),
                    field_goal_percentage=to_python_type(total_fgm / total_fga if total_fga > 0 else 0),
                    three_point_percentage=to_python_type(total_fg3m / total_fg3a if total_fg3a > 0 else 0),
                    free_throw_percentage=to_python_type(total_ftm / total_fta if total_fta > 0 else 0),
                    total_points=total_points,
                    total_rebounds=total_rebounds,
                    total_assists=total_assists
                ))

                awards_df = fetcher.get_player_awards(player_data['id'])
                championships = finals_appearances = mvp_awards = finals_mvp_awards = 0
                all_star_selections = all_nba_first = all_nba_second = all_nba_third = 0
                all_defensive_first = scoring_titles = 0

                if awards_df is not None and not awards_df.empty:
                    championships = len(awards_df[awards_df['DESCRIPTION'].str.contains('NBA Champion', case=False, na=False)])
                    finals_appearances = championships + len(awards_df[awards_df['DESCRIPTION'].str.contains('Finals|Runner-up', case=False, na=False)])
                    # Use exact award name to exclude Finals MVP, All-Star Game MVP, Playoff MVP, etc.
                    mvp_awards = len(awards_df[awards_df['DESCRIPTION'].str.contains(r'NBA Most Valuable Player Award$', case=False, na=False, regex=True)])
                    finals_mvp_awards = len(awards_df[awards_df['DESCRIPTION'].str.contains('Finals MVP|Finals Most Valuable', case=False, na=False)])
                    # Exclude All-Star Game MVP award rows; count only selection rows
                    all_star_selections = len(awards_df[
                        awards_df['DESCRIPTION'].str.contains('All-Star', case=False, na=False) &
                        ~awards_df['DESCRIPTION'].str.contains('Most Valuable|MVP', case=False, na=False)
                    ])
                    all_nba_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA', case=False, na=False)]
                    all_nba_first = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '1'])
                    all_nba_second = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '2'])
                    all_nba_third = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '3'])
                    all_defensive_first = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-Defensive', case=False, na=False)])
                    scoring_titles = len(awards_df[awards_df['DESCRIPTION'].str.contains('Scoring Champion|Scoring Title', case=False, na=False)])

                db.session.add(Achievement(
                    player_id=player.id,
                    championships=championships,
                    finals_appearances=finals_appearances,
                    mvp_awards=mvp_awards,
                    finals_mvp_awards=finals_mvp_awards,
                    all_star_selections=all_star_selections,
                    all_nba_first_team=all_nba_first,
                    all_nba_second_team=all_nba_second,
                    all_nba_third_team=all_nba_third,
                    all_defensive_first_team=all_defensive_first,
                    all_defensive_second_team=0,
                    scoring_titles=scoring_titles
                ))
                db.session.commit()

            except Exception as e:
                logger.error(f"Error processing {player_data.get('full_name', 'Unknown')}: {e}")
                db.session.rollback()

        logger.info(f"Done. {qualified_count} players added. Total in DB: {Player.query.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Populate NBA database')
    parser.add_argument('--mode', choices=['sample', 'api'], default='sample')
    args = parser.parse_args()

    if args.mode == 'sample':
        populate_sample_data()
    else:
        populate_from_api()
