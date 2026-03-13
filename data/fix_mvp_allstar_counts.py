"""Fix inflated MVP and All-Star counts caused by overly broad award-description matching.

The original populate_db.py used str.contains('Most Valuable Player') which captured
Finals MVP, All-Star Game MVP, Playoff MVP, etc. on top of regular-season MVPs.
Similarly str.contains('All-Star') over-counted All-Star Game MVPs.

This script sets the correct values for every player in the database.
Sources: Basketball Reference career pages.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, Player, Achievement

# fmt: (regular_season_mvps, all_star_selections)
# All-Star counts = number of All-Star Game *selections* (not appearances — some selected didn't play due to injury)
CORRECT = {
    # ── Legends / Hall of Famers ──────────────────────────────────────────────
    'Kareem Abdul-Jabbar':   (6,  19),
    'Michael Jordan':        (5,  14),
    'LeBron James':          (4,  20),
    'Magic Johnson':         (3,  12),
    'Larry Bird':            (3,  12),
    'Moses Malone':          (3,  12),
    'Wilt Chamberlain':      (4,  13),
    'Bill Russell':          (5,  12),
    'Tim Duncan':            (2,  15),
    'Shaquille O\'Neal':     (1,  15),
    'Hakeem Olajuwon':       (1,  12),
    'Charles Barkley':       (1,  11),
    'Julius Erving':         (1,  11),  # NBA only (3 ABA MVPs not counted here)
    'Bob Cousy':             (1,  13),
    'Allen Iverson':         (1,  11),
    'Oscar Robertson':       (1,  12),
    'Elgin Baylor':          (0,  11),
    'John Havlicek':         (0,  13),
    'Jerry West':            (0,  14),
    'Isiah Thomas':          (0,  12),
    'Patrick Ewing':         (0,  11),
    'Clyde Drexler':         (0,  10),
    'Rick Barry':            (1,   8),  # NBA only
    'Dave Cowens':           (2,   8),  # 1 regular season + 1 co-MVP
    'Nate Archibald':        (1,   6),
    'Bob Lanier':            (0,   8),
    'Dave Bing':             (0,   7),
    'Walt Frazier':          (0,   7),
    'George Gervin':         (0,   9),
    'Hal Greer':             (0,  10),
    'Paul Arizin':           (0,  10),
    'Elton Brand':           (0,   2),

    # ── Modern stars ─────────────────────────────────────────────────────────
    'Kevin Durant':          (1,  14),
    'Stephen Curry':         (2,  10),
    'Kobe Bryant':           (1,  18),
    'Kevin Garnett':         (1,  15),
    'Dirk Nowitzki':         (1,  14),
    'Dwyane Wade':           (0,  13),
    'Chris Paul':            (0,  12),
    'Carmelo Anthony':       (0,  10),
    'Giannis Antetokounmpo': (2,  10),
    'Nikola Jokic':          (3,   7),
    'Joel Embiid':           (1,   7),
    'James Harden':          (1,  10),
    'Kevin Durant':          (1,  14),
    'Kawhi Leonard':         (0,   6),  # 2 Finals MVPs, 0 regular season
    'Kyrie Irving':          (0,   8),
    'Russell Westbrook':     (1,   9),
    'Paul George':           (0,   9),
    'Anthony Davis':         (0,   8),
    'Jimmy Butler':          (0,   6),
    'Luka Doncic':           (0,   5),
    'Devin Booker':          (0,   3),
    'Shai Gilgeous-Alexander': (1,  3),
    'DeMar DeRozan':         (0,   6),
    'Jayson Tatum':          (0,   5),
    'Jaylen Brown':          (0,   2),
    'Ray Allen':             (0,  10),
    'Grant Hill':            (0,   7),
    'Vince Carter':          (0,   8),
    'Tracy McGrady':         (0,   7),
    'Kevin Johnson':         (0,   3),
    'Chauncey Billups':      (1,   5),
    'Joe Dumars':            (0,   6),
    'Manu Ginobili':         (0,   2),
    'Tony Parker':           (0,   6),
    'Pau Gasol':             (0,   6),
    'Chris Bosh':            (0,  11),
    'Dwight Howard':         (0,   8),
    'Blake Griffin':         (0,   6),
    'LaMarcus Aldridge':     (0,   7),
    'Andre Iguodala':        (0,   1),  # Finals MVP, but 0 regular season MVPs and 1 All-Star
    'Rudy Gobert':           (0,   3),
    'Bradley Beal':          (0,   3),
    'Zach LaVine':           (0,   2),
    'DeMarcus Cousins':      (0,   4),
    'Jrue Holiday':          (0,   1),

    # ── Classic role players / notable corrections ────────────────────────────
    'Tom Chambers':          (0,   4),
    'Larry Johnson':         (0,   2),
    'Dennis Johnson':        (0,   5),
    'Bob Dandridge':         (0,   4),
    'Bailey Howell':         (0,   6),
    'Bill Laimbeer':         (0,   2),
    'Bobby Jones':           (0,   0),
    'Gus Johnson':           (0,   4),
    'Harry Gallatin':        (0,   7),
    'Larry Foust':           (0,   8),
    'Rolando Blackman':      (0,   4),
    'Otis Birdsong':         (0,   4),
    'Maurice Cheeks':        (0,   4),
    'Bill Bridges':          (0,   2),
    'Mark Aguirre':          (0,   3),
    'Vin Baker':             (0,   4),
    'Joe Johnson':           (0,   7),
    'Marques Johnson':       (0,   5),
    'Walter Davis':          (0,   6),
    'Paul George':           (0,   9),
}


def fix_counts():
    fixed = 0
    not_found = []

    with app.app_context():
        for name, (mvp, allstar) in CORRECT.items():
            player = db.session.query(Player).filter(Player.full_name == name).first()
            if not player:
                not_found.append(name)
                continue
            ach = player.achievements
            if not ach:
                not_found.append(f'{name} (no achievements row)')
                continue

            changed = False
            if ach.mvp_awards != mvp:
                print(f'  {name}: MVPs {ach.mvp_awards} -> {mvp}')
                ach.mvp_awards = mvp
                changed = True
            if ach.all_star_selections != allstar:
                print(f'  {name}: All-Stars {ach.all_star_selections} -> {allstar}')
                ach.all_star_selections = allstar
                changed = True
            if changed:
                fixed += 1

        db.session.commit()

    print(f'\nFixed {fixed} players.')
    if not_found:
        print('Not found in DB:', not_found)


if __name__ == '__main__':
    fix_counts()
