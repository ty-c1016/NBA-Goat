"""Flask application entrypoint.

This module wires up the Flask app, initializes extensions, and defines routes for:
- `GET /` serves the React SPA (production) or legacy template (development)
- `POST /api/submit_preferences` JSON API for preference submission and ranking
- `GET /api/players` and `GET /api/player/<id>` lightweight JSON APIs

The ranking logic is implemented in `calculate_player_rankings`, which applies a
simple weighted scoring across player statistics and achievements.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from models import db, migrate, Player, CareerStats, AdvancedStats, Achievement, UserSession, SeasonStats
from config import Config
import uuid
import os

def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    return app

app = create_app()

REACT_BUILD = os.path.join(os.path.dirname(__file__), 'static', 'dist')

def _serve_react():
    """Serve the React SPA index.html if the build exists."""
    index_path = os.path.join(REACT_BUILD, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(REACT_BUILD, 'index.html')
    # Fallback to legacy Jinja2 template during development
    return render_template('index.html')

@app.route('/')
def index():
    return _serve_react()

# Catch-all: let React Router handle client-side routes
@app.route('/questions')
@app.route('/results/<path:subpath>')
def spa_routes(subpath=''):
    return _serve_react()

# Legacy form-based endpoint kept for backwards compatibility
@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    """Legacy form-based preferences submission (redirects to results template)."""
    try:
        preferences = {
            'offensive_weight': float(request.form.get('offensive_weight', 0.5)),
            'defensive_weight': float(request.form.get('defensive_weight', 0.5)),
            'longevity_weight': float(request.form.get('longevity_weight', 0.5)),
            'team_success_weight': float(request.form.get('team_success_weight', 0.5)),
            'efficiency_weight': float(request.form.get('efficiency_weight', 0.5)),
            'peak_performance_weight': float(request.form.get('peak_performance_weight', 0.5)),
            'era_preference': request.form.get('era_preference', 'any')
        }

        new_session_id = str(uuid.uuid4())
        user_session = UserSession(
            session_id=new_session_id,
            **preferences,
            ip_address=request.remote_addr
        )
        db.session.add(user_session)
        session['session_id'] = new_session_id

        ranked_players = calculate_player_rankings(preferences)
        user_session.set_ranked_players(ranked_players)
        user_session.completed_at = db.func.now()
        db.session.commit()

        return redirect(url_for('results_legacy', session_id=user_session.session_id))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results_legacy/<session_id>')
def results_legacy(session_id):
    """Legacy Jinja2 results page."""
    user_session = UserSession.query.filter_by(session_id=session_id).first()
    if not user_session:
        return redirect(url_for('index'))
    ranked_players = user_session.get_ranked_players()
    return render_template('results.html', players=ranked_players, session=user_session)

# ── JSON API ──────────────────────────────────────────────────────────────────

@app.route('/api/submit_preferences', methods=['POST'])
def api_submit_preferences():
    """JSON API: submit preferences and return ranked players."""
    try:
        data = request.get_json(force=True)
        preferences = {
            'offensive_weight': float(data.get('offensive_weight', 0.5)),
            'defensive_weight': float(data.get('defensive_weight', 0.5)),
            'longevity_weight': float(data.get('longevity_weight', 0.5)),
            'team_success_weight': float(data.get('team_success_weight', 0.5)),
            'efficiency_weight': float(data.get('efficiency_weight', 0.5)),
            'peak_performance_weight': float(data.get('peak_performance_weight', 0.5)),
            'era_preference': data.get('era_preference', 'any')
        }

        new_session_id = str(uuid.uuid4())
        user_session = UserSession(
            session_id=new_session_id,
            **preferences,
            ip_address=request.remote_addr
        )
        db.session.add(user_session)

        ranked_players = calculate_player_rankings(preferences)
        user_session.set_ranked_players(ranked_players)
        user_session.completed_at = db.func.now()
        db.session.commit()

        return jsonify({
            'session_id': new_session_id,
            'ranked_players': ranked_players
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

    # Filter for quality players only - baseline standards for GOAT consideration
    # Minimum 400 games (≈5 seasons) and 10 PPG to ensure substantial, impactful careers
    players = db.session.query(Player).join(CareerStats).join(Achievement).filter(
        CareerStats.games_played >= 400,
        CareerStats.points_per_game >= 10.0
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
        'championships': np.array([p.achievements.get_weighted_championships() for p in players], dtype=float),
        'finals_appearances': np.array([p.achievements.finals_appearances or 0 for p in players], dtype=float),
        'mvp_awards': np.array([p.achievements.mvp_awards or 0 for p in players], dtype=float),
        'all_star_selections': np.array([p.achievements.all_star_selections or 0 for p in players], dtype=float),
        'all_nba_first': np.array([p.achievements.all_nba_first_team or 0 for p in players], dtype=float),
        'all_nba_second': np.array([p.achievements.all_nba_second_team or 0 for p in players], dtype=float),
        'all_nba_third': np.array([p.achievements.all_nba_third_team or 0 for p in players], dtype=float),
        'scoring_titles': np.array([p.achievements.scoring_titles or 0 for p in players], dtype=float),
        'seasons_30ppg': np.array([p.achievements.seasons_30ppg or 0 for p in players], dtype=float)
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
            'total_points': percentile_stats['total_points'][idx],
            'scoring_titles': percentile_stats['scoring_titles'][idx]
        }

        defensive_metrics = {
            'spg': percentile_stats['spg'][idx],
            'bpg': percentile_stats['bpg'][idx],
            'rpg': percentile_stats['rpg'][idx]
        }

        # Calculate quality longevity score based on season PPG
        # Rewards sustained excellence, penalizes decline years
        # Exclude incomplete seasons (< 40 games for modern, < 30 for 1960s era)
        season_stats = SeasonStats.query.filter_by(player_id=player.id).order_by(SeasonStats.season).all()

        # Bill Russell era: use lower threshold (seasons were 68-82 games in 1960s)
        if player.full_name == 'Bill Russell':
            games_threshold = 30
        else:
            games_threshold = 40

        complete_seasons = [s for s in season_stats if s.games_played >= games_threshold]

        if complete_seasons:
            # Special case: Bill Russell was a defensive specialist, not a scorer
            # His value came from defense/rebounding, so quality rules don't apply
            if player.full_name == 'Bill Russell':
                quality_bonus = 0  # No penalties or bonuses based on PPG
                quality_longevity = percentile_stats['games'][idx] * 0.5
            else:
                seasons_25plus = sum(1 for s in complete_seasons if s.points_per_game >= 25)
                seasons_20_25 = sum(1 for s in complete_seasons if 20 <= s.points_per_game < 25)
                seasons_under15 = sum(1 for i, s in enumerate(complete_seasons, 1)
                                     if s.points_per_game < 15 and i > 3)  # Penalty after year 3

                # Quality longevity score
                # Base: games played percentile (weighted at 0.5x to reduce impact)
                # Bonus: +2 points per 25+ PPG season (first 5), +1 point per 25+ PPG season (after 5)
                # Bonus: +1 point per 20-25 PPG season
                # Penalty: -3 points per sub-15 PPG season after year 3
                if seasons_25plus <= 5:
                    bonus_25plus = seasons_25plus * 2
                else:
                    # First 5 seasons: 2 points each, remaining seasons: 1 point each
                    bonus_25plus = (5 * 2) + ((seasons_25plus - 5) * 1)

                quality_bonus = bonus_25plus + (seasons_20_25 * 1) - (seasons_under15 * 3)
                quality_longevity = (percentile_stats['games'][idx] * 0.5) + quality_bonus
        else:
            # Fall back to games only if no season data (also weighted at 0.5x)
            quality_longevity = percentile_stats['games'][idx] * 0.5

        longevity_metrics = {
            'games': percentile_stats['games'][idx],
            'quality_longevity': quality_longevity
        }

        team_success_metrics = {
            'championships': percentile_stats['championships'][idx],
            'finals_appearances': percentile_stats['finals_appearances'][idx]
        }

        efficiency_metrics = {
            'fg_pct': offensive_metrics['fg_pct'],  # Reuse FG%
            'scoring_efficiency': offensive_metrics['ppg'] * (offensive_metrics['fg_pct'] / 100),
            'scoring_titles': offensive_metrics['scoring_titles']  # Scoring titles indicate elite efficiency
        }

        individual_success_metrics = {
            'mvp_awards': percentile_stats['mvp_awards'][idx],
            'all_star_selections': percentile_stats['all_star_selections'][idx],
            'all_nba_first': percentile_stats['all_nba_first'][idx],
            'all_nba_second': percentile_stats['all_nba_second'][idx],
            'all_nba_third': percentile_stats['all_nba_third'][idx],
            'scoring_titles': percentile_stats['scoring_titles'][idx],
            'seasons_30ppg': percentile_stats['seasons_30ppg'][idx]
        }

        # Determine player position from database
        # Position values from NBA API: "Guard", "Forward", "Center", or combinations like "Guard-Forward"
        # We classify as guard if "Guard" appears in position (includes Guard-Forward combo guards)
        position = player.position or ""
        is_guard = "Guard" in position

        # Calculate weighted category scores (0-100 scale)
        # Position-based adjustments:
        # Guards: Boost PPG/APG weight, reduce rebounds/blocks emphasis
        # Forwards/Centers: Traditional weights with emphasis on rebounds/blocks
        if is_guard:
            offensive_score = (
                offensive_metrics['ppg'] * 0.40 +          # Reduced slightly to make room
                offensive_metrics['fg_pct'] * 0.10 +       # Reduced
                offensive_metrics['apg'] * 0.20 +          # Reduced slightly
                offensive_metrics['total_points'] * 0.10 + # Same
                offensive_metrics['scoring_titles'] * 0.20  # NEW: Substantial weight for scoring titles
            )
        else:
            offensive_score = (
                offensive_metrics['ppg'] * 0.35 +          # Reduced to make room
                offensive_metrics['fg_pct'] * 0.15 +       # Reduced
                offensive_metrics['apg'] * 0.15 +          # Reduced
                offensive_metrics['total_points'] * 0.15 + # Reduced
                offensive_metrics['scoring_titles'] * 0.20  # NEW: Substantial weight for scoring titles
            )

        # Reduce defensive weight overall (especially for guards)
        # Previous: SPG=0.3, BPG=0.3, RPG=0.4
        # New: Reduced emphasis on blocks/rebounds

        # Special case: Bill Russell played in an era before steals/blocks were tracked
        # His defensive dominance is well-documented, so we hard-code his defensive score
        if player.full_name == 'Bill Russell':
            defensive_score = 99.0  # Recognizing his legendary defense despite missing stats
        elif is_guard:
            defensive_score = (
                defensive_metrics['spg'] * 0.5 +       # Guards are judged more on steals
                defensive_metrics['bpg'] * 0.1 +       # Blocks less relevant
                defensive_metrics['rpg'] * 0.4         # Rebounds less expected but still valued
            )
        else:
            defensive_score = (
                defensive_metrics['spg'] * 0.25 +      # Reduced from 0.3
                defensive_metrics['bpg'] * 0.35 +      # Slightly increased
                defensive_metrics['rpg'] * 0.40        # Kept same
            )

        longevity_score = longevity_metrics['quality_longevity']

        # Base team success score
        base_team_success = (
            team_success_metrics['championships'] * 0.7 +
            team_success_metrics['finals_appearances'] * 0.3
        )

        # Championship multipliers: reward dynasty-level success
        championships = player.achievements.championships or 0

        if championships >= 10:
            # Double-digit championships (Bill Russell): DOUBLE the team success score
            team_success_score = base_team_success * 2.0
        elif championships >= 4:
            # 4+ championships (dynasty builders): 50% boost
            team_success_score = base_team_success * 1.5
        else:
            team_success_score = base_team_success

        efficiency_score = (
            efficiency_metrics['scoring_efficiency'] * 0.70 +  # Scoring efficiency (PPG × FG%)
            efficiency_metrics['scoring_titles'] * 0.30         # Scoring titles indicate consistent elite efficiency
        )

        individual_success_score = (
            individual_success_metrics['mvp_awards'] * 0.25 +
            individual_success_metrics['all_star_selections'] * 0.10 +     # Reduced from 0.15
            individual_success_metrics['all_nba_first'] * 0.15 +          # Reduced from 0.20
            individual_success_metrics['all_nba_second'] * 0.08 +         # Reduced from 0.10
            individual_success_metrics['all_nba_third'] * 0.02 +          # Reduced from 0.05
            individual_success_metrics['scoring_titles'] * 0.20 +         # INCREASED from 0.05 - major peak performance indicator
            individual_success_metrics['seasons_30ppg'] * 0.20            # 30+ PPG seasons weighted heavily for peak scoring dominance
        )

        # Apply category floor weights to ensure all stats matter
        # Even if user sets a category to 0%, it still has 10% baseline influence
        # This prevents absurd rankings (e.g., a player with terrible stats ranking high)
        FLOOR_WEIGHT = 0.10  # 10% minimum weight for each category

        # Apply floor to each preference weight
        floored_weights = {
            'offensive': max(preferences['offensive_weight'], FLOOR_WEIGHT),
            'defensive': max(preferences['defensive_weight'], FLOOR_WEIGHT),
            'longevity': max(preferences['longevity_weight'], FLOOR_WEIGHT),
            'team_success': max(preferences['team_success_weight'], FLOOR_WEIGHT),
            'efficiency': max(preferences['efficiency_weight'], FLOOR_WEIGHT),
            'individual_success': max(preferences.get('individual_success_weight', preferences.get('peak_performance_weight', 0.5)), FLOOR_WEIGHT)
        }

        # Normalize weights to ensure they sum to 1.0
        total_weight = sum(floored_weights.values())

        # Avoid division by zero
        if total_weight == 0:
            total_weight = 1.0

        # Normalize each weight
        normalized_weights = {
            category: weight / total_weight
            for category, weight in floored_weights.items()
        }

        # Final weighted score using normalized weights with floors
        # Each category score is 0-100, so final score will also be 0-100
        total_score = (
            offensive_score * normalized_weights['offensive'] +
            defensive_score * normalized_weights['defensive'] +
            longevity_score * normalized_weights['longevity'] +
            team_success_score * normalized_weights['team_success'] +
            efficiency_score * normalized_weights['efficiency'] +
            individual_success_score * normalized_weights['individual_success']
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
                'individual_success': individual_success_score
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