"""We Adding Shai indivuidually cus he's Shai"""

from app import app, db
from models import Player, CareerStats, AdvancedStats, Achievement
from data.nba_fetcher import NBADataFetcher
import json
from datetime import datetime

def add_shai_gilgeous_alexander():
    """Fetch and add Shai Gilgeous-Alexander to the database"""

    with app.app_context():
        # Initialize the fetcher
        fetcher = NBADataFetcher()

        # First, get all players to find Shai's NBA ID
        print("Fetching all players from NBA API...")
        all_players = fetcher.get_all_players()

        # Find Shai Gilgeous-Alexander
        shai = None
        for player in all_players:
            if 'Gilgeous-Alexander' in player['full_name'] or \
               (player['first_name'] == 'Shai' and 'Alexander' in player['last_name']):
                shai = player
                break

        if not shai:
            print("Could not find Shai Gilgeous-Alexander in NBA API")
            return

        print(f"Found player: {shai['full_name']} (ID: {shai['id']})")

        # Check if player already exists
        existing_player = Player.query.filter_by(nba_id=shai['id']).first()
        if existing_player:
            print(f"Player already exists in database with ID {existing_player.id}")
            return

        # Get career stats
        print("Fetching career stats...")
        career_stats_df = fetcher.get_player_career_stats(shai['id'])

        if career_stats_df is None or career_stats_df.empty:
            print("No career stats found")
            return

        # Get awards
        print("Fetching awards...")
        awards_df = fetcher.get_player_awards(shai['id'])

        # Create Player record
        player = Player(
            nba_id=shai['id'],
            full_name=shai['full_name'],
            first_name=shai.get('first_name', 'Shai'),
            last_name=shai.get('last_name', 'Gilgeous-Alexander'),
            is_active=shai.get('is_active', True)
        )

        # Parse career stats from the dataframe
        # Sum up all seasons for career totals
        total_games = int(career_stats_df['GP'].sum())
        total_minutes = float(career_stats_df['MIN'].sum())
        total_points = int(career_stats_df['PTS'].sum())
        total_rebounds = int(career_stats_df['REB'].sum())
        total_assists = int(career_stats_df['AST'].sum())
        total_steals = int(career_stats_df['STL'].sum())
        total_blocks = int(career_stats_df['BLK'].sum())
        total_turnovers = int(career_stats_df['TOV'].sum())
        total_fgm = int(career_stats_df['FGM'].sum())
        total_fga = int(career_stats_df['FGA'].sum())
        total_fg3m = int(career_stats_df['FG3M'].sum())
        total_fg3a = int(career_stats_df['FG3A'].sum())
        total_ftm = int(career_stats_df['FTM'].sum())
        total_fta = int(career_stats_df['FTA'].sum())

        # Calculate per-game averages
        ppg = total_points / total_games if total_games > 0 else 0
        rpg = total_rebounds / total_games if total_games > 0 else 0
        apg = total_assists / total_games if total_games > 0 else 0
        spg = total_steals / total_games if total_games > 0 else 0
        bpg = total_blocks / total_games if total_games > 0 else 0
        tpg = total_turnovers / total_games if total_games > 0 else 0
        mpg = total_minutes / total_games if total_games > 0 else 0

        # Calculate shooting percentages
        fg_pct = total_fgm / total_fga if total_fga > 0 else 0
        fg3_pct = total_fg3m / total_fg3a if total_fg3a > 0 else 0
        ft_pct = total_ftm / total_fta if total_fta > 0 else 0

        # Get career years
        from_year = int(career_stats_df['SEASON_ID'].min().split('-')[0])
        to_year = int(career_stats_df['SEASON_ID'].max().split('-')[0])

        # Get teams (unique team abbreviations)
        teams = career_stats_df['TEAM_ABBREVIATION'].unique().tolist()
        player.teams = json.dumps(teams)
        player.from_year = from_year
        player.to_year = to_year

        # Add to session
        db.session.add(player)
        db.session.flush()  # Get the player ID

        # Create CareerStats
        career_stats = CareerStats(
            player_id=player.id,
            games_played=total_games,
            minutes_per_game=round(mpg, 1),
            points_per_game=round(ppg, 1),
            rebounds_per_game=round(rpg, 1),
            assists_per_game=round(apg, 1),
            steals_per_game=round(spg, 1),
            blocks_per_game=round(bpg, 1),
            turnovers_per_game=round(tpg, 1),
            field_goal_percentage=round(fg_pct, 3),
            three_point_percentage=round(fg3_pct, 3),
            free_throw_percentage=round(ft_pct, 3),
            field_goals_made=round(total_fgm / total_games, 1) if total_games > 0 else 0,
            field_goals_attempted=round(total_fga / total_games, 1) if total_games > 0 else 0,
            three_pointers_made=round(total_fg3m / total_games, 1) if total_games > 0 else 0,
            three_pointers_attempted=round(total_fg3a / total_games, 1) if total_games > 0 else 0,
            free_throws_made=round(total_ftm / total_games, 1) if total_games > 0 else 0,
            free_throws_attempted=round(total_fta / total_games, 1) if total_games > 0 else 0,
            total_points=total_points,
            total_rebounds=total_rebounds,
            total_assists=total_assists
        )
        db.session.add(career_stats)

        # Create AdvancedStats (placeholder values for now)
        advanced_stats = AdvancedStats(
            player_id=player.id
        )
        db.session.add(advanced_stats)

        # Process awards
        achievements = Achievement(player_id=player.id)

        if awards_df is not None and not awards_df.empty:
            # Count different types of awards
            all_star = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-Star', case=False, na=False)])
            all_nba_first = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA First Team', case=False, na=False)])
            all_nba_second = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA Second Team', case=False, na=False)])
            all_nba_third = len(awards_df[awards_df['DESCRIPTION'].str.contains('All-NBA Third Team', case=False, na=False)])
            roy = len(awards_df[awards_df['DESCRIPTION'].str.contains('Rookie', case=False, na=False)])

            achievements.all_star_selections = all_star
            achievements.all_nba_first_team = all_nba_first
            achievements.all_nba_second_team = all_nba_second
            achievements.all_nba_third_team = all_nba_third
            achievements.rookie_of_year = 1 if roy > 0 else 0

        db.session.add(achievements)

        # Commit all changes
        db.session.commit()

        print(f"\n✓ Successfully added {player.full_name} to the database!")
        print(f"  Player ID: {player.id}")
        print(f"  Career: {player.from_year}-{player.to_year}")
        print(f"  Teams: {player.teams}")
        print(f"  Games Played: {career_stats.games_played}")
        print(f"  PPG: {career_stats.points_per_game}")
        print(f"  RPG: {career_stats.rebounds_per_game}")
        print(f"  APG: {career_stats.assists_per_game}")
        print(f"  FG%: {career_stats.field_goal_percentage}")
        print(f"  All-Star Selections: {achievements.all_star_selections}")
        print(f"  All-NBA First Team: {achievements.all_nba_first_team}")

if __name__ == '__main__':
    add_shai_gilgeous_alexander()
