#!/usr/bin/env python3
"""Add missing legendary players: Harden, Bill Russell, Dirk, Shaq."""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app import create_app
from models import db, Player, CareerStats, Achievement
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo

PLAYER_DATA = {
    'James Harden': {
        'nba_id': 201935,
        'scoring_titles': 3, 'mvp_awards': 1, 'championships': 0,
        'finals_mvp': 0, 'finals_appearances': 1, 'all_star': 10,
        'all_nba_1st': 6, 'all_nba_2nd': 1, 'all_nba_3rd': 3,
        'seasons_30ppg': 4, 'dominant_championships': 0
    },
    'Bill Russell': {
        'nba_id': 77161,
        'scoring_titles': 0, 'mvp_awards': 5, 'championships': 11,
        'finals_mvp': 0, 'finals_appearances': 12, 'all_star': 12,
        'all_nba_1st': 3, 'all_nba_2nd': 8, 'all_nba_3rd': 0,
        'seasons_30ppg': 0, 'dominant_championships': 8
    },
    'Dirk Nowitzki': {
        'nba_id': 1717,
        'scoring_titles': 0, 'mvp_awards': 1, 'championships': 1,
        'finals_mvp': 1, 'finals_appearances': 2, 'all_star': 14,
        'all_nba_1st': 4, 'all_nba_2nd': 5, 'all_nba_3rd': 3,
        'seasons_30ppg': 0, 'dominant_championships': 1
    },
    "Shaquille O'Neal": {
        'nba_id': 406,
        'scoring_titles': 2, 'mvp_awards': 1, 'championships': 4,
        'finals_mvp': 3, 'finals_appearances': 6, 'all_star': 15,
        'all_nba_1st': 8, 'all_nba_2nd': 2, 'all_nba_3rd': 4,
        'seasons_30ppg': 1, 'dominant_championships': 3
    }
}


def add_missing_legends():
    app = create_app()
    with app.app_context():
        for player_name, data in PLAYER_DATA.items():
            try:
                existing = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()
                if existing:
                    print(f'✓ {player_name} already exists, updating achievements...')
                    if existing.achievements:
                        ach = existing.achievements
                        ach.scoring_titles = data['scoring_titles']
                        ach.mvp_awards = data['mvp_awards']
                        ach.championships = data['championships']
                        ach.finals_mvp_awards = data['finals_mvp']
                        ach.finals_appearances = data['finals_appearances']
                        ach.all_star_selections = data['all_star']
                        ach.all_nba_first_team = data['all_nba_1st']
                        ach.all_nba_second_team = data['all_nba_2nd']
                        ach.all_nba_third_team = data['all_nba_3rd']
                        ach.seasons_30ppg = data['seasons_30ppg']
                        ach.dominant_championships = data['dominant_championships']
                    continue

                print(f'Adding {player_name}...')
                time.sleep(0.6)
                player_id = data['nba_id']

                info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                info_df = info.get_data_frames()[0]
                if len(info_df) == 0:
                    print(f'✗ Could not fetch info for {player_name}')
                    continue
                info_row = info_df.iloc[0]

                career = playercareerstats.PlayerCareerStats(player_id=player_id, per_mode36='PerGame')
                career_totals = career.get_data_frames()[1]
                if len(career_totals) == 0:
                    print(f'✗ Could not fetch career stats for {player_name}')
                    continue
                totals = career_totals.iloc[0]

                player = Player(
                    nba_id=player_id,
                    full_name=info_row['DISPLAY_FIRST_LAST'],
                    first_name=info_row['FIRST_NAME'],
                    last_name=info_row['LAST_NAME'],
                    position=info_row['POSITION'] if pd.notna(info_row['POSITION']) else None,
                    height=info_row['HEIGHT'] if pd.notna(info_row['HEIGHT']) else None,
                    weight=int(info_row['WEIGHT']) if pd.notna(info_row['WEIGHT']) and info_row['WEIGHT'] else None,
                    from_year=int(info_row['FROM_YEAR']) if pd.notna(info_row['FROM_YEAR']) else None,
                    to_year=int(info_row['TO_YEAR']) if pd.notna(info_row['TO_YEAR']) else None,
                    is_active=(info_row['ROSTERSTATUS'] == 1) if pd.notna(info_row['ROSTERSTATUS']) else False
                )
                db.session.add(player)
                db.session.flush()

                db.session.add(CareerStats(
                    player_id=player.id,
                    games_played=int(totals['GP']) if totals['GP'] else 0,
                    points_per_game=float(totals['PTS']) if totals['PTS'] else 0.0,
                    rebounds_per_game=float(totals['REB']) if totals['REB'] else 0.0,
                    assists_per_game=float(totals['AST']) if totals['AST'] else 0.0,
                    steals_per_game=float(totals['STL']) if totals['STL'] else 0.0,
                    blocks_per_game=float(totals['BLK']) if totals['BLK'] else 0.0,
                    field_goal_percentage=float(totals['FG_PCT']) if totals['FG_PCT'] else 0.0,
                    total_points=int(float(totals['PTS']) * int(totals['GP'])) if totals['PTS'] and totals['GP'] else 0
                ))

                db.session.add(Achievement(
                    player_id=player.id,
                    scoring_titles=data['scoring_titles'],
                    mvp_awards=data['mvp_awards'],
                    championships=data['championships'],
                    finals_mvp_awards=data['finals_mvp'],
                    finals_appearances=data['finals_appearances'],
                    all_star_selections=data['all_star'],
                    all_nba_first_team=data['all_nba_1st'],
                    all_nba_second_team=data['all_nba_2nd'],
                    all_nba_third_team=data['all_nba_3rd'],
                    seasons_30ppg=data['seasons_30ppg'],
                    dominant_championships=data['dominant_championships'],
                    hall_of_fame=True
                ))

                db.session.commit()
                print(f'✓ Added {player.full_name}')

            except Exception as e:
                print(f'✗ Error adding {player_name}: {e}')
                db.session.rollback()

        db.session.commit()
        print('\n✓ Done!')


if __name__ == '__main__':
    add_missing_legends()
