import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import type { Preferences } from '../types';
import { submitPreferences } from '../api/client';

ChartJS.register(ArcElement, Tooltip, Legend);

const CATEGORIES = [
  { key: 'offensive_weight', label: 'Offensive Skills', color: '#C9082A' },
  { key: 'defensive_weight', label: 'Defensive Skills', color: '#17408B' },
  { key: 'team_success_weight', label: 'Team Success', color: '#FFD700' },
  { key: 'longevity_weight', label: 'Career Longevity', color: '#4ECDC4' },
  { key: 'efficiency_weight', label: 'Statistical Efficiency', color: '#95E1D3' },
  { key: 'peak_performance_weight', label: 'Peak Performance', color: '#F38181' },
] as const;

type WeightKey = (typeof CATEGORIES)[number]['key'];

const DEFAULT_WEIGHTS: Record<WeightKey, number> = {
  offensive_weight: 17,
  defensive_weight: 17,
  team_success_weight: 17,
  longevity_weight: 17,
  efficiency_weight: 16,
  peak_performance_weight: 16,
};

export default function Questions() {
  const navigate = useNavigate();
  const [weights, setWeights] = useState<Record<WeightKey, number>>(DEFAULT_WEIGHTS);
  const [era, setEra] = useState<Preferences['era_preference']>('any');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const total = Object.values(weights).reduce((a, b) => a + b, 0);
  const isValid = total === 100;

  // Adjust last slider so total always stays at 100
  const handleSliderChange = useCallback(
    (changedKey: WeightKey, newValue: number) => {
      setWeights((prev) => {
        const otherKeys = CATEGORIES.map((c) => c.key).filter((k) => k !== changedKey);
        const otherTotal = otherKeys.reduce((s, k) => s + prev[k], 0);
        const remaining = 100 - newValue;

        if (otherTotal === 0) {
          // Distribute equally among others
          const share = Math.floor(remaining / otherKeys.length);
          const extra = remaining - share * otherKeys.length;
          const updated: Record<WeightKey, number> = { ...prev, [changedKey]: newValue };
          otherKeys.forEach((k, i) => {
            updated[k] = share + (i === 0 ? extra : 0);
          });
          return updated;
        }

        // Scale others proportionally
        const updated: Record<WeightKey, number> = { ...prev, [changedKey]: newValue };
        let allocated = 0;
        otherKeys.forEach((k, i) => {
          if (i < otherKeys.length - 1) {
            const scaled = Math.round((prev[k] / otherTotal) * remaining);
            updated[k] = scaled;
            allocated += scaled;
          } else {
            updated[k] = remaining - allocated;
          }
        });
        return updated;
      });
    },
    []
  );

  const handleSubmit = async () => {
    if (!isValid) return;
    setLoading(true);
    setError(null);
    try {
      const prefs: Preferences = {
        offensive_weight: weights.offensive_weight / 100,
        defensive_weight: weights.defensive_weight / 100,
        longevity_weight: weights.longevity_weight / 100,
        team_success_weight: weights.team_success_weight / 100,
        efficiency_weight: weights.efficiency_weight / 100,
        peak_performance_weight: weights.peak_performance_weight / 100,
        era_preference: era,
      };
      const result = await submitPreferences(prefs);
      navigate(`/results/${result.session_id}`, {
        state: { players: result.ranked_players, preferences: prefs },
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  const chartData = {
    labels: CATEGORIES.map((c) => c.label),
    datasets: [
      {
        data: CATEGORIES.map((c) => weights[c.key]),
        backgroundColor: CATEGORIES.map((c) => c.color),
        borderWidth: 2,
        borderColor: '#111827',
      },
    ],
  };

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-2">Set Your Preferences</h1>
        <p className="text-gray-400 text-center mb-10">
          Adjust the sliders so they add up to 100%. Each category influences your final rankings.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Sliders */}
          <div className="space-y-6">
            {CATEGORIES.map((cat) => (
              <div key={cat.key}>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-sm font-medium text-gray-200">{cat.label}</label>
                  <span
                    className="text-sm font-bold tabular-nums"
                    style={{ color: cat.color }}
                  >
                    {weights[cat.key]}%
                  </span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={weights[cat.key]}
                  onChange={(e) => handleSliderChange(cat.key, Number(e.target.value))}
                  className="w-full h-2 rounded-lg appearance-none cursor-pointer bg-gray-700"
                  style={{ accentColor: cat.color }}
                />
              </div>
            ))}

            {/* Era selector */}
            <div>
              <label className="block text-sm font-medium text-gray-200 mb-2">Era Preference</label>
              <select
                value={era}
                onChange={(e) => setEra(e.target.value as Preferences['era_preference'])}
                className="w-full bg-gray-800 border border-gray-700 text-gray-100 text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-nba-blue"
              >
                <option value="any">All Eras</option>
                <option value="modern">Modern (1980+)</option>
                <option value="classic">Classic (pre-1980)</option>
              </select>
            </div>

            {/* Total indicator */}
            <div
              className={`flex justify-between text-sm font-semibold px-3 py-2 rounded-lg ${
                isValid
                  ? 'bg-green-900/40 text-green-400 border border-green-800'
                  : 'bg-red-900/40 text-red-400 border border-red-800'
              }`}
            >
              <span>Total</span>
              <span>{total}% {isValid ? '✓' : `(need ${100 - total > 0 ? '+' : ''}${100 - total} more)`}</span>
            </div>

            {error && (
              <p className="text-red-400 text-sm bg-red-900/30 border border-red-800 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              onClick={handleSubmit}
              disabled={!isValid || loading}
              className="w-full bg-nba-red hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 rounded-lg transition-colors text-base"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  Calculating...
                </span>
              ) : (
                'Get My Rankings'
              )}
            </button>
          </div>

          {/* Pie chart */}
          <div className="flex flex-col items-center justify-center">
            <div className="w-72 h-72">
              <Pie
                data={chartData}
                options={{
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: { color: '#9CA3AF', font: { size: 11 }, padding: 12 },
                    },
                  },
                  animation: { duration: 200 },
                }}
              />
            </div>
            <p className="text-gray-500 text-xs mt-4 text-center">
              Your preference breakdown
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
