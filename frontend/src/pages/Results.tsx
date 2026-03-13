import { useParams, useLocation, Navigate, Link } from 'react-router-dom';
import { useMemo, useState } from 'react';
import type { RankedPlayer, Preferences } from '../types';

interface LocationState {
  players: RankedPlayer[];
  preferences: Preferences;
}

function fmt(n: number | undefined | null, decimals = 1): string {
  if (n == null) return '—';
  return n.toFixed(decimals);
}

const PREF_LABELS: Record<keyof Omit<Preferences, 'era_preference'>, string> = {
  offensive_weight:        'Offense',
  defensive_weight:        'Defense',
  team_success_weight:     'Team Success',
  longevity_weight:        'Longevity',
  efficiency_weight:       'Efficiency',
  peak_performance_weight: 'Peak Perf.',
};

const CATEGORY_LABELS: Record<string, string> = {
  offensive:           'Offense',
  defensive:           'Defense',
  longevity:           'Longevity',
  team_success:        'Team Success',
  efficiency:          'Efficiency',
  individual_success:  'Peak Perf.',
};

const CATEGORY_COLORS: Record<string, string> = {
  offensive:           'bg-purple',
  defensive:           'bg-sky-dark',
  longevity:           'bg-purple-light',
  team_success:        'bg-purple-dark',
  efficiency:          'bg-sky-light',
  individual_success:  'bg-purple/60',
};

function scoreColor(score: number): string {
  if (score >= 80) return 'text-purple font-extrabold';
  if (score >= 65) return 'text-sky-dark font-bold';
  if (score >= 50) return 'text-purple-light font-semibold';
  return 'text-muted';
}

const PODIUM_META = [
  { rank: 1, emoji: '🏆', border: 'border-purple/40 ring-1 ring-purple/20', nameColor: 'text-purple' },
  { rank: 2, emoji: '🥈', border: 'border-rim',                          nameColor: 'text-ink' },
  { rank: 3, emoji: '🥉', border: 'border-rim',                          nameColor: 'text-ink' },
];

