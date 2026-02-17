#!/usr/bin/env python3
"""Test script to check data type of ALL_NBA_TEAM_NUMBER"""

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
            all_nba_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA', case=False, na=False)]
            if not all_nba_df.empty:
                print(f"Data type of ALL_NBA_TEAM_NUMBER: {all_nba_df['ALL_NBA_TEAM_NUMBER'].dtype}")
                print(f"Sample values: {all_nba_df['ALL_NBA_TEAM_NUMBER'].head().tolist()}")
                print(f"Unique values: {sorted(all_nba_df['ALL_NBA_TEAM_NUMBER'].unique().tolist())}")

                # Try different comparison methods
                print(f"\nTrying comparison with ==1: {len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == 1])}")
                print(f"Trying comparison with =='1': {len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == '1'])}")
                print(f"Trying comparison with ==1.0: {len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == 1.0])}")

                # Check for NaN or None
                print(f"\nNull values: {all_nba_df['ALL_NBA_TEAM_NUMBER'].isna().sum()}")
        else:
            print("No awards data found!")
