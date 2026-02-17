#!/usr/bin/env python3
"""Test script to check ALL_NBA_TEAM_NUMBER column"""

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
            print(f"\nAll-NBA awards with team numbers:")
            all_nba_df = awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA', case=False, na=False)]
            if not all_nba_df.empty:
                print(all_nba_df[['DESCRIPTION', 'ALL_NBA_TEAM_NUMBER', 'SEASON']].to_string())

                # Count by team
                all_nba_first = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == 1])
                all_nba_second = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == 2])
                all_nba_third = len(all_nba_df[all_nba_df['ALL_NBA_TEAM_NUMBER'] == 3])

                print(f"\nAll-NBA First Team: {all_nba_first}")
                print(f"All-NBA Second Team: {all_nba_second}")
                print(f"All-NBA Third Team: {all_nba_third}")
                print(f"Total All-NBA selections: {len(all_nba_df)}")
        else:
            print("No awards data found!")
