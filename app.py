"""Flask application — routes and app setup."""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from models import db, migrate, Player, CareerStats, AdvancedStats, Achievement, UserSession, SeasonStats
from config import Config
from ranking import calculate_player_rankings
import uuid
import os
import math
import time
from collections import defaultdict

_rate_limit_store = defaultdict(list)
_RATE_LIMIT_WINDOW = 60
_RATE_LIMIT_MAX = 10

def _is_rate_limited(key):
    now = time.time()
    _rate_limit_store[key] = [t for t in _rate_limit_store[key] if now - t < _RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[key]) >= _RATE_LIMIT_MAX:
        return True
    _rate_limit_store[key].append(now)
    return False

def _safe_weight(value, default=0.5):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(0.0, min(1.0, v))

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    return app

app = create_app()

REACT_BUILD = os.path.join(os.path.dirname(__file__), 'static', 'dist')

def _serve_react():
    index_path = os.path.join(REACT_BUILD, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(REACT_BUILD, 'index.html')
    return render_template('index.html')

@app.route('/')
def index():
    return _serve_react()

@app.route('/questions')
@app.route('/results/<path:subpath>')
def spa_routes(subpath=''):
    return _serve_react()

@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    """Legacy form-based preferences submission."""
    if _is_rate_limited(request.remote_addr):
        return jsonify({'error': 'Too many requests'}), 429
    try:
        preferences = {
            'offensive_weight':       float(request.form.get('offensive_weight', 0.5)),
            'defensive_weight':       float(request.form.get('defensive_weight', 0.5)),
            'longevity_weight':       float(request.form.get('longevity_weight', 0.5)),
            'team_success_weight':    float(request.form.get('team_success_weight', 0.5)),
            'efficiency_weight':      float(request.form.get('efficiency_weight', 0.5)),
            'peak_performance_weight': float(request.form.get('peak_performance_weight', 0.5)),
            'era_preference':         request.form.get('era_preference', 'any'),
        }
        new_session_id = str(uuid.uuid4())
        user_session = UserSession(session_id=new_session_id, **preferences, ip_address=None)
        db.session.add(user_session)
        session['session_id'] = new_session_id
        ranked_players = calculate_player_rankings(preferences)
        user_session.set_ranked_players(ranked_players)
        user_session.completed_at = db.func.now()
        db.session.commit()
        return redirect(url_for('results_legacy', session_id=user_session.session_id))
    except Exception:
        app.logger.exception("Error in submit_preferences")
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/results_legacy/<session_id>')
def results_legacy(session_id):
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        return redirect(url_for('index'))
    return render_template('results.html', players=user_session.get_ranked_players(), session=user_session)

@app.route('/api/submit_preferences', methods=['POST'])
def api_submit_preferences():
    if _is_rate_limited(request.remote_addr):
        return jsonify({'error': 'Too many requests'}), 429
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'Request must be JSON'}), 415

        era_value = data.get('era_preference', 'any')
        if era_value not in ('modern', 'classic', 'any'):
            era_value = 'any'

        preferences = {
            'offensive_weight':       _safe_weight(data.get('offensive_weight', 0.5)),
            'defensive_weight':       _safe_weight(data.get('defensive_weight', 0.5)),
            'longevity_weight':       _safe_weight(data.get('longevity_weight', 0.5)),
            'team_success_weight':    _safe_weight(data.get('team_success_weight', 0.5)),
            'efficiency_weight':      _safe_weight(data.get('efficiency_weight', 0.5)),
            'peak_performance_weight': _safe_weight(data.get('peak_performance_weight', 0.5)),
            'era_preference':         era_value,
        }

        new_session_id = str(uuid.uuid4())
        user_session = UserSession(session_id=new_session_id, **preferences, ip_address=None)
        db.session.add(user_session)
        ranked_players = calculate_player_rankings(preferences)
        user_session.set_ranked_players(ranked_players)
        user_session.completed_at = db.func.now()
        db.session.commit()

        return jsonify({'session_id': new_session_id, 'ranked_players': ranked_players})
    except Exception:
        app.logger.exception("Error in api_submit_preferences")
        return jsonify({'error': 'An internal error occurred'}), 500

@app.route('/api/players')
def api_players():
    return jsonify([p.to_dict() for p in Player.query.all()])

@app.route('/api/player/<int:player_id>')
def api_player_detail(player_id):
    player = Player.query.get_or_404(player_id)
    data = player.to_dict()
    if player.career_stats:
        data['career_stats'] = {
            'points_per_game':        player.career_stats.points_per_game,
            'rebounds_per_game':      player.career_stats.rebounds_per_game,
            'assists_per_game':       player.career_stats.assists_per_game,
            'field_goal_percentage':  player.career_stats.field_goal_percentage,
            'games_played':           player.career_stats.games_played,
            'total_points':           player.career_stats.total_points,
        }
    if player.achievements:
        data['achievements'] = {
            'championships':      player.achievements.championships,
            'mvp_awards':         player.achievements.mvp_awards,
            'all_star_selections': player.achievements.all_star_selections,
            'hall_of_fame':       player.achievements.hall_of_fame,
        }
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
