"""Flask application entrypoint.

This module wires up the Flask app, initializes extensions, and defines routes for:
- `GET /` home page
- `GET /questions` questionnaire to capture user preferences
- `POST /submit_preferences` processing preferences and persisting a `UserSession`
- `GET /results/<session_id>` showing personalized rankings
- `GET /api/players` and `GET /api/player/<id>` lightweight JSON APIs

The ranking logic is implemented in `calculate_player_rankings`, which applies a
simple weighted scoring across player statistics and achievements.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, migrate, Player, CareerStats, AdvancedStats, Achievement, UserSession
from config import Config
import uuid
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    return app

app = create_app()

@app.route('/')
def index():
    """Main page with the questionnaire"""
    return render_template('index.html')

@app.route('/questions')
def questions():
    """Display the questionnaire"""
    # Generate a unique session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    return render_template('questions.html')

@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    """Process user preferences and calculate rankings"""
    try:
        # Get user preferences from form
        preferences = {
            'offensive_weight': float(request.form.get('offensive_weight', 0.5)),
            'defensive_weight': float(request.form.get('defensive_weight', 0.5)),
            'longevity_weight': float(request.form.get('longevity_weight', 0.5)),
            'team_success_weight': float(request.form.get('team_success_weight', 0.5)),
            'efficiency_weight': float(request.form.get('efficiency_weight', 0.5)),
            'peak_performance_weight': float(request.form.get('peak_performance_weight', 0.5)),
            'era_preference': request.form.get('era_preference', 'any')
        }

        # Always create a new session for each ranking calculation
        # This ensures each preference submission gets a unique results URL
        new_session_id = str(uuid.uuid4())
        user_session = UserSession(
            session_id=new_session_id,
            **preferences,
            ip_address=request.remote_addr
        )
        db.session.add(user_session)

        # Update the Flask session to track the new session
        session['session_id'] = new_session_id

        # Calculate rankings based on preferences
        ranked_players = calculate_player_rankings(preferences)
        user_session.set_ranked_players(ranked_players)
        user_session.completed_at = db.func.now()

        db.session.commit()

        return redirect(url_for('results', session_id=user_session.session_id))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results/<session_id>')
def results(session_id):
    """Display the ranked results"""
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        return redirect(url_for('index'))

    ranked_players = user_session.get_ranked_players()
    return render_template('results.html', players=ranked_players, session=user_session)

@app.route('/api/players')
def api_players():
    """API endpoint to get all players"""
    players = Player.query.all()
    return jsonify([player.to_dict() for player in players])

@app.route('/api/player/<int:player_id>')
def api_player_detail(player_id):
    """API endpoint to get detailed player information"""
    player = Player.query.get_or_404(player_id)

    player_data = player.to_dict()

    # Add stats if available
    if player.career_stats:
        player_data['career_stats'] = {
            'points_per_game': player.career_stats.points_per_game,
            'rebounds_per_game': player.career_stats.rebounds_per_game,
            'assists_per_game': player.career_stats.assists_per_game,
            'field_goal_percentage': player.career_stats.field_goal_percentage,
            'games_played': player.career_stats.games_played,
            'total_points': player.career_stats.total_points
        }

    if player.achievements:
        player_data['achievements'] = {
            'championships': player.achievements.championships,
            'mvp_awards': player.achievements.mvp_awards,
            'all_star_selections': player.achievements.all_star_selections,
            'hall_of_fame': player.achievements.hall_of_fame
        }

    return jsonify(player_data)

def calculate_player_rankings(preferences):
    """Calculate player rankings based on user preferences with normalized scoring"""
    import numpy as np

    # Filter for quality players only (minimum 20 games for meaningful stats)
    players = db.session.query(Player).join(CareerStats).join(Achievement).filter(
        CareerStats.games_played >= 20
    ).all()

    if not players:
        return []

    # Extract all stats for normalization
    all_stats = {
        'ppg': [p.career_stats.points_per_game or 0 for p in players],
        'fg_pct': [p.career_stats.field_goal_percentage or 0 for p in players],
        'apg': [p.career_stats.assists_per_game or 0 for p in players],
        'rpg': [p.career_stats.rebounds_per_game or 0 for p in players],
        'spg': [p.career_stats.steals_per_game or 0 for p in players],
        'bpg': [p.career_stats.blocks_per_game or 0 for p in players],
        'games': [p.career_stats.games_played or 0 for p in players],
        'total_points': [p.career_stats.total_points or 0 for p in players],
        'championships': [p.achievements.championships or 0 for p in players],
        'finals_appearances': [p.achievements.finals_appearances or 0 for p in players],
        'mvp_awards': [p.achievements.mvp_awards or 0 for p in players],
        'all_star_selections': [p.achievements.all_star_selections or 0 for p in players]
    }

    # Calculate percentiles for normalization (0-100 scale)
    def get_percentile_score(value, stat_list):
        if not stat_list or len(stat_list) == 0:
            return 0
        if value is None:
            return 0

        # Convert to float and handle NaN
        try:
            value = float(value)
            if np.isnan(value):
                return 0
        except (TypeError, ValueError):
            return 0

        # Sort the list and find percentile
        sorted_list = sorted([float(x) for x in stat_list if x is not None and not np.isnan(float(x))])
        if not sorted_list:
            return 0

        # Find the percentile rank
        n = len(sorted_list)
        rank = sum(1 for x in sorted_list if x <= value)
        return (rank / n) * 100

    scored_players = []

    for player in players:
        if not player.career_stats:
            continue

        # Normalize each metric to 0-100 percentile
        offensive_metrics = {
            'ppg': get_percentile_score(player.career_stats.points_per_game or 0, all_stats['ppg']),
            'fg_pct': get_percentile_score(player.career_stats.field_goal_percentage or 0, all_stats['fg_pct']),
            'apg': get_percentile_score(player.career_stats.assists_per_game or 0, all_stats['apg']),
            'total_points': get_percentile_score(player.career_stats.total_points or 0, all_stats['total_points'])
        }

        defensive_metrics = {
            'spg': get_percentile_score(player.career_stats.steals_per_game or 0, all_stats['spg']),
            'bpg': get_percentile_score(player.career_stats.blocks_per_game or 0, all_stats['bpg']),
            'rpg': get_percentile_score(player.career_stats.rebounds_per_game or 0, all_stats['rpg'])
        }

        longevity_metrics = {
            'games': get_percentile_score(player.career_stats.games_played or 0, all_stats['games'])
        }

        team_success_metrics = {
            'championships': get_percentile_score(player.achievements.championships or 0, all_stats['championships']),
            'finals_appearances': get_percentile_score(player.achievements.finals_appearances or 0, all_stats['finals_appearances'])
        }

        efficiency_metrics = {
            'fg_pct': offensive_metrics['fg_pct'],  # Reuse FG%
            'scoring_efficiency': offensive_metrics['ppg'] * (offensive_metrics['fg_pct'] / 100)
        }

        peak_performance_metrics = {
            'mvp_awards': get_percentile_score(player.achievements.mvp_awards or 0, all_stats['mvp_awards']),
            'all_star_selections': get_percentile_score(player.achievements.all_star_selections or 0, all_stats['all_star_selections'])
        }

        # Calculate weighted category scores (0-100 scale)
        offensive_score = (
            offensive_metrics['ppg'] * 0.4 +
            offensive_metrics['fg_pct'] * 0.2 +
            offensive_metrics['apg'] * 0.2 +
            offensive_metrics['total_points'] * 0.2
        )

        defensive_score = (
            defensive_metrics['spg'] * 0.3 +
            defensive_metrics['bpg'] * 0.3 +
            defensive_metrics['rpg'] * 0.4
        )

        longevity_score = longevity_metrics['games']

        team_success_score = (
            team_success_metrics['championships'] * 0.7 +
            team_success_metrics['finals_appearances'] * 0.3
        )

        efficiency_score = efficiency_metrics['scoring_efficiency']

        peak_performance_score = (
            peak_performance_metrics['mvp_awards'] * 0.6 +
            peak_performance_metrics['all_star_selections'] * 0.4
        )

        # Normalize weights to ensure they sum to 1.0
        # This ensures that different weight distributions are comparable
        total_weight = (
            preferences['offensive_weight'] +
            preferences['defensive_weight'] +
            preferences['longevity_weight'] +
            preferences['team_success_weight'] +
            preferences['efficiency_weight'] +
            preferences['peak_performance_weight']
        )

        # Avoid division by zero
        if total_weight == 0:
            total_weight = 1.0

        # Normalize each weight
        normalized_weights = {
            'offensive': preferences['offensive_weight'] / total_weight,
            'defensive': preferences['defensive_weight'] / total_weight,
            'longevity': preferences['longevity_weight'] / total_weight,
            'team_success': preferences['team_success_weight'] / total_weight,
            'efficiency': preferences['efficiency_weight'] / total_weight,
            'peak_performance': preferences['peak_performance_weight'] / total_weight
        }

        # Final weighted score using normalized weights
        # Each category score is 0-100, so final score will also be 0-100
        total_score = (
            offensive_score * normalized_weights['offensive'] +
            defensive_score * normalized_weights['defensive'] +
            longevity_score * normalized_weights['longevity'] +
            team_success_score * normalized_weights['team_success'] +
            efficiency_score * normalized_weights['efficiency'] +
            peak_performance_score * normalized_weights['peak_performance']
        )

        scored_players.append({
            'player': player.to_dict(),
            'score': total_score,
            'category_scores': {
                'offensive': offensive_score,
                'defensive': defensive_score,
                'longevity': longevity_score,
                'team_success': team_success_score,
                'efficiency': efficiency_score,
                'peak_performance': peak_performance_score
            },
            'career_stats': player.career_stats.to_dict() if player.career_stats else {},
            'achievements': player.achievements.to_dict() if player.achievements else {}
        })

    # Sort by score and return top 100
    scored_players.sort(key=lambda x: x['score'], reverse=True)
    return scored_players[:100]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)