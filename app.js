// YT Short Clipper - Frontend JavaScript

let processingInterval = null;

// Show alert message
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.getElementById('alert-container').innerHTML = alertHtml;
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Start processing
async function startProcessing() {
    const url = document.getElementById('video-url').value.trim();
    const numClips = parseInt(document.getElementById('num-clips').value);
    const addCaptions = document.getElementById('add-captions').checked;
    const addHook = document.getElementById('add-hook').checked;
    
    if (!url) {
        showAlert('URL tidak boleh kosong!', 'warning');
        return;
    }
    
    // Validate URL
    const supportedPlatforms = ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 'facebook.com', 'twitch.tv'];
    const isSupported = supportedPlatforms.some(platform => url.toLowerCase().includes(platform));
    
    if (!isSupported) {
        showAlert('Platform tidak didukung! Gunakan: YouTube, TikTok, Instagram, Facebook, Twitch', 'danger');
        return;
    }
    
    // Disable input section
    document.getElementById('input-section').style.display = 'none';
    document.getElementById('processing-section').style.display = 'block';
    
    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                num_clips: numClips,
                add_captions: addCaptions,
                add_hook: addHook
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Proses dimulai! Mohon tunggu...', 'success');
            startStatusPolling();
        } else {
            showAlert(data.error || 'Gagal memulai proses', 'danger');
            resetUI();
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
        resetUI();
    }
}

// Poll processing status
function startStatusPolling() {
    if (processingInterval) {
        clearInterval(processingInterval);
    }
    
    processingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            updateStatusUI(status);
            
            if (!status.is_processing) {
                clearInterval(processingInterval);
                processingInterval = null;
                
                if (status.error) {
                    showAlert('Error: ' + status.error, 'danger');
                } else {
                    showAlert('Proses selesai! ' + status.clips.length + ' klip berhasil dibuat!', 'success');
                    loadClips();
                }
                
                resetUI();
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 1000); // Poll every 1 second
}

// Update status UI
function updateStatusUI(status) {
    document.getElementById('status-text').textContent = status.current_step;
    document.getElementById('progress-bar').style.width = status.progress + '%';
    document.getElementById('progress-text').textContent = Math.round(status.progress) + '%';
    document.getElementById('current-clip').textContent = status.current_clip;
    document.getElementById('total-clips').textContent = status.total_clips;
}

// Reset UI
function resetUI() {
    document.getElementById('input-section').style.display = 'block';
    document.getElementById('processing-section').style.display = 'none';
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-text').textContent = '0%';
}

// Load clips
async function loadClips() {
    try {
        const response = await fetch('/api/clips');
        const data = await response.json();
        
        const container = document.getElementById('clips-container');
        
        if (data.clips.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center text-muted py-5">
                    <i class="fas fa-film fa-3x mb-3"></i>
                    <p>Belum ada klip. Mulai proses video untuk membuat klip!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = '';
        
        data.clips.forEach(clip => {
            const metadata = clip.metadata;
            const card = createClipCard(clip.folder, metadata, clip.file_size_mb);
            container.innerHTML += card;
        });
        
    } catch (error) {
        console.error('Error loading clips:', error);
        showAlert('Gagal memuat klip', 'danger');
    }
}

// Create clip card HTML
function createClipCard(folder, metadata, fileSize) {
    const duration = Math.round(metadata.duration_seconds);
    const hasHook = metadata.has_hook ? '<i class="fas fa-fish text-success"></i>' : '';
    const hasCaptions = metadata.has_captions ? '<i class="fas fa-closed-captioning text-success"></i>' : '';
    
    return `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card h-100 clip-card">
                <div class="card-body">
                    <h6 class="card-title text-truncate" title="${metadata.title}">
                        ${metadata.title}
                    </h6>
                    <p class="card-text small text-muted">
                        ${metadata.description || 'Tidak ada deskripsi'}
                    </p>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <small class="text-muted">
                            <i class="fas fa-clock"></i> ${duration}s | ${fileSize}MB
                        </small>
                        <small>
                            ${hasHook} ${hasCaptions}
                        </small>
                    </div>
                    <div class="btn-group w-100" role="group">
                        <button 
                            class="btn btn-sm btn-primary" 
                            onclick="previewClip('${folder}')"
                            title="Preview"
                        >
                            <i class="fas fa-play"></i>
                        </button>
                        <button 
                            class="btn btn-sm btn-success" 
                            onclick="downloadClip('${folder}')"
                            title="Download"
                        >
                            <i class="fas fa-download"></i>
                        </button>
                        <button 
                            class="btn btn-sm btn-danger" 
                            onclick="deleteClip('${folder}')"
                            title="Delete"
                        >
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Preview clip
function previewClip(folder) {
    const videoUrl = `/api/clips/${folder}/stream`;
    const modal = `
        <div class="modal fade" id="previewModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Preview Clip</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <video controls style="max-width: 100%; max-height: 70vh;">
                            <source src="${videoUrl}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('previewModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modal);
    const modalElement = new bootstrap.Modal(document.getElementById('previewModal'));
    modalElement.show();
}

// Download clip
function downloadClip(folder) {
    window.location.href = `/api/clips/${folder}/video`;
}

// Delete clip
async function deleteClip(folder) {
    if (!confirm('Yakin ingin menghapus klip ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/clips/${folder}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Klip berhasil dihapus', 'success');
            loadClips();
        } else {
            showAlert(data.error || 'Gagal menghapus klip', 'danger');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    }
}

// Save settings
async function saveSettings() {
    const apiKey = document.getElementById('api-key-input').value;
    const model = document.getElementById('model-select').value;
    const whisperModel = document.getElementById('whisper-model-select').value;
    
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                openrouter_api_key: apiKey,
                model: model,
                whisper_model: whisperModel
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Pengaturan berhasil disimpan', 'success');
            bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
        } else {
            showAlert(data.error || 'Gagal menyimpan pengaturan', 'danger');
        }
    } catch (error) {
        showAlert('Error: ' + error.message, 'danger');
    }
}

// Load config on page load
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('model-select').value = config.model || 'meta-llama/llama-3.1-70b-instruct';
        document.getElementById('whisper-model-select').value = config.whisper_model || 'base';
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadClips();
    loadConfig();
    
    // Allow Enter key to start processing
    document.getElementById('video-url').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            startProcessing();
        }
    });
});
