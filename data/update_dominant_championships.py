#!/usr/bin/env python3
"""Script to populate dominant championships data.

Marks championships where a player was clearly dominant (25+ PPG in playoffs/Finals
or equivalent impact for non-scorers like Dennis Rodman, Ben Wallace).
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Player, Achievement

# Dominant championships data
# Format: player name -> number of championships where they were dominant
# Based on playoff/Finals PPG 25+, or equivalent defensive/rebounding dominance
DOMINANT_CHAMPIONSHIPS = {
    # Modern era stars
    'Michael Jordan': 6,          # All 6 rings (28-41 PPG in Finals)
    'LeBron James': 4,            # All 4 rings (28-36 PPG in Finals)
    'Stephen Curry': 3,           # 2015, 2017, 2022 (2018 he deferred to KD)
    'Kevin Durant': 2,            # Both Warriors rings (dominant)
    'Kobe Bryant': 5,             # All 5 rings (dominant in all)
    'Shaquille O\'Neal': 3,       # All 3 Lakers rings (dominant)
    'Tim Duncan': 5,              # All 5 Spurs rings
    'Hakeem Olajuwon': 2,         # Both Rockets rings
    'Dirk Nowitzki': 1,           # 2011 run
    'Dwyane Wade': 2,             # 2006 (clearly dominant), 2012-2013 (shared with LeBron but still dominant)
    'Kawhi Leonard': 2,           # 2014, 2019 (both dominant)
    'Giannis Antetokounmpo': 1,   # 2021 (50-point Finals closeout game)

    # 80s-90s stars
    'Magic Johnson': 5,           # All 5 Lakers rings
    'Larry Bird': 3,              # All 3 Celtics rings
    'Kareem Abdul-Jabbar': 4,     # 1971, 1980, 1985, 1987 (not 1982, 1988 - older role)
    'Isiah Thomas': 2,            # Both Pistons rings
    'Clyde Drexler': 1,           # 1995 with Rockets (supporting, not lead)

    # 70s stars
    'Julius Erving': 1,           # 1983 76ers
    'Moses Malone': 1,            # 1983 76ers
    'Rick Barry': 1,              # 1975 Warriors
    'Wilt Chamberlain': 2,        # Both rings (1967, 1972)

    # 60s stars (pre-FMVP era - marking dominant ones)
    'Bill Russell': 8,            # Was clearly the leader on 8+ of his 11 rings
    'Jerry West': 1,              # 1972 (only ring)
    'Oscar Robertson': 1,         # 1971 Bucks
    'Wes Unseld': 1,              # 1978 Bullets
    'Willis Reed': 2,             # Both Knicks rings

    # Role player championships (defensive specialists who were critical)
    'Dennis Rodman': 5,           # All 5 rings (defensive dominance)
    'Ben Wallace': 1,             # 2004 Pistons (DPOY, anchor)
    'Scottie Pippen': 6,          # All 6 Bulls rings
    'Draymond Green': 4,          # All 4 Warriors rings (defensive anchor)

    # Supporting stars (some rings dominant, some not)
    'Kevin Garnett': 1,           # 2008 (defensive dominance)
    'Paul Pierce': 1,             # 2008
    'Ray Allen': 2,               # 2008, 2013
    'Pau Gasol': 2,               # Both Lakers rings
    'Tony Parker': 3,             # 2003, 2005, 2007 (not 2014)
    'Chauncey Billups': 1,        # 2004 Pistons
    'Joe Dumars': 2,              # Both Pistons rings
    'James Worthy': 3,            # All 3 Lakers rings
    'Dennis Johnson': 3,          # All 3 rings
    'John Havlicek': 8,           # Dominant on most of his rings
    'Dave Cowens': 2,             # Both Celtics rings
    'Nikola Jokic': 1,            # 2023 (31 PPG in playoffs)
}

def update_dominant_championships():
    """Update dominant championships for players"""
    app = create_app()

    with app.app_context():
        updated_count = 0
        not_found = []

        for player_name, dominant_count in DOMINANT_CHAMPIONSHIPS.items():
            # Find player
            player = Player.query.filter(Player.full_name.like(f'%{player_name}%')).first()

            if player and player.achievements:
                player.achievements.dominant_championships = dominant_count
                updated_count += 1
                print(f'✓ Updated {player.full_name}: {dominant_count} dominant championships')
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
    update_dominant_championships()
