#!/usr/bin/env python3
"""Test script to check awards API data structure"""

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
            print(f"\nColumns in awards DataFrame:")
            print(awards_df.columns.tolist())

            print(f"\nAll-NBA awards detail:")
            all_nba_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA', case=False, na=False)]
            if not all_nba_df.empty:
                print(all_nba_df[['DESCRIPTION', 'TYPE', 'TEAM', 'SEASON']].to_string())

            print(f"\nAll-Defensive awards detail:")
            all_def_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-Defensive', case=False, na=False)]
            if not all_def_df.empty:
                print(all_def_df[['DESCRIPTION', 'TYPE', 'TEAM', 'SEASON']].head(10).to_string())
        else:
            print("No awards data found!")
