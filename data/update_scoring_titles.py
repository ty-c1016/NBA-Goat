#!/usr/bin/env python3
"""Update scoring titles for players."""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player

SCORING_TITLES = {
    'Michael Jordan': 10,
    'Wilt Chamberlain': 7,
    'George Gervin': 4,
    'Allen Iverson': 4,
    'Kevin Durant': 4,
    'James Harden': 3,
    'Bob McAdoo': 3,
    'Neil Johnston': 3,
    'George Mikan': 3,
    'Kobe Bryant': 2,
    'Tracy McGrady': 2,
    "Shaquille O'Neal": 2,
    'Kareem Abdul-Jabbar': 2,
    'Bob Pettit': 2,
    'Paul Arizin': 2,
    'Adrian Dantley': 2,
    'Russell Westbrook': 2,
    'Stephen Curry': 2,
    'Joel Embiid': 2,
    'LeBron James': 1,
    'Tiny Archibald': 1,
    'Rick Barry': 1,
    'Dave Bing': 1,
    'Alex English': 1,
    'Bernard King': 1,
    'Moses Malone': 1,
    'Pete Maravich': 1,
    'Dominique Wilkins': 1,
    'Oscar Robertson': 1,
    'Jerry West': 1,
    'Carmelo Anthony': 1,
    'Dwyane Wade': 1,
    'Luka Doncic': 1,
    'Elgin Baylor': 0,
    'Larry Bird': 0,
    'Bob Lanier': 0,
    'Damian Lillard': 0,
    'Giannis Antetokounmpo': 0,
}


def update_scoring_titles():
    app = create_app()
    with app.app_context():
        updated = []
        not_found = []

        for player_name, titles in SCORING_TITLES.items():
            player = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()
            if player and player.achievements:
                player.achievements.scoring_titles = titles
                updated.append(player_name)
                print(f'{"✓" if titles > 0 else "○"} {player.full_name}: {titles} scoring titles')
            else:
                not_found.append(player_name)
                print(f'✗ Not found: {player_name}')

        db.session.commit()
        print(f'\nUpdated: {len(updated)}, not found: {len(not_found)}')
        if not_found:
            print(f'Not found: {", ".join(not_found)}')


if __name__ == '__main__':
    update_scoring_titles()
