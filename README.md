# Goat Simulator

A web application that determines NBA player greatness rankings based on user preferences. Users adjust sliders for what they value most in basketball greatness (offense, defense, championships, longevity, etc.), and the system returns a personalized ranking of the top 100 NBA players.

## Features

- **Interactive Questionnaire**: Auto-balancing sliders (always sum to 100%) for different aspects of greatness
- **Personalized Rankings**: Custom algorithm weights player stats based on user preferences
- **Comprehensive Database**: Player statistics, achievements, and career data
- **RESTful API**: JSON endpoints for player data and rankings
- **React Frontend**: TypeScript + Vite + Tailwind CSS

## Technology Stack

- **Backend**: Flask + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Data Source**: NBA API (`nba_api` Python wrapper)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Database**: SQLite (development) / PostgreSQL (production)

## Project Structure

```
NBA-Goat/
├── app.py                        # Flask app, routes, ranking algorithm
├── config.py                     # Database and app configuration
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not committed)
├── models/
│   ├── __init__.py               # Database initialization
│   ├── player.py                 # Player model
│   ├── stats.py                  # Career and season stats models
│   ├── achievements.py           # Achievements model
│   └── user_session.py           # User session tracking
├── data/
│   ├── nba_fetcher.py            # NBA API wrapper + sample data
│   ├── populate_db.py            # Seed database (sample or API mode)
│   ├── populate_season_stats.py  # Fetch season-by-season stats
│   ├── update_all_nba.py         # Update All-NBA / All-Defensive / scoring titles
│   ├── update_positions.py       # Update position, height, weight data
│   ├── update_30ppg_seasons.py   # Update 30+ PPG season counts
│   ├── update_finals_mvps.py     # Update Finals MVP counts
│   ├── update_dominant_championships.py  # Update dominant championship counts
│   ├── update_scoring_titles.py  # Update scoring title counts
│   ├── add_missing_legends.py    # Add Harden, Bill Russell, Dirk, Shaq
│   └── add_legends_batch.py      # Add Hakeem, Moses, Oscar, Wade, West, Westbrook, Isiah
├── frontend/                     # React + TypeScript frontend (Goat Simulator)
│   ├── src/
│   │   ├── api/client.ts         # API calls
│   │   ├── pages/                # Questions, Results, Home
│   │   ├── components/           # Navbar
│   │   └── types/                # TypeScript types
│   ├── vite.config.ts            # Vite config (proxies /api to Flask on :5001)
│   └── package.json
├── templates/                    # Legacy Jinja2 templates (fallback)
└── static/                       # Legacy static assets + React build output (dist/)
```

## Architecture Overview

- **Flask app (`app.py`)**: JSON API at `/api/*` for the React frontend, plus legacy Jinja2 routes for backwards compatibility. `calculate_player_rankings()` applies weighted, percentile-normalized scoring across all player stats.
- **Models (`models/`)**: SQLAlchemy models for players, career stats, season stats, achievements, and user sessions.
- **Data layer (`data/`)**: `nba_fetcher.py` wraps `nba_api`; `populate_db.py` seeds the DB. The `update_*` and `add_*` scripts patch specific fields after initial population.
- **Frontend (`frontend/`)**: React SPA served by Vite in development (proxied to Flask on port 5001). Built output goes to `static/dist/` for production.

## Data Flow

1. User visits `/questions` and adjusts preference sliders (auto-balance to 100%).
2. `POST /api/submit_preferences` computes rankings via `calculate_player_rankings()` and stores a `UserSession`.
3. Results are returned as JSON and displayed by the React frontend at `/results/<session_id>`.
4. The DB is seeded via `data/populate_db.py` and patched with the `update_*` / `add_*` scripts.

## Local Development Quickstart

**Backend:**
```bash
python3 -m venv nba_env
source nba_env/bin/activate
pip install -r requirements.txt

# Seed sample data
python data/populate_db.py --mode sample

# Run Flask on port 5001
python app.py
```

**Frontend (separate terminal):**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies `/api` requests to Flask on port 5001.

## Setup Instructions

### 1. Environment Setup

```bash
python3 -m venv nba_env
source nba_env/bin/activate   # macOS/Linux
# nba_env\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 2. Database Configuration

#### SQLite (Development)
No setup needed — the app creates `instance/nba_goat.db` automatically.

#### PostgreSQL (Production)
1. Install PostgreSQL and create the database: `createdb nba_goat`
2. Set `DATABASE_URL` in `.env`:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/nba_goat
```

### 3. Populate Database

```bash
# Quick sample data (5 players, for testing)
python data/populate_db.py --mode sample

# Full NBA API data (real players, takes ~30 min)
python data/populate_db.py --mode api

# After API population, run these to fill in missing fields:
python data/populate_season_stats.py
python data/update_all_nba.py
python data/update_positions.py
python data/update_30ppg_seasons.py
python data/update_finals_mvps.py
python data/update_dominant_championships.py
python data/update_scoring_titles.py
python data/add_missing_legends.py
python data/add_legends_batch.py
```

### 4. Run Application

```bash
# Backend
python app.py   # http://localhost:5001

# Frontend
cd frontend && npm run dev   # http://localhost:5173
```

## API Endpoints

- `GET /` — Serves React SPA (or legacy template if no build exists)
- `POST /api/submit_preferences` — Submit preferences, returns ranked players (JSON)
- `GET /api/players` — All players (JSON)
- `GET /api/player/<id>` — Single player detail (JSON)

## Ranking Algorithm

Players are scored on a 0–100 percentile scale across six categories:

1. **Offensive Skills** — PPG, FG%, APG, total points, scoring titles
2. **Defensive Skills** — SPG, BPG, RPG (position-adjusted)
3. **Team Success** — Championships (with multipliers for dynasties), Finals appearances
4. **Longevity** — Games played + quality longevity bonus (25+ PPG seasons rewarded, sub-15 PPG seasons penalized after year 3)
5. **Efficiency** — Scoring efficiency (PPG × FG%), scoring titles
6. **Peak Performance** — MVP awards, All-Star selections, All-NBA teams, scoring titles, 30+ PPG seasons

Weights for each category come from the user's slider inputs. All weights have a 10% floor so no category is fully ignored. Weights are normalized to sum to 1.0 before scoring.

Users can adjust the sliders — they auto-balance to always sum to 100% and cannot go below 0%.

## Development

### Modifying the Ranking Algorithm
Edit `calculate_player_rankings()` in `app.py`.

### Database Migrations
```bash
flask db migrate -m "description"
flask db upgrade
```

### Building for Production
```bash
cd frontend && npm run build
# Output goes to static/dist/ — Flask serves it automatically
```

## Environment Variables

```env
DATABASE_URL=sqlite:///nba_goat.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## License

This project is for educational purposes. NBA data is used under fair use guidelines.
