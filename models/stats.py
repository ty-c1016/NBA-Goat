"""Statistics models.

Defines `CareerStats`, `AdvancedStats`, and `SeasonStats` capturing core box score and
advanced metrics at different granularities.
"""

from . import db
from datetime import datetime

class CareerStats(db.Model):
    __tablename__ = 'career_stats'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)

    # Basic stats
    games_played = db.Column(db.Integer)
    games_started = db.Column(db.Integer)
    minutes_per_game = db.Column(db.Float)

    # Scoring
    points_per_game = db.Column(db.Float)
    field_goals_made = db.Column(db.Float)
    field_goals_attempted = db.Column(db.Float)
    field_goal_percentage = db.Column(db.Float)
    three_pointers_made = db.Column(db.Float)
    three_pointers_attempted = db.Column(db.Float)
    three_point_percentage = db.Column(db.Float)
    free_throws_made = db.Column(db.Float)
    free_throws_attempted = db.Column(db.Float)
    free_throw_percentage = db.Column(db.Float)

    # Rebounding
    rebounds_per_game = db.Column(db.Float)
    offensive_rebounds = db.Column(db.Float)
    defensive_rebounds = db.Column(db.Float)

    # Other stats
    assists_per_game = db.Column(db.Float)
    steals_per_game = db.Column(db.Float)
    blocks_per_game = db.Column(db.Float)
    turnovers_per_game = db.Column(db.Float)
    personal_fouls = db.Column(db.Float)

    # Career totals
    total_points = db.Column(db.Integer)
    total_rebounds = db.Column(db.Integer)
    total_assists = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<CareerStats for Player {self.player_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'games_played': self.games_played,
            'games_started': self.games_started,
            'minutes_per_game': self.minutes_per_game,
            'points_per_game': self.points_per_game,
            'field_goals_made': self.field_goals_made,
            'field_goals_attempted': self.field_goals_attempted,
            'field_goal_percentage': self.field_goal_percentage,
            'three_pointers_made': self.three_pointers_made,
            'three_pointers_attempted': self.three_pointers_attempted,
            'three_point_percentage': self.three_point_percentage,
            'free_throws_made': self.free_throws_made,
            'free_throws_attempted': self.free_throws_attempted,
            'free_throw_percentage': self.free_throw_percentage,
            'rebounds_per_game': self.rebounds_per_game,
            'offensive_rebounds': self.offensive_rebounds,
            'defensive_rebounds': self.defensive_rebounds,
            'assists_per_game': self.assists_per_game,
            'steals_per_game': self.steals_per_game,
            'blocks_per_game': self.blocks_per_game,
            'turnovers_per_game': self.turnovers_per_game,
            'personal_fouls': self.personal_fouls,
            'total_points': self.total_points,
            'total_rebounds': self.total_rebounds,
            'total_assists': self.total_assists
        }


class AdvancedStats(db.Model):
    __tablename__ = 'advanced_stats'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)

    # Advanced metrics
    player_efficiency_rating = db.Column(db.Float)  # PER
    true_shooting_percentage = db.Column(db.Float)  # TS%
    effective_field_goal_percentage = db.Column(db.Float)  # eFG%
    offensive_rating = db.Column(db.Float)  # ORtg
    defensive_rating = db.Column(db.Float)  # DRtg
    net_rating = db.Column(db.Float)  # NetRtg

    # Win shares and advanced
    win_shares = db.Column(db.Float)  # WS
    win_shares_per_48 = db.Column(db.Float)  # WS/48
    box_plus_minus = db.Column(db.Float)  # BPM
    value_over_replacement = db.Column(db.Float)  # VORP

    # Usage and pace
    usage_rate = db.Column(db.Float)  # USG%
    pace = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AdvancedStats for Player {self.player_id}>'


class SeasonStats(db.Model):
    __tablename__ = 'season_stats'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)

    season = db.Column(db.String(10), nullable=False)  # e.g., "2023-24"
    team_id = db.Column(db.Integer)
    team_abbreviation = db.Column(db.String(5))

    # Same structure as career stats but for individual seasons
    games_played = db.Column(db.Integer)
    games_started = db.Column(db.Integer)
    minutes_per_game = db.Column(db.Float)
    points_per_game = db.Column(db.Float)
    rebounds_per_game = db.Column(db.Float)
    assists_per_game = db.Column(db.Float)
    field_goal_percentage = db.Column(db.Float)
    three_point_percentage = db.Column(db.Float)
    free_throw_percentage = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SeasonStats {self.season} for Player {self.player_id}>'