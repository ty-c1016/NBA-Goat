#!/usr/bin/env python3
"""Script to populate scoring titles for notable players.

Based on NBA historical scoring leaders.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player

# Scoring titles data (player name: number of scoring titles)
SCORING_TITLES = {
    # Modern era (1946-present)
    'Michael Jordan': 10,     # 1987-88, 1989-93, 1996-98
    'Wilt Chamberlain': 7,    # 1960-66
    'George Gervin': 4,       # 1978-80, 1982
    'Allen Iverson': 4,       # 1999, 2001, 2002, 2005
    'Kevin Durant': 4,        # 2010-12, 2014
    'Kobe Bryant': 2,         # 2006, 2007
    'George Mikan': 3,        # 1949-51
    'Bob McAdoo': 3,          # 1974-76
    'Tracy McGrady': 2,       # 2003, 2004
    'Shaquille O\'Neal': 2,   # 1995, 2000
    'LeBron James': 1,        # 2008
    'Kareem Abdul-Jabbar': 2, # 1971, 1972
    'Bob Pettit': 2,          # 1956, 1959
    'Neil Johnston': 3,       # 1953-55
    'Paul Arizin': 2,         # 1952, 1957
    'Tiny Archibald': 1,      # 1973
    'Rick Barry': 1,          # 1967
    'Elgin Baylor': 0,        # Never won (peaked 2nd multiple times)
    'Dave Bing': 1,           # 1968
    'Larry Bird': 0,          # Never won
    'Adrian Dantley': 2,      # 1981, 1984
    'Alex English': 1,        # 1983
    'Bernard King': 1,        # 1985
    'Bob Lanier': 0,
    'Moses Malone': 1,        # 1979
    'Pete Maravich': 1,       # 1977
    'Dominique Wilkins': 1,   # 1986
    'James Harden': 3,        # 2018-20
    'Russell Westbrook': 2,   # 2015, 2017
    'Stephen Curry': 2,       # 2016, 2021
    'Carmelo Anthony': 1,     # 2013
    'Dwyane Wade': 1,         # 2009
    'Joel Embiid': 2,         # 2022, 2023
    'Luka Doncic': 1,         # 2024
    'Damian Lillard': 0,
    'Giannis Antetokounmpo': 0,
}

def update_scoring_titles():
    """Update scoring titles for players"""
    app = create_app()

    with app.app_context():
        updated_count = 0
        not_found = []

        for player_name, titles in SCORING_TITLES.items():
            # Find player
            player = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()

            if player and player.achievements:
                player.achievements.scoring_titles = titles
                updated_count += 1
                if titles > 0:
                    print(f'✓ Updated {player.full_name}: {titles} scoring titles')
                else:
                    print(f'○ Set {player.full_name}: 0 scoring titles')
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
    update_scoring_titles()
