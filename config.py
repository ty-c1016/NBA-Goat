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
    POSTGRES_USER = os.environ.get('POSTGRES_USER') or 'ty'  # Use current user
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD') or ''
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST') or 'localhost'
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT') or '5432'
    POSTGRES_DB = os.environ.get('POSTGRES_DB') or 'nba_goat'

    # Use PostgreSQL by default, fallback to SQLite for testing
    if POSTGRES_PASSWORD:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Application settings
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'