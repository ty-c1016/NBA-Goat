"""Application configuration.

Loads environment variables via `python-dotenv` and exposes a `Config` class used by
the Flask app. Supports SQLite by default and PostgreSQL via `DATABASE_URL`.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database configuration
    # Use DATABASE_URL from environment if set, otherwise default to SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'instance', 'nba_goat.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLite-specific settings for better concurrency
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'timeout': 30,  # Wait up to 30 seconds if database is locked
            'check_same_thread': False
        },
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }

    # Application settings
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'