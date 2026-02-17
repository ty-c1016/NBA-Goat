export interface Player {
  id: number;
  full_name: string;
  position: string;
  from_year: number;
  to_year: number;
  is_active: boolean;
}

export interface CareerStats {
  points_per_game: number;
  rebounds_per_game: number;
  assists_per_game: number;
  field_goal_percentage: number;
  games_played: number;
  total_points: number;
}

export interface Achievements {
  championships: number;
  mvp_awards: number;
  all_star_selections: number;
  finals_appearances: number;
  all_nba_first_team: number;
  all_nba_second_team: number;
  all_nba_third_team: number;
  scoring_titles: number;
  seasons_30ppg: number;
  hall_of_fame: boolean;
}

export interface CategoryScores {
  offensive: number;
  defensive: number;
  longevity: number;
  team_success: number;
  efficiency: number;
  individual_success: number;
}

export interface RankedPlayer {
  player: Player;
  score: number;
  category_scores: CategoryScores;
  career_stats: CareerStats;
  achievements: Achievements;
}

export interface Preferences {
  offensive_weight: number;
  defensive_weight: number;
  longevity_weight: number;
  team_success_weight: number;
  efficiency_weight: number;
  peak_performance_weight: number;
  era_preference: 'any' | 'modern' | 'classic';
}

export interface SubmitPreferencesResponse {
  session_id: string;
  ranked_players: RankedPlayer[];
}
