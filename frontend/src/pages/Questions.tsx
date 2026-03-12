import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import type { Preferences } from '../types';
import { submitPreferences } from '../api/client';

ChartJS.register(ArcElement, Tooltip, Legend);

const CATEGORIES = [
  { key: 'offensive_weight',        label: 'Offensive Skills',        color: '#7B5EA7', tip: 'PPG, FG%, APG, total points, scoring titles' },
  { key: 'defensive_weight',        label: 'Defensive Skills',        color: '#72B8D8', tip: 'RPG, BPG, SPG, defensive awards' },
  { key: 'team_success_weight',     label: 'Team Success',            color: '#5B3F87', tip: 'Championships, Finals appearances, team wins' },
  { key: 'longevity_weight',        label: 'Career Longevity',        color: '#4A96BA', tip: 'Games played, seasons, All-Star selections' },
  { key: 'efficiency_weight',       label: 'Statistical Efficiency',  color: '#B39DCC', tip: 'FG%, FT%, TS%, PER, win shares per 48' },
  { key: 'peak_performance_weight', label: 'Peak Performance',        color: '#BDE0F0', tip: 'MVP awards, All-NBA 1st team, best single seasons' },
] as const;

type WeightKey = (typeof CATEGORIES)[number]['key'];

const DEFAULT_WEIGHTS: Record<WeightKey, number> = {
  offensive_weight:       17,
  defensive_weight:       17,
  team_success_weight:    17,
  longevity_weight:       17,
  efficiency_weight:      16,
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

  const handleSliderChange = useCallback((changedKey: WeightKey, newValue: number) => {
    setWeights((prev) => {
      const otherKeys = CATEGORIES.map((c) => c.key).filter((k) => k !== changedKey);
      newValue = Math.max(0, Math.min(100, newValue));
      const otherTotal = otherKeys.reduce((s, k) => s + prev[k], 0);
      const remaining = 100 - newValue;

      if (otherTotal === 0) {
        const share = Math.floor(remaining / otherKeys.length);
        const extra = remaining - share * otherKeys.length;
        const updated: Record<WeightKey, number> = { ...prev, [changedKey]: newValue };
        otherKeys.forEach((k, i) => { updated[k] = share + (i === 0 ? extra : 0); });
        return updated;
      }

      const updated: Record<WeightKey, number> = { ...prev, [changedKey]: newValue };
      let allocated = 0;
      otherKeys.forEach((k, i) => {
        if (i < otherKeys.length - 1) {
          const scaled = Math.max(0, Math.round((prev[k] / otherTotal) * remaining));
          updated[k] = scaled;
          allocated += scaled;
        } else {
          updated[k] = Math.max(0, remaining - allocated);
        }
      });
      return updated;
    });
  }, []);

  const handleSubmit = async () => {
    if (!isValid) return;
    setLoading(true);
    setError(null);
    try {
      const prefs: Preferences = {
        offensive_weight:        weights.offensive_weight / 100,
        defensive_weight:        weights.defensive_weight / 100,
        longevity_weight:        weights.longevity_weight / 100,
        team_success_weight:     weights.team_success_weight / 100,
        efficiency_weight:       weights.efficiency_weight / 100,
        peak_performance_weight: weights.peak_performance_weight / 100,
        era_preference:          era,
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
    datasets: [{
      data: CATEGORIES.map((c) => weights[c.key]),
      backgroundColor: CATEGORIES.map((c) => c.color),
      borderWidth: 2,
      borderColor: '#FFFFFF',
    }],
  };

  return (
    <div className="min-h-screen bg-canvas py-12 px-4">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-ink mb-2">Set Your Preferences</h1>
        <p className="text-muted text-center text-sm mb-10">
          Adjust the sliders — they auto-balance to 100%. Each category influences your final rankings.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Sliders */}
          <div className="bg-surface border border-rim rounded-2xl p-6 shadow-sm space-y-5">
            {CATEGORIES.map((cat) => (
              <div key={cat.key}>
                <div className="flex justify-between items-center mb-1.5">
                  <label htmlFor={cat.key} className="text-sm font-medium text-ink flex items-center gap-1.5">
                    {cat.label}
                    <span
                      className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-rim text-muted text-[10px] font-bold cursor-help shrink-0"
                      title={cat.tip}
                    >
                      ?
                    </span>
                  </label>
                  <span className="text-sm font-bold tabular-nums" style={{ color: cat.color }}>
                    {weights[cat.key]}%
                  </span>
                </div>
                <input
                  id={cat.key}
                  type="range"
                  min={0}
                  max={100}
                  value={weights[cat.key]}
                  onChange={(e) => handleSliderChange(cat.key, Number(e.target.value))}
                  aria-label={cat.label}
                  className="w-full h-2 rounded-lg appearance-none cursor-pointer"
                  style={{ accentColor: cat.color }}
                />
              </div>
            ))}

            {/* Era selector */}
            <div>
              <label htmlFor="era_preference" className="block text-sm font-medium text-ink mb-1.5">Era Preference</label>
              <select
                id="era_preference"
                value={era}
                onChange={(e) => setEra(e.target.value as Preferences['era_preference'])}
                aria-label="Era Preference"
                className="w-full bg-canvas border border-rim text-ink text-sm rounded-lg px-3 py-2 focus:outline-none focus:border-purple"
              >
                <option value="any">All Eras</option>
                <option value="modern">Modern (1980+)</option>
                <option value="classic">Classic (pre-1980)</option>
              </select>
            </div>

            {/* Total indicator */}
            <div className={`flex justify-between text-sm font-semibold px-3 py-2 rounded-lg border ${
              isValid
                ? 'bg-sky-subtle text-sky-dark border-sky-light'
                : 'bg-red-50 text-red-600 border-red-200'
            }`}>
              <span>Total</span>
              <span>
                {total}%{' '}
                {isValid ? '✓' : `(${100 - total > 0 ? '+' : ''}${100 - total} needed)`}
              </span>
            </div>

            {error && (
              <p className="text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                {error}
              </p>
            )}

            <button
              onClick={handleSubmit}
              disabled={!isValid || loading}
              className="w-full bg-purple hover:bg-purple-dark disabled:opacity-40 disabled:cursor-not-allowed text-white font-bold py-3 rounded-xl transition-colors text-base shadow-sm"
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
          <div className="flex flex-col items-center justify-center bg-surface border border-rim rounded-2xl p-6 shadow-sm">
            <div className="w-72 h-72">
              <Pie
                data={chartData}
                options={{
                  plugins: {
                    legend: {
                      position: 'bottom',
                      labels: {
                        color: '#56516B',
                        font: { size: 11 },
                        padding: 12,
                      },
                    },
                  },
                  animation: { duration: 200 },
                }}
              />
            </div>
            <p className="text-muted text-xs mt-4 text-center">Your preference breakdown</p>
          </div>
        </div>
      </div>
    </div>
  );
}
