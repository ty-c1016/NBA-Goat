#!/usr/bin/env python3
"""Add missing legendary players: James Harden, Bill Russell, Dirk Nowitzki, Shaquille O'Neal"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, CareerStats, Achievement
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo
import time

# Manual data for players (in case API doesn't have complete info)
PLAYER_DATA = {
    'James Harden': {
        'nba_id': 201935,
        'scoring_titles': 3,  # 2018, 2019, 2020
        'mvp_awards': 1,      # 2018
        'championships': 0,
        'finals_mvp': 0,
        'finals_appearances': 1,  # 2012
        'all_star': 10,
        'all_nba_1st': 6,
        'all_nba_2nd': 1,
        'all_nba_3rd': 3,
        'seasons_30ppg': 4,
        'dominant_championships': 0
    },
    'Bill Russell': {
        'nba_id': 77161,
        'scoring_titles': 0,
        'mvp_awards': 5,      # 1958, 1961-63, 1965
        'championships': 11,  # 1957, 1959-66, 1968-69
        'finals_mvp': 0,      # Award didn't exist in his era
        'finals_appearances': 12,
        'all_star': 12,
        'all_nba_1st': 3,
        'all_nba_2nd': 8,
        'all_nba_3rd': 0,
        'seasons_30ppg': 0,
        'dominant_championships': 8  # Was the clear leader on 8 of his 11 rings
    },
    'Dirk Nowitzki': {
        'nba_id': 1717,
        'scoring_titles': 0,
        'mvp_awards': 1,      # 2007
        'championships': 1,   # 2011
        'finals_mvp': 1,      # 2011
        'finals_appearances': 2,  # 2006, 2011
        'all_star': 14,
        'all_nba_1st': 4,
        'all_nba_2nd': 5,
        'all_nba_3rd': 3,
        'seasons_30ppg': 0,
        'dominant_championships': 1  # 2011 legendary run
    },
    'Shaquille O\'Neal': {
        'nba_id': 406,
        'scoring_titles': 2,  # 1995, 2000
        'mvp_awards': 1,      # 2000
        'championships': 4,   # 2000-02 (Lakers), 2006 (Heat)
        'finals_mvp': 3,      # 2000-02
        'finals_appearances': 6,  # 1995, 2000-02, 2004, 2006
        'all_star': 15,
        'all_nba_1st': 8,
        'all_nba_2nd': 2,
        'all_nba_3rd': 4,
        'seasons_30ppg': 1,
        'dominant_championships': 3  # 2000-02 Lakers threepeat
    }
}

def add_missing_legends():
    """Add missing legendary players to database"""
    app = create_app()

    with app.app_context():
        for player_name, data in PLAYER_DATA.items():
            try:
                # Check if player already exists
                existing = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()
                if existing:
                    print(f'✓ {player_name} already exists (ID: {existing.id})')

                    # Update achievements if missing
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
                        print(f'  Updated achievements for {player_name}')
                    continue

                print(f'Adding {player_name}...')

                # Fetch from NBA API
                time.sleep(0.6)
                player_id = data['nba_id']

                # Get player info
                info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                info_df = info.get_data_frames()[0]

                if len(info_df) == 0:
                    print(f'✗ Could not fetch info for {player_name}')
                    continue

                info_row = info_df.iloc[0]

                # Get career stats
                career = playercareerstats.PlayerCareerStats(player_id=player_id, per_mode36='PerGame')
                career_totals = career.get_data_frames()[1]  # Career totals

                if len(career_totals) == 0:
                    print(f'✗ Could not fetch career stats for {player_name}')
                    continue

                totals = career_totals.iloc[0]

                # Create Player
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

                # Create CareerStats
                career_stats = CareerStats(
                    player_id=player.id,
                    games_played=int(totals['GP']) if totals['GP'] else 0,
                    points_per_game=float(totals['PTS']) if totals['PTS'] else 0.0,
                    rebounds_per_game=float(totals['REB']) if totals['REB'] else 0.0,
                    assists_per_game=float(totals['AST']) if totals['AST'] else 0.0,
                    steals_per_game=float(totals['STL']) if totals['STL'] else 0.0,
                    blocks_per_game=float(totals['BLK']) if totals['BLK'] else 0.0,
                    field_goal_percentage=float(totals['FG_PCT']) if totals['FG_PCT'] else 0.0,
                    total_points=int(float(totals['PTS']) * int(totals['GP'])) if totals['PTS'] and totals['GP'] else 0
                )
                db.session.add(career_stats)

                # Create Achievements
                achievements = Achievement(
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
                )
                db.session.add(achievements)

                print(f'✓ Added {player.full_name}')

            except Exception as e:
                print(f'✗ Error adding {player_name}: {e}')
                db.session.rollback()
                continue

        db.session.commit()
        print('\n✓ Done!')

if __name__ == '__main__':
    import pandas as pd
    add_missing_legends()
