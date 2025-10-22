"""Player model.

Represents an NBA player and basic biographical/career info. Related one-to-one/one-to-many
with `CareerStats`, `AdvancedStats`, `SeasonStats`, and `Achievement`.
"""

from . import db
from datetime import datetime

class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    nba_id = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    position = db.Column(db.String(10))
    height = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    birth_date = db.Column(db.Date)

    # Career info
    from_year = db.Column(db.Integer)
    to_year = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=False)

    # Teams (simplified - could be normalized into separate table)
    teams = db.Column(db.Text)  # JSON string of teams played for

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    career_stats = db.relationship('CareerStats', backref='player', uselist=False)
    advanced_stats = db.relationship('AdvancedStats', backref='player', uselist=False)
    season_stats = db.relationship('SeasonStats', backref='player')
    achievements = db.relationship('Achievement', backref='player', uselist=False)

    def __repr__(self):
        return f'<Player {self.full_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'nba_id': self.nba_id,
            'full_name': self.full_name,
            'position': self.position,
            'height': self.height,
            'weight': self.weight,
            'from_year': self.from_year,
            'to_year': self.to_year,
            'is_active': self.is_active
        }