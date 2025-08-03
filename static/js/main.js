// Main JavaScript for Spotify Migration Tool
class SpotifyMigrationApp {
    constructor() {
        this.socket = null;
        this.currentTempFile = null;
        this.currentPlaylistName = null;
        this.init();
    }

    init() {
        this.initSocket();
        this.bindEvents();
    }

    initSocket() {
        this.socket = io();
        
        this.socket.on('progress', (data) => {
            this.updateProgress(data.message, data.progress);
        });

        this.socket.on('error', (data) => {
            this.hideProgress();
            this.showError(data.message);
        });

        this.socket.on('playlist_fetched', (data) => {
            this.hideProgress();
            this.handlePlaylistFetched(data);
        });

        this.socket.on('liked_songs_fetched', (data) => {
            this.hideProgress();
            this.handleLikedSongsFetched(data);
        });

        this.socket.on('m3u_generated', (data) => {
            this.hideProgress();
            this.handleM3UGenerated(data);
        });

        this.socket.on('lidarr_complete', (data) => {
            this.hideProgress();
            this.handleLidarrComplete(data);
        });
    }

    bindEvents() {
        // Global error handling
        window.addEventListener('error', (e) => {
            console.error('JavaScript error:', e.error);
        });

        // Handle form submissions
        document.addEventListener('submit', (e) => {
            e.preventDefault();
        });
    }

    // Progress handling
    showProgress(title = 'Processing...') {
        const modal = document.getElementById('progressModal');
        const titleElement = modal.querySelector('.modal-title');
        const progressBar = modal.querySelector('.progress-bar');
        const messageElement = document.getElementById('progress-message');
        const closeButton = document.getElementById('close-progress');

        titleElement.textContent = title;
        progressBar.style.width = '0%';
        messageElement.textContent = 'Starting...';
        closeButton.style.display = 'none';

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    updateProgress(message, progress) {
        const progressBar = document.querySelector('#progressModal .progress-bar');
        const messageElement = document.getElementById('progress-message');
        const closeButton = document.getElementById('close-progress');

        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }

        if (messageElement) {
            messageElement.textContent = message;
        }

        // Show close button when complete
        if (progress >= 100 && closeButton) {
            closeButton.style.display = 'block';
        }
    }

    hideProgress() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('progressModal'));
        if (modal) {
            modal.hide();
        }
    }

    // Error handling
    showError(message) {
        const modal = document.getElementById('errorModal');
        const messageElement = document.getElementById('error-message');
        
        messageElement.textContent = message;
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Success handling
    showSuccess(message, downloadUrl = null) {
        const modal = document.getElementById('successModal');
        const messageElement = document.getElementById('success-message');
        const downloadLink = document.getElementById('download-link');
        const downloadBtn = document.getElementById('download-btn');

        messageElement.textContent = message;

        if (downloadUrl) {
            downloadBtn.href = downloadUrl;
            downloadLink.style.display = 'block';
        } else {
            downloadLink.style.display = 'none';
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // API helpers
    async makeRequest(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Playlist handling
    handlePlaylistFetched(data) {
        this.currentTempFile = data.temp_file;
        this.currentPlaylistName = data.playlist_name;

        // Show playlist results
        const resultsDiv = document.getElementById('playlist-results');
        const infoDiv = document.getElementById('playlist-info');
        const trackList = document.getElementById('track-list');

        if (resultsDiv && infoDiv && trackList) {
            infoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-check-circle me-2"></i>Playlist Fetched Successfully!</h6>
                    <p class="mb-0"><strong>${data.playlist_name}</strong> - ${data.track_count} tracks</p>
                </div>
            `;

            // Populate track preview
            trackList.innerHTML = '';
            data.tracks.forEach(track => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${this.escapeHtml(track.track_name)}</td>
                    <td>${this.escapeHtml(track.artist_name)}</td>
                    <td>${this.escapeHtml(track.album_name)}</td>
                `;
                trackList.appendChild(row);
            });

            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // Liked songs handling
    handleLikedSongsFetched(data) {
        this.currentTempFile = data.temp_file;

        // Show liked songs results
        const resultsDiv = document.getElementById('liked-songs-results');
        const infoDiv = document.getElementById('liked-songs-info');
        const trackList = document.getElementById('track-list-liked');

        if (resultsDiv && infoDiv && trackList) {
            infoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h6><i class="fas fa-check-circle me-2"></i>Liked Songs Fetched Successfully!</h6>
                    <p class="mb-0"><strong>${data.track_count}</strong> liked songs retrieved</p>
                </div>
            `;

            // Populate track preview
            trackList.innerHTML = '';
            data.tracks.forEach(track => {
                const row = document.createElement('tr');
                const addedDate = new Date(track.added_at).toLocaleDateString();
                row.innerHTML = `
                    <td>${this.escapeHtml(track.track_name)}</td>
                    <td>${this.escapeHtml(track.artist_name)}</td>
                    <td>${this.escapeHtml(track.album_name)}</td>
                    <td>${addedDate}</td>
                `;
                trackList.appendChild(row);
            });

            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
    }

    // M3U generation handling
    handleM3UGenerated(data) {
        const downloadUrl = `/download/${encodeURIComponent(data.file_path)}`;
        this.showSuccess(
            'M3U playlist has been generated successfully!',
            downloadUrl
        );
    }

    // Lidarr completion handling
    handleLidarrComplete(data) {
        this.showSuccess(data.message);
    }

    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDuration(ms) {
        const minutes = Math.floor(ms / 60000);
        const seconds = ((ms % 60000) / 1000).toFixed(0);
        return `${minutes}:${seconds.padStart(2, '0')}`;
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString();
    }

    // Animation helpers
    fadeIn(element) {
        element.classList.add('fade-in');
        element.style.display = 'block';
    }

    slideIn(element) {
        element.classList.add('slide-in');
        element.style.display = 'block';
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.spotifyApp = new SpotifyMigrationApp();
});

// Export for use in other scripts
window.SpotifyMigrationApp = SpotifyMigrationApp;
