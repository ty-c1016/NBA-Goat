#!/usr/bin/env python3
"""Script to populate Finals MVP data for notable players.

Finals MVP award was introduced in 1969. This script adds FMVP counts
for players who won the award.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, Achievement

# Finals MVP data (player name: number of FMVPs)
FINALS_MVP_DATA = {
    'Michael Jordan': 6,
    'LeBron James': 4,
    'Magic Johnson': 3,
    'Shaquille O\'Neal': 3,
    'Tim Duncan': 3,
    'Kobe Bryant': 2,
    'Kawhi Leonard': 2,
    'Kevin Durant': 2,
    'Hakeem Olajuwon': 2,
    'Willis Reed': 2,
    'Kareem Abdul-Jabbar': 2,
    'Larry Bird': 2,
    'Stephen Curry': 1,
    'Dirk Nowitzki': 1,
    'Dwyane Wade': 1,
    'Tony Parker': 1,
    'Chauncey Billups': 1,
    'Paul Pierce': 1,
    'Isiah Thomas': 1,
    'Joe Dumars': 1,
    'James Worthy': 1,
    'Moses Malone': 1,
    'Wes Unseld': 1,
    'Jerry West': 1,
    'John Havlicek': 1,
    'Rick Barry': 1,
    'Giannis Antetokounmpo': 1,
    'Nikola Jokic': 1,
    'Cedric Maxwell': 1,
    'Dennis Johnson': 1,
}

def update_finals_mvps():
    """Update Finals MVP awards for players"""
    app = create_app()

    with app.app_context():
        updated_count = 0
        not_found = []

        for player_name, fmvp_count in FINALS_MVP_DATA.items():
            # Find player
            player = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()

            if player and player.achievements:
                player.achievements.finals_mvp_awards = fmvp_count
                updated_count += 1
                print(f'✓ Updated {player.full_name}: {fmvp_count} Finals MVPs')
            else:
                not_found.append(player_name)
                print(f'✗ Player not found: {player_name}')

        db.session.commit()

        print(f'\n--- Summary ---')
        print(f'Updated: {updated_count} players')
        print(f'Not found: {len(not_found)} players')

        if not_found:
            print(f'\nNot found: {", ".join(not_found)}')

if __name__ == '__main__':
    update_finals_mvps()
