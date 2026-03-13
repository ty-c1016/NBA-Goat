"""Player ranking algorithm.

Computes a weighted, percentile-normalized score for each player
based on user preference weights across six categories:
offensive, defensive, longevity, team_success, efficiency, individual_success.
"""

import numpy as np
from scipy import stats
from sqlalchemy.orm import joinedload
from models import db, Player, CareerStats, Achievement


def calculate_player_rankings(preferences):
    players = db.session.query(Player).join(CareerStats).join(Achievement).options(
        joinedload(Player.career_stats),
        joinedload(Player.achievements),
        joinedload(Player.season_stats)
    ).filter(
        CareerStats.games_played >= 400,
        CareerStats.points_per_game >= 10.0
    ).all()

    if not players:
        return []

    era_preference = preferences.get('era_preference', 'any')
    if era_preference == 'modern':
        players = [p for p in players if (p.to_year or 0) >= 2000]
    elif era_preference == 'classic':
        players = [p for p in players if (p.from_year or 9999) < 2000]

    if not players:
        return []

    all_stats = {
        'ppg':              np.array([p.career_stats.points_per_game or 0 for p in players], dtype=float),
        'fg_pct':           np.array([p.career_stats.field_goal_percentage or 0 for p in players], dtype=float),
        'apg':              np.array([p.career_stats.assists_per_game or 0 for p in players], dtype=float),
        'rpg':              np.array([p.career_stats.rebounds_per_game or 0 for p in players], dtype=float),
        'spg':              np.array([p.career_stats.steals_per_game or 0 for p in players], dtype=float),
        'bpg':              np.array([p.career_stats.blocks_per_game or 0 for p in players], dtype=float),
        'games':            np.array([p.career_stats.games_played or 0 for p in players], dtype=float),
        'total_points':     np.array([p.career_stats.total_points or 0 for p in players], dtype=float),
        'championships':    np.array([p.achievements.get_weighted_championships() for p in players], dtype=float),
        'finals_appearances': np.array([p.achievements.finals_appearances or 0 for p in players], dtype=float),
        'mvp_awards':       np.array([p.achievements.mvp_awards or 0 for p in players], dtype=float),
        'all_star_selections': np.array([p.achievements.all_star_selections or 0 for p in players], dtype=float),
        'all_nba_first':    np.array([p.achievements.all_nba_first_team or 0 for p in players], dtype=float),
        'all_nba_second':   np.array([p.achievements.all_nba_second_team or 0 for p in players], dtype=float),
        'all_nba_third':    np.array([p.achievements.all_nba_third_team or 0 for p in players], dtype=float),
        'scoring_titles':   np.array([p.achievements.scoring_titles or 0 for p in players], dtype=float),
        'seasons_30ppg':    np.array([p.achievements.seasons_30ppg or 0 for p in players], dtype=float),
    }

    percentile_stats = {
        name: (stats.rankdata(values, method='average') / len(values)) * 100
        for name, values in all_stats.items()
    }

    scored_players = []

    for idx, player in enumerate(players):
        if not player.career_stats:
            continue

        p = percentile_stats  # shorthand

        # ── Offensive ────────────────────────────────────────────────────────
        is_guard = "Guard" in (player.position or "")
        if is_guard:
            offensive_score = (
                p['ppg'][idx]           * 0.40 +
                p['fg_pct'][idx]        * 0.10 +
                p['apg'][idx]           * 0.20 +
                p['total_points'][idx]  * 0.10 +
                p['scoring_titles'][idx]* 0.20
            )
        else:
            offensive_score = (
                p['ppg'][idx]           * 0.35 +
                p['fg_pct'][idx]        * 0.15 +
                p['apg'][idx]           * 0.15 +
                p['total_points'][idx]  * 0.15 +
                p['scoring_titles'][idx]* 0.20
            )

        # ── Defensive ────────────────────────────────────────────────────────
        if player.full_name == 'Bill Russell':
            defensive_score = 99.0
        elif is_guard:
            defensive_score = (
                p['spg'][idx] * 0.5 +
                p['bpg'][idx] * 0.1 +
                p['rpg'][idx] * 0.4
            )
        else:
            defensive_score = (
                p['spg'][idx] * 0.25 +
                p['bpg'][idx] * 0.35 +
                p['rpg'][idx] * 0.40
            )

        # ── Longevity ────────────────────────────────────────────────────────
        games_threshold = 30 if player.full_name == 'Bill Russell' else 40
        season_stats = sorted(player.season_stats, key=lambda s: s.season)
        complete_seasons = [s for s in season_stats if s.games_played >= games_threshold]

        if complete_seasons and player.full_name != 'Bill Russell':
            seasons_25plus = sum(1 for s in complete_seasons if s.points_per_game >= 25)
            seasons_20_25  = sum(1 for s in complete_seasons if 20 <= s.points_per_game < 25)
            seasons_under15 = sum(1 for i, s in enumerate(complete_seasons, 1)
                                  if s.points_per_game < 15 and i > 3)
            bonus_25plus = min(seasons_25plus, 5) * 2 + max(seasons_25plus - 5, 0)
            quality_bonus = bonus_25plus + seasons_20_25 - (seasons_under15 * 3)
            longevity_score = max(0.0, min(100.0, p['games'][idx] * 0.5 + quality_bonus))
        else:
            longevity_score = max(0.0, min(100.0, p['games'][idx] * 0.5))

        # ── Team success ─────────────────────────────────────────────────────
        base_team_success = (
            p['championships'][idx]    * 0.7 +
            p['finals_appearances'][idx] * 0.3
        )
        championships = player.achievements.championships or 0
        if championships >= 10:
            team_success_score = min(base_team_success * 2.0, 100.0)
        elif championships >= 4:
            team_success_score = min(base_team_success * 1.5, 100.0)
        else:
            team_success_score = base_team_success

        # ── Efficiency ───────────────────────────────────────────────────────
        efficiency_score = (
            (p['ppg'][idx] * (p['fg_pct'][idx] / 100)) * 0.70 +
            p['scoring_titles'][idx] * 0.30
        )

        # ── Individual success ───────────────────────────────────────────────
        individual_success_score = (
            p['mvp_awards'][idx]          * 0.25 +
            p['all_star_selections'][idx] * 0.10 +
            p['all_nba_first'][idx]       * 0.15 +
            p['all_nba_second'][idx]      * 0.08 +
            p['all_nba_third'][idx]       * 0.02 +
            p['scoring_titles'][idx]      * 0.20 +
            p['seasons_30ppg'][idx]       * 0.20
        )

        # ── Weighted total ───────────────────────────────────────────────────
        FLOOR = 0.10
        floored = {
            'offensive':        max(preferences['offensive_weight'],       FLOOR),
            'defensive':        max(preferences['defensive_weight'],       FLOOR),
            'longevity':        max(preferences['longevity_weight'],       FLOOR),
            'team_success':     max(preferences['team_success_weight'],    FLOOR),
            'efficiency':       max(preferences['efficiency_weight'],      FLOOR),
            'individual_success': max(preferences.get('peak_performance_weight', 0.5), FLOOR),
        }
        total_weight = sum(floored.values()) or 1.0
        w = {k: v / total_weight for k, v in floored.items()}

        total_score = (
            offensive_score         * w['offensive'] +
            defensive_score         * w['defensive'] +
            longevity_score         * w['longevity'] +
            team_success_score      * w['team_success'] +
            efficiency_score        * w['efficiency'] +
            individual_success_score * w['individual_success']
        )

        scored_players.append({
            'player': player.to_dict(),
            'score': total_score,
            'category_scores': {
                'offensive':          offensive_score,
                'defensive':          defensive_score,
                'longevity':          longevity_score,
                'team_success':       team_success_score,
                'efficiency':         efficiency_score,
                'individual_success': individual_success_score,
            },
            'career_stats':  player.career_stats.to_dict() if player.career_stats else {},
            'achievements':  player.achievements.to_dict() if player.achievements else {},
        })

    scored_players.sort(key=lambda x: x['score'], reverse=True)
    return scored_players[:100]
