"""Database and model package setup.

Initializes SQLAlchemy (`db`) and Flask-Migrate (`migrate`) and exposes model classes
for convenient imports elsewhere in the application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

from .player import Player
from .stats import CareerStats, AdvancedStats, SeasonStats
from .achievements import Achievement
from .user_session import UserSession