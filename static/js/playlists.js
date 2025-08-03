// Playlists page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    const playlistForm = document.getElementById('playlist-form');
    const playlistInput = document.getElementById('playlist-input');
    const downloadJsonBtn = document.getElementById('download-json');
    const generateM3UBtn = document.getElementById('generate-m3u');
    const sendToLidarrBtn = document.getElementById('send-to-lidarr');
    const userPlaylistsDiv = document.getElementById('user-playlists');

    // Load user playlists on page load
    loadUserPlaylists();

    // Handle playlist form submission
    if (playlistForm) {
        playlistForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const playlistId = playlistInput.value.trim();
            
            if (!playlistId) {
                window.spotifyApp.showError('Please enter a playlist URL or ID');
                return;
            }

            await fetchPlaylist(playlistId);
        });
    }

    // Handle JSON download
    if (downloadJsonBtn) {
        downloadJsonBtn.addEventListener('click', () => {
            if (!window.spotifyApp.currentPlaylistData) {
                window.spotifyApp.showError('Please fetch a playlist first');
                return;
            }

            window.spotifyApp.downloadJSON(window.spotifyApp.currentPlaylistData, window.spotifyApp.currentPlaylistName || 'playlist');
        });
    }

    // Handle M3U generation
    if (generateM3UBtn) {
        generateM3UBtn.addEventListener('click', async () => {
            if (!window.spotifyApp.currentTempFile) {
                window.spotifyApp.showError('Please fetch a playlist first');
                return;
            }

            await generateM3U();
        });
    }

    // Handle Lidarr submission
    if (sendToLidarrBtn) {
        sendToLidarrBtn.addEventListener('click', async () => {
            if (!window.spotifyApp.currentTempFile) {
                window.spotifyApp.showError('Please fetch a playlist first');
                return;
            }

            await sendToLidarr();
        });
    }

    // Load user playlists
    async function loadUserPlaylists() {
        try {
            const response = await window.spotifyApp.makeRequest('/api/user-playlists');
            displayUserPlaylists(response.items || []);
        } catch (error) {
            console.error('Failed to load user playlists:', error);
            userPlaylistsDiv.innerHTML = `
                <div class="alert alert-warning">
                    <small>Unable to load your playlists. ${error.message}</small>
                </div>
            `;
        }
    }

    // Display user playlists
    function displayUserPlaylists(playlists) {
        if (!playlists.length) {
            userPlaylistsDiv.innerHTML = `
                <div class="text-muted text-center">
                    <i class="fas fa-music fa-2x mb-2"></i>
                    <p>No playlists found</p>
                </div>
            `;
            return;
        }

        const playlistsHtml = playlists.map(playlist => `
            <div class="playlist-item mb-2" data-playlist-id="${playlist.id}">
                <div class="d-flex align-items-center">
                    <div class="flex-shrink-0">
                        ${playlist.images && playlist.images[0] 
                            ? `<img src="${playlist.images[0].url}" alt="${playlist.name}" 
                                 class="rounded" style="width: 40px; height: 40px; object-fit: cover;">`
                            : `<div class="bg-secondary rounded d-flex align-items-center justify-content-center" 
                                 style="width: 40px; height: 40px;">
                                 <i class="fas fa-music text-white"></i>
                               </div>`
                        }
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <h6 class="mb-1">${window.spotifyApp.escapeHtml(playlist.name)}</h6>
                        <small class="text-muted">${playlist.tracks.total} tracks</small>
                    </div>
                </div>
            </div>
        `).join('');

        userPlaylistsDiv.innerHTML = playlistsHtml;

        // Add click handlers to playlist items
        document.querySelectorAll('.playlist-item').forEach(item => {
            item.addEventListener('click', () => {
                const playlistId = item.dataset.playlistId;
                playlistInput.value = playlistId;
                
                // Visual feedback
                document.querySelectorAll('.playlist-item').forEach(p => p.classList.remove('selected'));
                item.classList.add('selected');
            });
        });
    }

    // Fetch playlist data
    async function fetchPlaylist(playlistId) {
        try {
            window.spotifyApp.showProgress('Fetching Playlist');
            
            const response = await window.spotifyApp.makeRequest('/api/fetch-playlist', {
                method: 'POST',
                body: JSON.stringify({ playlist_id: playlistId })
            });

            // Progress updates will be handled by socket events
        } catch (error) {
            window.spotifyApp.hideProgress();
            window.spotifyApp.showError(`Failed to fetch playlist: ${error.message}`);
        }
    }

    // Generate M3U playlist
    async function generateM3U() {
        try {
            window.spotifyApp.showProgress('Generating M3U');
            
            const response = await window.spotifyApp.makeRequest('/api/generate-m3u', {
                method: 'POST',
                body: JSON.stringify({
                    temp_file: window.spotifyApp.currentTempFile,
                    playlist_name: window.spotifyApp.currentPlaylistName || 'spotify_playlist'
                })
            });

            // Progress updates will be handled by socket events
        } catch (error) {
            window.spotifyApp.hideProgress();
            window.spotifyApp.showError(`Failed to generate M3U: ${error.message}`);
        }
    }

    // Send to Lidarr
    async function sendToLidarr() {
        try {
            window.spotifyApp.showProgress('Sending to Lidarr');
            
            const response = await window.spotifyApp.makeRequest('/api/send-to-lidarr', {
                method: 'POST',
                body: JSON.stringify({
                    temp_file: window.spotifyApp.currentTempFile
                })
            });

            // Progress updates will be handled by socket events
        } catch (error) {
            window.spotifyApp.hideProgress();
            window.spotifyApp.showError(`Failed to send to Lidarr: ${error.message}`);
        }
    }

    // Handle playlist URL input formatting
    if (playlistInput) {
        playlistInput.addEventListener('input', (e) => {
            let value = e.target.value.trim();
            
            // Extract playlist ID from URL if needed
            if (value.includes('spotify.com/playlist/')) {
                const match = value.match(/playlist\/([a-zA-Z0-9]+)/);
                if (match) {
                    e.target.value = match[1];
                }
            }
        });

        // Handle paste events
        playlistInput.addEventListener('paste', (e) => {
            setTimeout(() => {
                const event = new Event('input', { bubbles: true });
                e.target.dispatchEvent(event);
            }, 10);
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to fetch playlist
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            if (document.activeElement === playlistInput) {
                playlistForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Auto-focus playlist input
    if (playlistInput && !playlistInput.value) {
        playlistInput.focus();
    }
});
