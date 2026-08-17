# RockMyRun

AI-powered music discovery and playlist generation for runners.

## Features

- Search for songs by title and artist
- Connect a Spotify account
- Import Spotify playlists
- Maintain a local song database
- Calculate custom scores:
  - Hype
  - Energy
  - Motivation
- Build reusable running vibe profiles
- Generate playlists tailored to workout progression
- Visualize playlist characteristics with interactive charts

## How It Works

User Input -> Spotify Search / Playlist Import -> Audio Features -> Custom Scoring -> Recommendation Engine -> Running Playlist

## Spotify Integration

### Client Credentials Flow

Used for:
- Song discovery
- Title/artist searches
- Resolving Spotify track IDs

### User OAuth Flow

Used for:
- Reading user playlists
- Creating playlists
- Updating playlists

## Technology Stack

### Backend
- Python
- Flask
- SQLAlchemy
- SQLite
- Spotipy

### Data Science
- NumPy
- Pandas
- scikit-learn

### Frontend
- HTML
- CSS
- JavaScript
- Chart.js

### Deployment
- Railway
- Gunicorn

## Project Goal

Put the right song at the right point in a run.

## Author

Krista Smith
PhD Bioinformatics | Data Scientist | Software Engineer
