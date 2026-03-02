#!/usr/bin/env python3
"""Update dominant championships count for players."""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player

DOMINANT_CHAMPIONSHIPS = {
    'Michael Jordan': 6,
    'LeBron James': 4,
    'Stephen Curry': 3,
    'Kevin Durant': 2,
    'Kobe Bryant': 5,
    "Shaquille O'Neal": 3,
    'Tim Duncan': 5,
    'Hakeem Olajuwon': 2,
    'Dirk Nowitzki': 1,
    'Dwyane Wade': 2,
    'Kawhi Leonard': 2,
    'Giannis Antetokounmpo': 1,
    'Magic Johnson': 5,
    'Larry Bird': 3,
    'Kareem Abdul-Jabbar': 4,
    'Isiah Thomas': 2,
    'Clyde Drexler': 1,
    'Julius Erving': 1,
    'Moses Malone': 1,
    'Rick Barry': 1,
    'Wilt Chamberlain': 2,
    'Bill Russell': 8,
    'Jerry West': 1,
    'Oscar Robertson': 1,
    'Wes Unseld': 1,
    'Willis Reed': 2,
    'Dennis Rodman': 5,
    'Ben Wallace': 1,
    'Scottie Pippen': 6,
    'Draymond Green': 4,
    'Kevin Garnett': 1,
    'Paul Pierce': 1,
    'Ray Allen': 2,
    'Pau Gasol': 2,
    'Tony Parker': 3,
    'Chauncey Billups': 1,
    'Joe Dumars': 2,
    'James Worthy': 3,
    'Dennis Johnson': 3,
    'John Havlicek': 8,
    'Dave Cowens': 2,
    'Nikola Jokic': 1,
}


def update_dominant_championships():
    app = create_app()
    with app.app_context():
        updated = []
        not_found = []

        for player_name, dominant_count in DOMINANT_CHAMPIONSHIPS.items():
            player = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()
            if player and player.achievements:
                player.achievements.dominant_championships = dominant_count
                updated.append(player_name)
                print(f'✓ {player.full_name}: {dominant_count} dominant championships')
            else:
                not_found.append(player_name)
                print(f'✗ Not found: {player_name}')

        db.session.commit()
        print(f'\nUpdated: {len(updated)}, not found: {len(not_found)}')
        if not_found:
            print(f'Not found: {", ".join(not_found)}')


if __name__ == '__main__':
    update_dominant_championships()
