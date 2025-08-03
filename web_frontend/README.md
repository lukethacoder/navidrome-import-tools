# Navidrome Import Tools - Web Frontend

A modern web interface for importing Spotify playlists and liked songs to M3U format or Lidarr.

## Features

- **Spotify Authentication**: Secure OAuth integration with Spotify
- **Playlist Management**: Fetch and export any Spotify playlist
- **Liked Songs Export**: Export your entire liked songs collection
- **M3U Generation**: Create playlist files compatible with media players
- **Lidarr Integration**: Automatically add albums to your Lidarr instance
- **Playlist Splitting**: Split large collections into manageable playlists
- **Real-time Progress**: Live updates during processing
- **Responsive Design**: Works on desktop and mobile devices

## Setup

### Prerequisites

1. Python 3.8 or higher
2. Spotify Developer Account
3. (Optional) Lidarr instance for automatic music management
4. (Optional) Navidrome database for M3U generation

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd spotify-migration/web_frontend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Copy `.env.example` to `.env` and configure:
   ```bash
   cp ../.env.example .env
   ```

   Edit `.env` with your credentials:
   ```env
   CLIENT_ID="your_spotify_client_id"
   CLIENT_SECRET="your_spotify_client_secret"
   REDIRECT_URI="http://localhost:5000/callback"
   LIDARR_URL="http://localhost:8686/api/v1"
   API_KEY="your_lidarr_api_key"
   ```

### Spotify App Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add `http://localhost:5000/callback` to Redirect URIs
4. Copy Client ID and Client Secret to your `.env` file

## Usage

### Starting the Application

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

### Basic Workflow

1. **Login**: Click "Login with Spotify" to authenticate
2. **Fetch Data**: 
   - Go to "Playlists" to export specific playlists
   - Go to "Liked Songs" to export your liked songs collection
3. **Choose Export Method**:
   - **Generate M3U**: Creates playlist files for media players
   - **Send to Lidarr**: Automatically adds albums to Lidarr
   - **Split Playlists**: (Liked songs only) Creates multiple smaller playlists

### Configuration

Visit the Settings page to configure:

- **Lidarr Settings**: URL, API key, and folder settings
- **Navidrome Settings**: Database path and music folder prefix

## API Endpoints

The web frontend provides several API endpoints:

- `GET /api/user-playlists` - Get user's playlists
- `POST /api/fetch-playlist` - Fetch playlist data
- `POST /api/fetch-liked-songs` - Fetch liked songs
- `POST /api/generate-m3u` - Generate M3U playlist
- `POST /api/send-to-lidarr` - Send to Lidarr
- `GET /download/<filename>` - Download generated files

## File Structure

```
web_frontend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── dashboard.html    # Main dashboard
│   ├── playlists.html    # Playlist management
│   ├── liked_songs.html  # Liked songs management
│   └── settings.html     # Configuration page
└── static/               # Static assets
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        ├── main.js       # Core JavaScript
        ├── playlists.js  # Playlist functionality
        ├── liked_songs.js # Liked songs functionality
        └── settings.js   # Settings functionality
```

## Integration with Existing Scripts

The web frontend integrates with the existing Python scripts:

- `fetch_spotify_playlist.py` - Playlist fetching logic
- `fetch_spotify_liked.py` - Liked songs fetching logic
- `spoti_playlist_to_m3u.py` - M3U generation
- `process_spotify_mb.py` - MusicBrainz processing
- `mb_lidarr_sync.py` - Lidarr synchronization
- `spotify_liked_chopper.py` - Playlist splitting

## Troubleshooting

### Common Issues

1. **"Not authenticated" errors**:
   - Make sure you've logged in with Spotify
   - Check that your Spotify app credentials are correct

2. **M3U generation fails**:
   - Ensure Navidrome database path is correct in Settings
   - Check that the database file is accessible

3. **Lidarr integration fails**:
   - Verify Lidarr URL and API key in Settings
   - Test the connection using the "Test Connection" button

4. **Import errors**:
   - Make sure all Python dependencies are installed
   - Ensure the parent directory scripts are accessible

### Logs

Check the console output where you started the Flask app for detailed error messages.

## Development

### Adding New Features

1. **Backend**: Add new routes in `app.py`
2. **Frontend**: Add new templates in `templates/`
3. **JavaScript**: Add functionality in `static/js/`
4. **Styles**: Modify `static/css/style.css`

### WebSocket Events

The application uses WebSocket for real-time updates:

- `progress` - Progress updates during processing
- `error` - Error messages
- `playlist_fetched` - Playlist data ready
- `liked_songs_fetched` - Liked songs data ready
- `m3u_generated` - M3U file generated
- `lidarr_complete` - Lidarr processing complete

## Security Notes

- The application uses session-based authentication
- Spotify tokens are stored in server-side sessions
- API keys should be kept secure in environment variables
- The application is intended for local/private use

## License

This project is licensed under the same terms as the parent repository.
