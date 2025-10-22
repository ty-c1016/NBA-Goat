"""Achievements model.

Stores team and individual accolades for a player (rings, MVPs, All-NBA, etc.).
"""

from . import db
from datetime import datetime

class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)

    # Championship info
    championships = db.Column(db.Integer, default=0)
    finals_appearances = db.Column(db.Integer, default=0)

    # Individual awards
    mvp_awards = db.Column(db.Integer, default=0)
    finals_mvp_awards = db.Column(db.Integer, default=0)
    defensive_player_of_year = db.Column(db.Integer, default=0)
    sixth_man_awards = db.Column(db.Integer, default=0)
    rookie_of_year = db.Column(db.Integer, default=0)

    # All-Star selections
    all_star_selections = db.Column(db.Integer, default=0)
    all_nba_first_team = db.Column(db.Integer, default=0)
    all_nba_second_team = db.Column(db.Integer, default=0)
    all_nba_third_team = db.Column(db.Integer, default=0)
    all_defensive_first_team = db.Column(db.Integer, default=0)
    all_defensive_second_team = db.Column(db.Integer, default=0)

    # Statistical achievements
    scoring_titles = db.Column(db.Integer, default=0)
    assist_titles = db.Column(db.Integer, default=0)
    rebound_titles = db.Column(db.Integer, default=0)
    steals_titles = db.Column(db.Integer, default=0)
    blocks_titles = db.Column(db.Integer, default=0)

    # Hall of Fame
    hall_of_fame = db.Column(db.Boolean, default=False)
    hall_of_fame_year = db.Column(db.Integer)

    # Jersey retirement
    jersey_retired = db.Column(db.Boolean, default=False)
    retired_teams = db.Column(db.Text)  # JSON string of teams that retired jersey

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Achievements for Player {self.player_id}>'

    def total_all_nba_teams(self):
        return (self.all_nba_first_team or 0) + (self.all_nba_second_team or 0) + (self.all_nba_third_team or 0)

    def total_all_defensive_teams(self):
        return (self.all_defensive_first_team or 0) + (self.all_defensive_second_team or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'player_id': self.player_id,
            'championships': self.championships,
            'finals_appearances': self.finals_appearances,
            'mvp_awards': self.mvp_awards,
            'finals_mvp_awards': self.finals_mvp_awards,
            'defensive_player_of_year': self.defensive_player_of_year,
            'sixth_man_awards': self.sixth_man_awards,
            'rookie_of_year': self.rookie_of_year,
            'all_star_selections': self.all_star_selections,
            'all_nba_first_team': self.all_nba_first_team,
            'all_nba_second_team': self.all_nba_second_team,
            'all_nba_third_team': self.all_nba_third_team,
            'all_defensive_first_team': self.all_defensive_first_team,
            'all_defensive_second_team': self.all_defensive_second_team,
            'scoring_titles': self.scoring_titles,
            'assist_titles': self.assist_titles,
            'rebound_titles': self.rebound_titles,
            'steals_titles': self.steals_titles,
            'blocks_titles': self.blocks_titles,
            'hall_of_fame': self.hall_of_fame,
            'hall_of_fame_year': self.hall_of_fame_year,
            'jersey_retired': self.jersey_retired,
            'retired_teams': self.retired_teams
        }