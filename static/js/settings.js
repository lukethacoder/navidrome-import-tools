// Settings page JavaScript
document.addEventListener('DOMContentLoaded', () => {
    const lidarrForm = document.getElementById('lidarr-settings');
    const navidromeForm = document.getElementById('navidrome-settings');
    const testLidarrBtn = document.getElementById('test-lidarr');
    const testNavidromeBtn = document.getElementById('test-navidrome');

    // Handle Lidarr settings form
    if (lidarrForm) {
        lidarrForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveLidarrSettings();
        });
    }

    // Handle Navidrome settings form
    if (navidromeForm) {
        navidromeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await saveNavidromeSettings();
        });
    }

    // Handle Lidarr connection test
    if (testLidarrBtn) {
        testLidarrBtn.addEventListener('click', async () => {
            await testLidarrConnection();
        });
    }

    // Handle Navidrome database test
    if (testNavidromeBtn) {
        testNavidromeBtn.addEventListener('click', async () => {
            await testNavidromeDatabase();
        });
    }

    // Load current settings on page load
    loadCurrentSettings();

    // Save Lidarr settings
    async function saveLidarrSettings() {
        const formData = {
            lidarr_url: document.getElementById('lidarr-url').value.trim(),
            api_key: document.getElementById('lidarr-api-key').value.trim(),
            root_folder: document.getElementById('root-folder').value.trim(),
            quality_profile_id: parseInt(document.getElementById('quality-profile').value),
            metadata_profile_id: parseInt(document.getElementById('metadata-profile').value)
        };

        try {
            const response = await window.spotifyApp.makeRequest('/api/settings/lidarr', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            showToast('Lidarr settings saved successfully!', 'success');
        } catch (error) {
            window.spotifyApp.showError(`Failed to save Lidarr settings: ${error.message}`);
        }
    }

    // Save Navidrome settings
    async function saveNavidromeSettings() {
        const formData = {
            db_path: document.getElementById('navidrome-db-path').value.trim(),
            music_path_prefix: document.getElementById('music-path-prefix').value.trim()
        };

        try {
            const response = await window.spotifyApp.makeRequest('/api/settings/navidrome', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            showToast('Navidrome settings saved successfully!', 'success');
        } catch (error) {
            window.spotifyApp.showError(`Failed to save Navidrome settings: ${error.message}`);
        }
    }

    // Test Lidarr connection
    async function testLidarrConnection() {
        const url = document.getElementById('lidarr-url').value.trim();
        const apiKey = document.getElementById('lidarr-api-key').value.trim();

        if (!url || !apiKey) {
            window.spotifyApp.showError('Please enter both Lidarr URL and API key');
            return;
        }

        const originalText = testLidarrBtn.innerHTML;
        testLidarrBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
        testLidarrBtn.disabled = true;

        try {
            const response = await window.spotifyApp.makeRequest('/api/test-lidarr', {
                method: 'POST',
                body: JSON.stringify({ lidarr_url: url, api_key: apiKey })
            });

            updateStatusBadge('lidarr-status', 'success', 'Connected');
            showTestResult('Lidarr Connection Test', 'success', 
                'Successfully connected to Lidarr!', response);
        } catch (error) {
            updateStatusBadge('lidarr-status', 'danger', 'Failed');
            showTestResult('Lidarr Connection Test', 'danger', 
                `Connection failed: ${error.message}`, null);
        } finally {
            testLidarrBtn.innerHTML = originalText;
            testLidarrBtn.disabled = false;
        }
    }

    // Test Navidrome database
    async function testNavidromeDatabase() {
        const dbPath = document.getElementById('navidrome-db-path').value.trim();

        if (!dbPath) {
            window.spotifyApp.showError('Please enter the database path');
            return;
        }

        const originalText = testNavidromeBtn.innerHTML;
        testNavidromeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Testing...';
        testNavidromeBtn.disabled = true;

        try {
            const response = await window.spotifyApp.makeRequest('/api/test-navidrome', {
                method: 'POST',
                body: JSON.stringify({ db_path: dbPath })
            });

            updateStatusBadge('navidrome-status', 'success', 'Connected');
            showTestResult('Navidrome Database Test', 'success', 
                'Successfully connected to Navidrome database!', response);
        } catch (error) {
            updateStatusBadge('navidrome-status', 'danger', 'Failed');
            showTestResult('Navidrome Database Test', 'danger', 
                `Database test failed: ${error.message}`, null);
        } finally {
            testNavidromeBtn.innerHTML = originalText;
            testNavidromeBtn.disabled = false;
        }
    }

    // Load current settings
    async function loadCurrentSettings() {
        try {
            const response = await window.spotifyApp.makeRequest('/api/settings');
            
            // Populate Lidarr settings
            if (response.lidarr) {
                const lidarr = response.lidarr;
                document.getElementById('lidarr-url').value = lidarr.url || '';
                document.getElementById('lidarr-api-key').value = lidarr.api_key || '';
                document.getElementById('root-folder').value = lidarr.root_folder || '/music/';
                document.getElementById('quality-profile').value = lidarr.quality_profile_id || 1;
                document.getElementById('metadata-profile').value = lidarr.metadata_profile_id || 1;
            }

            // Populate Navidrome settings
            if (response.navidrome) {
                const navidrome = response.navidrome;
                document.getElementById('navidrome-db-path').value = navidrome.db_path || 'navidrome.db';
                document.getElementById('music-path-prefix').value = navidrome.music_path_prefix || '/music/';
            }
        } catch (error) {
            console.error('Failed to load settings:', error);
        }
    }

    // Update status badge
    function updateStatusBadge(elementId, type, text) {
        const badge = document.getElementById(elementId);
        if (badge) {
            badge.className = `badge bg-${type}`;
            badge.textContent = text;
        }
    }

    // Show test result modal
    function showTestResult(title, type, message, details) {
        const modal = document.getElementById('testModal');
        const header = document.getElementById('test-modal-header');
        const titleElement = document.getElementById('test-modal-title');
        const messageElement = document.getElementById('test-modal-message');
        const detailsDiv = document.getElementById('test-modal-details');
        const codeElement = document.getElementById('test-modal-code');

        // Set header color
        header.className = `modal-header bg-${type} text-white`;
        titleElement.textContent = title;
        messageElement.textContent = message;

        // Show details if available
        if (details) {
            codeElement.textContent = JSON.stringify(details, null, 2);
            detailsDiv.style.display = 'block';
        } else {
            detailsDiv.style.display = 'none';
        }

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    // Show toast notification
    function showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to page
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        toastContainer.appendChild(toast);

        // Show toast
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();

        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    // Input validation
    const urlInputs = document.querySelectorAll('input[type="url"]');
    urlInputs.forEach(input => {
        input.addEventListener('blur', (e) => {
            let value = e.target.value.trim();
            if (value && !value.startsWith('http://') && !value.startsWith('https://')) {
                e.target.value = 'http://' + value;
            }
        });
    });

    // Path input validation
    const pathInputs = document.querySelectorAll('#root-folder, #music-path-prefix');
    pathInputs.forEach(input => {
        input.addEventListener('blur', (e) => {
            let value = e.target.value.trim();
            if (value && !value.endsWith('/')) {
                e.target.value = value + '/';
            }
        });
    });

    // Auto-save on input change (debounced)
    let saveTimeout;
    const autoSaveInputs = document.querySelectorAll('#lidarr-settings input, #navidrome-settings input');
    autoSaveInputs.forEach(input => {
        input.addEventListener('input', () => {
            clearTimeout(saveTimeout);
            saveTimeout = setTimeout(() => {
                // Visual indicator that settings are being saved
                const form = input.closest('form');
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
                    setTimeout(() => {
                        submitBtn.innerHTML = originalText;
                    }, 1000);
                }
            }, 2000);
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + S to save settings
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const activeForm = document.activeElement.closest('form');
            if (activeForm) {
                activeForm.dispatchEvent(new Event('submit'));
            }
        }
    });
});
