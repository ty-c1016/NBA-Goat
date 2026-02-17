import { useParams, useLocation, Navigate, Link } from 'react-router-dom';
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
  offensive_weight: 'Offense',
  defensive_weight: 'Defense',
  team_success_weight: 'Team Success',
  longevity_weight: 'Longevity',
  efficiency_weight: 'Efficiency',
  peak_performance_weight: 'Peak Perf.',
};

function scoreColor(score: number): string {
  if (score >= 80) return 'text-yellow-400';
  if (score >= 65) return 'text-green-400';
  if (score >= 50) return 'text-blue-400';
  return 'text-gray-400';
}

export default function Results() {
  useParams<{ sessionId: string }>();
  const location = useLocation();
  const state = location.state as LocationState | undefined;

  if (!state?.players) {
    return <Navigate to="/questions" replace />;
  }

  const { players, preferences } = state;

  return (
    <div className="min-h-screen py-10 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-1">Your NBA GOAT Rankings</h1>
          <p className="text-gray-400 text-sm">Based on your personalized preferences</p>
        </div>

        {/* Preference summary */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-8">
          <p className="text-xs text-gray-500 uppercase font-semibold mb-3">Your Weights</p>
          <div className="flex flex-wrap gap-3">
            {(Object.keys(PREF_LABELS) as (keyof typeof PREF_LABELS)[]).map((key) => (
              <span
                key={key}
                className="bg-gray-800 text-gray-200 text-xs font-medium px-3 py-1 rounded-full"
              >
                {PREF_LABELS[key]}: {Math.round(preferences[key] * 100)}%
              </span>
            ))}
            <span className="bg-nba-blue/30 text-blue-300 text-xs font-medium px-3 py-1 rounded-full capitalize">
              Era: {preferences.era_preference === 'any' ? 'All Eras' : preferences.era_preference}
            </span>
          </div>
        </div>

        {/* Top 3 spotlight */}
        {players.length >= 3 && (
          <div className="grid grid-cols-3 gap-4 mb-8">
            {[1, 0, 2].map((i) => {
              const p = players[i];
              const rank = i + 1;
              const isFirst = i === 0;
              return (
                <div
                  key={p.player.id}
                  className={`bg-gray-900 border rounded-xl p-4 text-center ${
                    isFirst
                      ? 'border-yellow-500/50 ring-1 ring-yellow-500/30 order-first sm:order-none'
                      : 'border-gray-800'
                  }`}
                  style={{ order: i === 0 ? -1 : i === 1 ? 0 : 1 }}
                >
                  <div className="text-2xl mb-1">{rank === 1 ? '🏆' : rank === 2 ? '🥈' : '🥉'}</div>
                  <div className="text-xs text-gray-500 mb-1">#{rank}</div>
                  <div className={`font-bold text-sm sm:text-base mb-1 ${isFirst ? 'text-yellow-300' : 'text-white'}`}>
                    {p.player.full_name}
                  </div>
                  <div className="text-gray-400 text-xs mb-2">{p.player.position}</div>
                  <div className={`text-2xl font-extrabold ${scoreColor(p.score)}`}>
                    {fmt(p.score)}
                  </div>
                  <div className="text-gray-500 text-xs">GOAT Score</div>
                </div>
              );
            })}
          </div>
        )}

        {/* Full table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-800 text-gray-400 text-xs uppercase">
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
                {players.map((p, i) => (
                  <tr
                    key={p.player.id}
                    className="border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors"
                  >
                    <td className="px-4 py-3 text-gray-500 font-mono text-xs">{i + 1}</td>
                    <td className="px-4 py-3">
                      <div className="font-semibold text-white">{p.player.full_name}</div>
                      <div className="text-gray-500 text-xs sm:hidden">{p.player.position}</div>
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400 hidden sm:table-cell text-xs">
                      {p.player.position}
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400 hidden md:table-cell text-xs">
                      {p.player.from_year}–{p.player.to_year}
                    </td>
                    <td className="px-4 py-3 text-center text-gray-200 font-medium">
                      {fmt(p.career_stats?.points_per_game)}
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400 hidden sm:table-cell">
                      {fmt(p.career_stats?.rebounds_per_game)}
                    </td>
                    <td className="px-4 py-3 text-center text-gray-400 hidden sm:table-cell">
                      {fmt(p.career_stats?.assists_per_game)}
                    </td>
                    <td className="px-4 py-3 text-center hidden md:table-cell">
                      {p.achievements?.championships > 0 ? (
                        <span className="text-yellow-400 font-bold">{p.achievements.championships}</span>
                      ) : (
                        <span className="text-gray-600">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`font-bold ${scoreColor(p.score)}`}>
                        {fmt(p.score)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4 justify-center mt-8">
          <Link
            to="/questions"
            className="bg-nba-red hover:bg-red-700 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors"
          >
            Try Different Preferences
          </Link>
          <Link
            to="/"
            className="border border-gray-700 hover:border-gray-500 text-gray-300 font-semibold px-6 py-2.5 rounded-lg transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