export default function Results() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const location = useLocation();
  const routerState = location.state as LocationState | undefined;
  const [expandedRow, setExpandedRow] = useState<number | null>(null);
  const toggleRow = (id: number) => setExpandedRow(prev => prev === id ? null : id);

  const state = useMemo<LocationState | null>(() => {
    if (routerState?.players) {
      if (sessionId) {
        sessionStorage.setItem(
          `results_${sessionId}`,
          JSON.stringify({ players: routerState.players, preferences: routerState.preferences })
        );
      }
      return routerState;
    }
    if (sessionId) {
      const cached = sessionStorage.getItem(`results_${sessionId}`);
      if (cached) {
        try { return JSON.parse(cached) as LocationState; } catch { /* ignore */ }
      }
    }
    return null;
  }, [routerState, sessionId]);

  if (!state?.players) {
    return <Navigate to="/questions" replace />;
  }

  const { players, preferences } = state;

  if (players.length === 0) {
    return (
      <div className="min-h-screen bg-canvas py-10 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h1 className="text-3xl font-bold text-ink mb-4">No Players Found</h1>
          <p className="text-muted mb-8">
            No players matched your criteria. Try adjusting your preferences.
          </p>
          <Link
            to="/questions"
            className="bg-purple hover:bg-purple-dark text-white font-semibold px-6 py-2.5 rounded-xl transition-colors shadow-sm"
          >
            Try Different Preferences
          </Link>
        </div>
      </div>
    );
  }

  // Podium order: 2nd, 1st, 3rd
  const podiumOrder = [1, 0, 2];

  return (
    <div className="min-h-screen bg-canvas py-10 px-4">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-ink mb-1">Your NBA GOAT Rankings</h1>
          <p className="text-muted text-sm">Based on your personalized preferences</p>
        </div>

        {/* Preference summary */}
        <div className="bg-surface border border-rim rounded-2xl p-4 mb-8 shadow-sm">
          <p className="text-xs text-muted uppercase font-semibold tracking-wide mb-3">Your Weights</p>
          <div className="flex flex-wrap gap-2">
            {(Object.keys(PREF_LABELS) as (keyof typeof PREF_LABELS)[]).map((key) => (
              <span
                key={key}
                className="bg-purple-subtle text-purple text-xs font-medium px-3 py-1 rounded-full border border-purple/20"
              >
                {PREF_LABELS[key]}: {Math.round(preferences[key] * 100)}%
              </span>
            ))}
            <span className="bg-sky-subtle text-sky-dark text-xs font-medium px-3 py-1 rounded-full border border-sky-light capitalize">
              Era: {preferences.era_preference === 'any' ? 'All Eras' : preferences.era_preference}
            </span>
          </div>
        </div>

        {/* Top 3 podium */}
        {players.length >= 3 && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            {podiumOrder.map((playerIdx) => {
              const p = players[playerIdx];
              const meta = PODIUM_META[playerIdx];
              return (
                <div
                  key={p.player.id}
                  className={`bg-surface border rounded-2xl p-4 text-center shadow-sm ${meta.border}`}
                >
                  <div className="text-2xl mb-1">{meta.emoji}</div>
                  <div className="text-xs text-muted mb-1">#{meta.rank}</div>
                  <div className={`font-bold text-sm sm:text-base mb-1 ${meta.nameColor}`}>
                    {p.player.full_name}
                  </div>
                  <div className="text-muted text-xs mb-3">{p.player.position}</div>
                  <div className={`text-2xl ${scoreColor(p.score)}`}>
                    {fmt(p.score)}
                  </div>
                  <div className="text-muted text-xs">GOAT Score</div>
                </div>
              );
            })}
          </div>
        )}

        {/* Podium fallback for 1-2 players */}
        {players.length > 0 && players.length < 3 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
            {players.map((p, i) => {
              const meta = PODIUM_META[i];
              return (
                <div
                  key={p.player.id}
                  className={`bg-surface border rounded-2xl p-4 text-center shadow-sm ${meta.border}`}
                >
                  <div className="text-2xl mb-1">{meta.emoji}</div>
                  <div className="text-xs text-muted mb-1">#{meta.rank}</div>
                  <div className={`font-bold text-sm sm:text-base mb-1 ${meta.nameColor}`}>
                    {p.player.full_name}
                  </div>
                  <div className="text-muted text-xs mb-3">{p.player.position}</div>
                  <div className={`text-2xl ${scoreColor(p.score)}`}>
                    {fmt(p.score)}
                  </div>
                  <div className="text-muted text-xs">GOAT Score</div>
                </div>
              );
            })}
          </div>
        )}

        {/* Category score breakdown */}
        {players.length > 0 && players[0].category_scores && (
          <div className="bg-surface border border-rim rounded-2xl p-4 mb-8 shadow-sm">
            <p className="text-xs text-muted uppercase font-semibold tracking-wide mb-4">Category Breakdown — Top {Math.min(players.length, 5)}</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-rim text-muted text-xs uppercase tracking-wide">
                    <th className="px-3 py-2 text-left">Player</th>
                    {Object.keys(CATEGORY_LABELS).map((key) => (
                      <th key={key} className="px-3 py-2 text-center">{CATEGORY_LABELS[key]}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {players.slice(0, 5).map((p) => (
                    <tr key={p.player.id} className="border-b border-rim/50">
                      <td className="px-3 py-2 font-semibold text-ink whitespace-nowrap">{p.player.full_name}</td>
                      {Object.keys(CATEGORY_LABELS).map((key) => {
                        const val = p.category_scores?.[key as keyof typeof p.category_scores];
                        return (
                          <td key={key} className="px-3 py-2">
                            <div className="flex items-center gap-2">
                              <div className="flex-1 h-2 bg-canvas rounded-full overflow-hidden min-w-[40px]">
                                <div
                                  className={`h-full rounded-full ${CATEGORY_COLORS[key] || 'bg-purple'}`}
                                  style={{ width: `${Math.max(0, Math.min(100, val ?? 0))}%` }}
                                />
                              </div>
                              <span className="text-xs text-muted tabular-nums w-8 text-right">{fmt(val)}</span>
                            </div>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Full rankings table */}
        <div className="bg-surface border border-rim rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-rim bg-purple-subtle text-muted text-xs uppercase tracking-wide">
                  <th className="px-4 py-3 text-left w-10">#</th>
                  <th className="px-4 py-3 text-left">Player</th>
                  <th className="px-4 py-3 text-center hidden sm:table-cell">Pos</th>
                  <th className="px-4 py-3 text-center hidden md:table-cell">Years</th>
                  <th className="px-4 py-3 text-center">PPG</th>
                  <th className="px-4 py-3 text-center hidden sm:table-cell">RPG</th>
                  <th className="px-4 py-3 text-center hidden sm:table-cell">APG</th>
                  <th className="px-4 py-3 text-center hidden md:table-cell">Rings</th>
                  <th className="px-4 py-3 text-center">Score</th>
                </tr>
              </thead>
              <tbody>
                {players.map((p, i) => {
                  const isExpanded = expandedRow === p.player.id;
                  return (
                    <>
                      <tr
                        key={p.player.id}
                        onClick={() => toggleRow(p.player.id)}
                        className="border-b border-rim/50 hover:bg-purple-subtle/40 transition-colors cursor-pointer select-none"
                      >
                        <td className="px-4 py-3 text-muted font-mono text-xs">{i + 1}</td>
                        <td className="px-4 py-3">
                          <div className="font-semibold text-ink">{p.player.full_name}</div>
                          <div className="text-muted text-xs sm:hidden">{p.player.position}</div>
                        </td>
                        <td className="px-4 py-3 text-center text-muted hidden sm:table-cell text-xs">
                          {p.player.position}
                        </td>
                        <td className="px-4 py-3 text-center text-muted hidden md:table-cell text-xs">
                          {p.player.from_year}–{p.player.to_year}
                        </td>
                        <td className="px-4 py-3 text-center text-ink font-medium">
                          {fmt(p.career_stats?.points_per_game)}
                        </td>
                        <td className="px-4 py-3 text-center text-muted hidden sm:table-cell">
                          {fmt(p.career_stats?.rebounds_per_game)}
                        </td>
                        <td className="px-4 py-3 text-center text-muted hidden sm:table-cell">
                          {fmt(p.career_stats?.assists_per_game)}
                        </td>
                        <td className="px-4 py-3 text-center hidden md:table-cell">
                          {p.achievements?.championships > 0 ? (
                            <span className="text-purple font-bold">{p.achievements.championships}</span>
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <span className={scoreColor(p.score)}>{fmt(p.score)}</span>
                            <span className={`text-muted text-xs transition-transform duration-200 inline-block ${isExpanded ? 'rotate-180' : ''}`}>▼</span>
                          </div>
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr key={`${p.player.id}-expanded`} className="border-b border-rim bg-canvas">
                          <td colSpan={9} className="px-4 py-4">
                            <div className="flex flex-col sm:flex-row gap-6">
                              {/* Score breakdown */}
                              <div className="flex-1">
                                <p className="text-xs text-muted uppercase font-semibold tracking-wide mb-3">Score Breakdown</p>
                                <div className="space-y-2">
                                  {Object.keys(CATEGORY_LABELS).map((key) => {
                                    const val = p.category_scores?.[key as keyof typeof p.category_scores] ?? 0;
                                    return (
                                      <div key={key} className="flex items-center gap-2">
                                        <span className="text-xs text-muted w-24 shrink-0">{CATEGORY_LABELS[key]}</span>
                                        <div className="flex-1 h-2 bg-surface rounded-full overflow-hidden">
                                          <div
                                            className={`h-full rounded-full ${CATEGORY_COLORS[key] || 'bg-purple'}`}
                                            style={{ width: `${Math.max(0, Math.min(100, val))}%` }}
                                          />
                                        </div>
                                        <span className="text-xs text-muted tabular-nums w-8 text-right">{fmt(val)}</span>
                                      </div>
                                    );
                                  })}
                                </div>
                              </div>
                              {/* Achievements */}
                              <div className="sm:w-56">
                                <p className="text-xs text-muted uppercase font-semibold tracking-wide mb-3">Achievements</p>
                                <div className="flex flex-wrap gap-2">
                                  {(p.achievements?.championships ?? 0) > 0 && (
                                    <span className="bg-purple-subtle border border-purple/20 text-purple text-xs font-medium px-2.5 py-1 rounded-full">
                                      🏆 {p.achievements.championships} Ring{p.achievements.championships !== 1 ? 's' : ''}
                                    </span>
                                  )}
                                  {(p.achievements?.mvp_awards ?? 0) > 0 && (
                                    <span className="bg-purple-subtle border border-purple/20 text-purple text-xs font-medium px-2.5 py-1 rounded-full">
                                      MVP ×{p.achievements.mvp_awards}
                                    </span>
                                  )}
                                  {(p.achievements?.all_star_selections ?? 0) > 0 && (
                                    <span className="bg-sky-subtle border border-sky-light text-sky-dark text-xs font-medium px-2.5 py-1 rounded-full">
                                      ⭐ {p.achievements.all_star_selections}× All-Star
                                    </span>
                                  )}
                                  {(p.achievements?.finals_appearances ?? 0) > 0 && (
                                    <span className="bg-surface border border-rim text-muted text-xs font-medium px-2.5 py-1 rounded-full">
                                      {p.achievements.finals_appearances}× Finals
                                    </span>
                                  )}
                                  {(p.achievements?.all_nba_first_team ?? 0) > 0 && (
                                    <span className="bg-surface border border-rim text-muted text-xs font-medium px-2.5 py-1 rounded-full">
                                      All-NBA 1st ×{p.achievements.all_nba_first_team}
                                    </span>
                                  )}
                                  {(p.achievements?.scoring_titles ?? 0) > 0 && (
                                    <span className="bg-surface border border-rim text-muted text-xs font-medium px-2.5 py-1 rounded-full">
                                      🎯 {p.achievements.scoring_titles} Scoring Title{p.achievements.scoring_titles !== 1 ? 's' : ''}
                                    </span>
                                  )}
                                  {(p.achievements?.seasons_30ppg ?? 0) > 0 && (
                                    <span className="bg-surface border border-rim text-muted text-xs font-medium px-2.5 py-1 rounded-full">
                                      {p.achievements.seasons_30ppg}× 30+ PPG Season{p.achievements.seasons_30ppg !== 1 ? 's' : ''}
                                    </span>
                                  )}
                                  {p.achievements?.hall_of_fame && (
                                    <span className="bg-purple-subtle border border-purple/20 text-purple text-xs font-medium px-2.5 py-1 rounded-full">
                                      Hall of Fame
                                    </span>
                                  )}
                                </div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8">
          <Link
            to="/questions"
            className="bg-purple hover:bg-purple-dark text-white font-semibold px-6 py-2.5 rounded-xl transition-colors shadow-sm"
          >
            Try Different Preferences
          </Link>
          <Link
            to="/"
            className="border border-rim hover:border-purple-light text-muted hover:text-ink font-semibold px-6 py-2.5 rounded-xl transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
