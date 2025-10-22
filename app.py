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
    from scipy import stats

    # Filter for quality players only (minimum 20 games for meaningful stats)
    players = db.session.query(Player).join(CareerStats).join(Achievement).filter(
        CareerStats.games_played >= 20
    ).all()

    if not players:
        return []

    # Extract all stats as numpy arrays for fast vectorized operations
    all_stats = {
        'ppg': np.array([p.career_stats.points_per_game or 0 for p in players], dtype=float),
        'fg_pct': np.array([p.career_stats.field_goal_percentage or 0 for p in players], dtype=float),
        'apg': np.array([p.career_stats.assists_per_game or 0 for p in players], dtype=float),
        'rpg': np.array([p.career_stats.rebounds_per_game or 0 for p in players], dtype=float),
        'spg': np.array([p.career_stats.steals_per_game or 0 for p in players], dtype=float),
        'bpg': np.array([p.career_stats.blocks_per_game or 0 for p in players], dtype=float),
        'games': np.array([p.career_stats.games_played or 0 for p in players], dtype=float),
        'total_points': np.array([p.career_stats.total_points or 0 for p in players], dtype=float),
        'championships': np.array([p.achievements.championships or 0 for p in players], dtype=float),
        'finals_appearances': np.array([p.achievements.finals_appearances or 0 for p in players], dtype=float),
        'mvp_awards': np.array([p.achievements.mvp_awards or 0 for p in players], dtype=float),
        'all_star_selections': np.array([p.achievements.all_star_selections or 0 for p in players], dtype=float)
    }

    # Pre-compute percentile ranks using scipy for all stats at once (much faster)
    # This converts raw values to 0-100 percentile scale
    percentile_stats = {}
    for stat_name, stat_values in all_stats.items():
        # Use scipy.stats.rankdata for fast percentile calculation
        # 'average' method handles ties by averaging ranks
        ranks = stats.rankdata(stat_values, method='average')
        percentile_stats[stat_name] = (ranks / len(ranks)) * 100

    scored_players = []

    for idx, player in enumerate(players):
        if not player.career_stats:
            continue

        # Lookup pre-computed percentiles (O(1) instead of O(n))
        offensive_metrics = {
            'ppg': percentile_stats['ppg'][idx],
            'fg_pct': percentile_stats['fg_pct'][idx],
            'apg': percentile_stats['apg'][idx],
            'total_points': percentile_stats['total_points'][idx]
        }

        defensive_metrics = {
            'spg': percentile_stats['spg'][idx],
            'bpg': percentile_stats['bpg'][idx],
            'rpg': percentile_stats['rpg'][idx]
        }

        longevity_metrics = {
            'games': percentile_stats['games'][idx]
        }

        team_success_metrics = {
            'championships': percentile_stats['championships'][idx],
            'finals_appearances': percentile_stats['finals_appearances'][idx]
        }

        efficiency_metrics = {
            'fg_pct': offensive_metrics['fg_pct'],  # Reuse FG%
            'scoring_efficiency': offensive_metrics['ppg'] * (offensive_metrics['fg_pct'] / 100)
        }

        peak_performance_metrics = {
            'mvp_awards': percentile_stats['mvp_awards'][idx],
            'all_star_selections': percentile_stats['all_star_selections'][idx]
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