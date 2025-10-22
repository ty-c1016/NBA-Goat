"""User session model.

Persists a user's preference weights and computed rankings for later retrieval.
Includes helpers to serialize/deserialize JSON fields.
"""

from . import db
from datetime import datetime
import json

class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)

    # User preferences (stored as JSON)
    offensive_weight = db.Column(db.Float, default=0.5)  # 0-1 scale
    defensive_weight = db.Column(db.Float, default=0.5)
    longevity_weight = db.Column(db.Float, default=0.5)
    team_success_weight = db.Column(db.Float, default=0.5)
    efficiency_weight = db.Column(db.Float, default=0.5)
    peak_performance_weight = db.Column(db.Float, default=0.5)
    era_preference = db.Column(db.String(20))  # 'modern', 'classic', 'any'

    # Results (stored as JSON string)
    ranked_players = db.Column(db.Text)  # JSON array of player rankings
    custom_weights = db.Column(db.Text)  # JSON object of any custom weightings

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))  # Support IPv6

    def __repr__(self):
        return f'<UserSession {self.session_id}>'

    def set_ranked_players(self, players_list):
        """Store the ranked players as JSON"""
        self.ranked_players = json.dumps(players_list)

    def get_ranked_players(self):
        """Retrieve the ranked players from JSON"""
        if self.ranked_players:
            return json.loads(self.ranked_players)
        return []

    def set_custom_weights(self, weights_dict):
        """Store custom weights as JSON"""
        self.custom_weights = json.dumps(weights_dict)

    def get_custom_weights(self):
        """Retrieve custom weights from JSON"""
        if self.custom_weights:
            return json.loads(self.custom_weights)
        return {}