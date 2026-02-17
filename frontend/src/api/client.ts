import type { Preferences, SubmitPreferencesResponse } from '../types';

export async function submitPreferences(
  preferences: Preferences
): Promise<SubmitPreferencesResponse> {
  const response = await fetch('/api/submit_preferences', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(preferences),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || 'Failed to submit preferences');
  }

  return response.json();
}
