#!/usr/bin/env python3
"""Test script to check awards API data"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.nba_fetcher import NBADataFetcher
from app import create_app
from models import Player

app = create_app()
fetcher = NBADataFetcher()

# Test with LeBron James (ID: 2544)
with app.app_context():
    lebron = Player.query.filter_by(full_name='LeBron James').first()
    if lebron:
        print(f"Testing awards for {lebron.full_name} (ID: {lebron.nba_id})")
        awards_df = fetcher.get_player_awards(lebron.nba_id)

        if awards_df is not None and not awards_df.empty:
            print(f"\nFound {len(awards_df)} awards")
            print("\nAll awards descriptions:")
            for desc in awards_df['DESCRIPTION'].values:
                print(f"  - {desc}")

            # Test our search patterns
            print("\n" + "="*60)
            print("Testing All-NBA patterns:")
            all_nba_first = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA First Team', case=False, na=False)])
            all_nba_second = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA Second Team', case=False, na=False)])
            all_nba_third = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA Third Team', case=False, na=False)])

            print(f"All-NBA First Team: {all_nba_first}")
            print(f"All-NBA Second Team: {all_nba_second}")
            print(f"All-NBA Third Team: {all_nba_third}")
        else:
            print("No awards data found!")
    else:
        print("LeBron James not found in database")
        print("\nTrying with Michael Jordan...")
        mj = Player.query.filter_by(full_name='Michael Jordan').first()
        if mj:
            print(f"Testing awards for {mj.full_name} (ID: {mj.nba_id})")
            awards_df = fetcher.get_player_awards(mj.nba_id)

            if awards_df is not None and not awards_df.empty:
                print(f"\nFound {len(awards_df)} awards")
                print("\nFirst 10 awards descriptions:")
                for desc in awards_df['DESCRIPTION'].values[:10]:
                    print(f"  - {desc}")
            else:
                print("No awards data found!")
