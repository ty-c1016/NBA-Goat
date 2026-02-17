#!/usr/bin/env python3
"""Fix Giannis's incorrect achievements data."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player

def fix_giannis():
    """Update Giannis with correct achievements"""
    app = create_app()

    with app.app_context():
        player = Player.query.filter(Player.full_name.like('%Giannis%')).first()

        if player and player.achievements:
            ach = player.achievements

            print(f'Before:')
            print(f'  MVP Awards: {ach.mvp_awards}')
            print(f'  Championships: {ach.championships}')
            print(f'  Finals MVPs: {ach.finals_mvp_awards}')
            print(f'  Finals Appearances: {ach.finals_appearances}')

            # Correct values
            ach.mvp_awards = 2  # 2019, 2020
            ach.championships = 1  # 2021
            ach.finals_mvp_awards = 1  # 2021
            ach.finals_appearances = 1  # 2021
            ach.dominant_championships = 1  # 2021 (50-point Finals closeout)

            db.session.commit()

            print(f'\nAfter:')
            print(f'  MVP Awards: {ach.mvp_awards}')
            print(f'  Championships: {ach.championships}')
            print(f'  Finals MVPs: {ach.finals_mvp_awards}')
            print(f'  Finals Appearances: {ach.finals_appearances}')
            print(f'  Dominant Championships: {ach.dominant_championships}')
            print('\n✓ Fixed!')
        else:
            print('Giannis not found')

if __name__ == '__main__':
    fix_giannis()
