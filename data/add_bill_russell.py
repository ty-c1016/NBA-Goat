#!/usr/bin/env python3
"""Manually add Bill Russell with his legendary stats"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, CareerStats, Achievement

def add_bill_russell():
    """Add Bill Russell manually"""
    app = create_app()

    with app.app_context():
        # Check if already exists
        existing = Player.query.filter(Player.full_name.like('%Bill Russell%')).first()
        if existing:
            print(f'Bill Russell already exists (ID: {existing.id})')
            return

        # Create Player
        player = Player(
            nba_id=77161,  # Bill Russell's NBA ID
            full_name='Bill Russell',
            first_name='Bill',
            last_name='Russell',
            position='Center',
            height='6-10',
            weight=215,
            from_year=1956,
            to_year=1969,
            is_active=False
        )
        db.session.add(player)
        db.session.flush()

        # Create CareerStats (Bill Russell's actual career stats)
        career_stats = CareerStats(
            player_id=player.id,
            games_played=963,
            points_per_game=15.1,
            rebounds_per_game=22.5,  # Most rebounds per game in NBA history
            assists_per_game=4.3,
            steals_per_game=0.0,  # Not tracked in his era
            blocks_per_game=0.0,  # Not tracked in his era
            field_goal_percentage=0.440,
            total_points=14522
        )
        db.session.add(career_stats)

        # Create Achievements
        achievements = Achievement(
            player_id=player.id,
            scoring_titles=0,
            mvp_awards=5,  # 1958, 1961, 1962, 1963, 1965
            championships=11,  # Most in NBA history
            finals_mvp_awards=0,  # Award didn't exist yet
            finals_appearances=12,
            all_star_selections=12,
            all_nba_first_team=3,
            all_nba_second_team=8,
            all_nba_third_team=0,
            seasons_30ppg=0,
            dominant_championships=8,  # Was the clear leader on 8 of his 11
            hall_of_fame=True,
            hall_of_fame_year=1975
        )
        db.session.add(achievements)

        db.session.commit()
        print(f'✓ Added {player.full_name}')
        print(f'  11 Championships')
        print(f'  5 MVP Awards')
        print(f'  22.5 RPG (all-time record)')

if __name__ == '__main__':
    add_bill_russell()
