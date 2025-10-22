# NBA GOAT Analyzer

A web application that determines NBA player greatness rankings based on user preferences. Users answer questions about what they value most in basketball greatness (offense, defense, championships, longevity, etc.), and the system returns a personalized ranking of the top 100 NBA players.

## Features

- **Interactive Questionnaire**: Adjustable sliders for different aspects of greatness
- **Personalized Rankings**: Custom algorithm weights player stats based on user preferences
- **Comprehensive Database**: Player statistics, achievements, and career data
- **RESTful API**: JSON endpoints for player data and rankings
- **Responsive Design**: Bootstrap-powered UI that works on all devices

## Technology Stack

- **Backend**: Flask + SQLAlchemy + PostgreSQL/SQLite
- **Data Source**: NBA API (nba_api Python wrapper)
- **Frontend**: HTML/CSS/JavaScript + Bootstrap 5
- **Database**: PostgreSQL (production) / SQLite (development)

## Project Structure

```
NBA_goat/
├── app.py                 # Main Flask application
├── config.py              # Database and app configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not committed)
├── models/
│   ├── __init__.py        # Database initialization
│   ├── player.py          # Player model
│   ├── stats.py           # Statistics models
│   ├── achievements.py    # Achievements model
│   └── user_session.py    # User session tracking
├── data/
│   ├── nba_fetcher.py     # NBA API data fetching
│   └── populate_db.py     # Database population script
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── questions.html     # Questionnaire
│   └── results.html       # Results display
└── static/
    ├── css/style.css      # Custom styles
    └── js/app.js          # Interactive features
```

## Architecture Overview

- **Flask app (`app.py`)**: Defines routes for UI pages and JSON APIs. Uses `calculate_player_rankings()` for a simple weighted scoring of players based on user preferences.
- **Models (`models/`)**: SQLAlchemy models for players, stats, achievements, and user sessions. `models/__init__.py` initializes `db` and `migrate`.
- **Data layer (`data/`)**: `nba_fetcher.py` wraps `nba_api` calls and provides sample data; `populate_db.py` seeds the database using either sample data or real API data.
- **Templates (`templates/`)**: Jinja templates for base layout, questionnaire, and results.
- **Static assets (`static/`)**: CSS and JS that enhance UI interactions.

## Data Flow

1. User visits `/questions` and submits preference weights.
2. `POST /submit_preferences` stores a `UserSession` and computes rankings via `calculate_player_rankings()`.
3. The results are saved to the session record and displayed at `/results/<session_id>`.
4. Data in the DB is populated via `data/populate_db.py` using either sample fixtures or the NBA API wrapper.

## Local Development Quickstart

```bash
python3 -m venv nba_env
source nba_env/bin/activate
pip install -r requirements.txt

# Seed sample data
python data/populate_db.py --mode sample

# Run the app
python app.py
```

App runs at `http://localhost:5000`.

## Setup Instructions

### 1. Environment Setup

```bash
# Clone/navigate to project directory
cd NBA_goat

# Create virtual environment
python3 -m venv nba_env

# Activate virtual environment
source nba_env/bin/activate  # On macOS/Linux
# nba_env\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

The application supports both PostgreSQL (recommended for production) and SQLite (for development).

#### For SQLite (Development)
No additional setup required. The app will create `nba_goat.db` automatically.

#### For PostgreSQL (Production)
1. Install PostgreSQL
2. Create database: `createdb nba_goat`
3. Update `.env` file with your database credentials:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/nba_goat
```

### 3. Populate Database

```bash
# Populate with sample data (for quick testing)
python data/populate_db.py --mode sample

# OR populate with real NBA API data (takes longer)
python data/populate_db.py --mode api
```

### 4. Run Application

```bash
# Start the Flask development server
python app.py

# Application will be available at http://localhost:5000
```

## API Endpoints

- `GET /` - Homepage
- `GET /questions` - Questionnaire form
- `POST /submit_preferences` - Submit user preferences and calculate rankings
- `GET /results/<session_id>` - View ranking results
- `GET /api/players` - Get all players (JSON)
- `GET /api/player/<id>` - Get specific player details (JSON)

## Database Schema

### Players Table
- Basic player information (name, position, height, weight, years active)

### Career Stats Table
- Career averages and totals (PPG, RPG, APG, FG%, etc.)

### Advanced Stats Table
- Advanced metrics (PER, TS%, BPM, VORP, etc.)

### Achievements Table
- Championships, MVP awards, All-Star selections, Hall of Fame status

### User Sessions Table
- User preferences and generated rankings

## Ranking Algorithm

The application uses a weighted scoring system that considers:

1. **Offensive Skills** (Scoring, shooting efficiency, playmaking)
2. **Defensive Skills** (Steals, blocks, defensive impact)
3. **Team Success** (Championships, Finals appearances)
4. **Longevity** (Games played, seasons, sustained excellence)
5. **Efficiency** (Advanced metrics, per-minute production)
6. **Peak Performance** (Best seasons, MVP awards, dominance)

Users can adjust the importance of each factor via interactive sliders.

## Development

### Adding New Players
```bash
# Update database with latest player data
python data/populate_db.py --mode api
```

### Modifying Ranking Algorithm
Edit the `calculate_player_rankings()` function in `app.py` to adjust how different statistics are weighted and combined.

### Database Migrations
For schema changes, use Flask-Migrate:
```bash
flask db init
flask db migrate -m "Description of changes"
flask db upgrade
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=sqlite:///nba_goat.db
# OR for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/nba_goat

# Flask
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Future Enhancements

- [ ] Player comparison tool
- [ ] Advanced filtering options
- [ ] Data visualizations and charts
- [ ] Export rankings to PDF/CSV
- [ ] Historical era adjustments
- [ ] Machine learning-based predictions
- [ ] Social sharing features
- [ ] User accounts and saved preferences

## License

This project is for educational purposes. NBA data is used under fair use guidelines.