#!/usr/bin/env python3
"""
YT-Short-Clipper Web Version with OpenRouter API
Web-based interface for automatic YouTube short video clipper
Access via http://YOUR_VPS_IP:7575
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import json
import threading
import time
from datetime import datetime
from pathlib import Path
import shutil

# Import core modules
from core.downloader import download_video
from core.highlight_finder import find_highlights
from core.video_clipper import clip_video
from core.portrait_converter import convert_to_portrait
from core.caption_generator import add_captions
from core.hook_generator import add_hook

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = OUTPUT_DIR / "_temp"
CONFIG_FILE = BASE_DIR / "config.json"

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Global state for processing status
processing_status = {
    "is_processing": False,
    "current_step": "",
    "progress": 0,
    "error": None,
    "clips": [],
    "current_clip": 0,
    "total_clips": 0
}

def load_config():
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "openrouter_api_key": "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",
        "default_num_clips": 5,
        "add_captions": True,
        "add_hook": True,
        "model": "meta-llama/llama-3.1-70b-instruct",
        "whisper_model": "base"
    }

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config = load_config()
    safe_config = {k: v for k, v in config.items() if k != 'openrouter_api_key'}
    safe_config['has_api_key'] = bool(config.get('openrouter_api_key'))
    return jsonify(safe_config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        config = load_config()
        data = request.json
        
        if 'openrouter_api_key' in data:
            config['openrouter_api_key'] = data['openrouter_api_key']
        if 'default_num_clips' in data:
            config['default_num_clips'] = int(data['default_num_clips'])
        if 'add_captions' in data:
            config['add_captions'] = bool(data['add_captions'])
        if 'add_hook' in data:
            config['add_hook'] = bool(data['add_hook'])
        if 'model' in data:
            config['model'] = data['model']
        if 'whisper_model' in data:
            config['whisper_model'] = data['whisper_model']
        
        save_config(config)
        return jsonify({"success": True, "message": "Konfigurasi berhasil disimpan"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/status')
def get_status():
    """Get current processing status"""
    return jsonify(processing_status)

@app.route('/api/process', methods=['POST'])
def process_video():
    """Start video processing"""
    global processing_status
    
    if processing_status['is_processing']:
        return jsonify({"success": False, "error": "Sedang memproses video lain"}), 409
    
    try:
        data = request.json
        url = data.get('url')
        num_clips = int(data.get('num_clips', 5))
        add_captions_flag = data.get('add_captions', True)
        add_hook_flag = data.get('add_hook', True)
        
        if not url:
            return jsonify({"success": False, "error": "URL tidak boleh kosong"}), 400
        
        # Validate URL platform
        supported_platforms = ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com', 'facebook.com', 'twitch.tv']
        if not any(platform in url.lower() for platform in supported_platforms):
            return jsonify({"success": False, "error": "Platform tidak didukung. Gunakan: YouTube, TikTok, Instagram, Facebook, Twitch"}), 400
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_video_background,
            args=(url, num_clips, add_captions_flag, add_hook_flag)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({"success": True, "message": "Proses dimulai"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

def process_video_background(url, num_clips, add_captions_flag, add_hook_flag):
    """Background processing function"""
    global processing_status
    
    processing_status['is_processing'] = True
    processing_status['error'] = None
    processing_status['clips'] = []
    processing_status['progress'] = 0
    processing_status['current_clip'] = 0
    processing_status['total_clips'] = num_clips
    
    config = load_config()
    
    try:
        # Step 1: Download video
        processing_status['current_step'] = "📥 Mengunduh video..."
        processing_status['progress'] = 5
        video_path, subtitle_path, video_info = download_video(url, str(TEMP_DIR))
        
        if not video_path or not os.path.exists(video_path):
            raise Exception("Gagal mengunduh video")
        
        processing_status['progress'] = 15
        
        # Step 2: Find highlights
        processing_status['current_step'] = "🤖 Mencari highlight menarik dengan AI..."
        processing_status['progress'] = 20
        highlights = find_highlights(
            subtitle_path, 
            num_clips, 
            config['openrouter_api_key'],
            config.get('model', 'meta-llama/llama-3.1-70b-instruct')
        )
        
        if not highlights:
            raise Exception("Tidak ditemukan highlight menarik")
        
        processing_status['progress'] = 30
        processing_status['total_clips'] = len(highlights)
        
        # Step 3: Process each clip
        for idx, highlight in enumerate(highlights, 1):
            processing_status['current_clip'] = idx
            processing_status['current_step'] = f"✂️ Memproses klip {idx}/{len(highlights)}..."
            
            # Create clip folder with timestamp
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            clip_folder = OUTPUT_DIR / f"{timestamp}-clip{idx:02d}"
            clip_folder.mkdir(exist_ok=True)
            
            base_progress = 30 + ((idx-1) / len(highlights)) * 60
            
            # Clip video
            processing_status['current_step'] = f"✂️ Memotong video klip {idx}..."
            processing_status['progress'] = int(base_progress + 5)
            clipped_path = clip_video(video_path, highlight, str(clip_folder))
            
            # Convert to portrait
            processing_status['current_step'] = f"📱 Konversi ke portrait klip {idx}..."
            processing_status['progress'] = int(base_progress + 15)
            portrait_path = convert_to_portrait(clipped_path, str(clip_folder))
            
            current_video = portrait_path
            
            # Add hook if requested
            if add_hook_flag and highlight.get('hook_text'):
                processing_status['current_step'] = f"🎣 Menambahkan hook klip {idx}..."
                processing_status['progress'] = int(base_progress + 25)
                hook_path = add_hook(
                    current_video, 
                    highlight.get('hook_text', ''),
                    str(clip_folder)
                )
                if hook_path and os.path.exists(hook_path):
                    current_video = hook_path
            
            # Add captions if requested
            if add_captions_flag:
                processing_status['current_step'] = f"📝 Menambahkan subtitle klip {idx}..."
                processing_status['progress'] = int(base_progress + 40)
                caption_path = add_captions(
                    current_video, 
                    str(clip_folder),
                    config.get('whisper_model', 'base')
                )
                if caption_path and os.path.exists(caption_path):
                    current_video = caption_path
            
            # Rename to master.mp4
            master_path = clip_folder / "master.mp4"
            if os.path.exists(current_video) and current_video != str(master_path):
                shutil.copy2(current_video, str(master_path))
            
            # Save metadata
            metadata = {
                "title": highlight.get('title', f'Clip {idx}'),
                "description": highlight.get('description', ''),
                "hook_text": highlight.get('hook_text', ''),
                "start_time": highlight.get('start_time', ''),
                "end_time": highlight.get('end_time', ''),
                "duration_seconds": highlight.get('duration', 0),
                "original_url": url,
                "original_title": video_info.get('title', ''),
                "has_hook": add_hook_flag and bool(highlight.get('hook_text')),
                "has_captions": add_captions_flag,
                "created_at": datetime.now().isoformat()
            }
            
            metadata_path = clip_folder / "data.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            processing_status['clips'].append({
                "folder": clip_folder.name,
                "title": metadata['title'],
                "duration": metadata['duration_seconds']
            })
        
        # Cleanup temp files
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(subtitle_path):
                os.remove(subtitle_path)
        except:
            pass
        
        processing_status['current_step'] = "✅ Selesai!"
        processing_status['progress'] = 100
        processing_status['is_processing'] = False
        
    except Exception as e:
        processing_status['error'] = str(e)
        processing_status['is_processing'] = False
        processing_status['current_step'] = "❌ Error!"
        print(f"Error processing video: {e}")
        import traceback
        traceback.print_exc()

@app.route('/api/clips')
def list_clips():
    """List all generated clips"""
    clips = []
    try:
        for folder in OUTPUT_DIR.iterdir():
            if folder.is_dir() and folder.name != "_temp":
                metadata_file = folder / "data.json"
                video_file = folder / "master.mp4"
                
                if metadata_file.exists() and video_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Get file size
                    file_size = os.path.getsize(video_file) / (1024 * 1024)  # MB
                    
                    clips.append({
                        "folder": folder.name,
                        "metadata": metadata,
                        "file_size_mb": round(file_size, 2)
                    })
    except Exception as e:
        print(f"Error listing clips: {e}")
    
    # Sort by creation time (newest first)
    clips.sort(key=lambda x: x['metadata'].get('created_at', ''), reverse=True)
    return jsonify({"clips": clips})

@app.route('/api/clips/<folder_name>')
def get_clip(folder_name):
    """Get specific clip metadata"""
    clip_folder = OUTPUT_DIR / folder_name
    if not clip_folder.exists():
        return jsonify({"error": "Clip tidak ditemukan"}), 404
    
    metadata_file = clip_folder / "data.json"
    if not metadata_file.exists():
        return jsonify({"error": "Metadata tidak ditemukan"}), 404
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    return jsonify(metadata)

@app.route('/api/clips/<folder_name>/video')
def download_clip(folder_name):
    """Download clip video"""
    clip_folder = OUTPUT_DIR / folder_name
    video_file = clip_folder / "master.mp4"
    
    if not video_file.exists():
        return jsonify({"error": "Video tidak ditemukan"}), 404
    
    return send_file(
        video_file, 
        as_attachment=True, 
        download_name=f"{folder_name}.mp4",
        mimetype='video/mp4'
    )

@app.route('/api/clips/<folder_name>/stream')
def stream_clip(folder_name):
    """Stream clip video for preview"""
    clip_folder = OUTPUT_DIR / folder_name
    video_file = clip_folder / "master.mp4"
    
    if not video_file.exists():
        return jsonify({"error": "Video tidak ditemukan"}), 404
    
    return send_file(video_file, mimetype='video/mp4')

@app.route('/api/clips/<folder_name>', methods=['DELETE'])
def delete_clip(folder_name):
    """Delete a clip"""
    clip_folder = OUTPUT_DIR / folder_name
    if not clip_folder.exists():
        return jsonify({"error": "Clip tidak ditemukan"}), 404
    
    try:
        shutil.rmtree(clip_folder)
        return jsonify({"success": True, "message": "Clip berhasil dihapus"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Initialize config with API key
    config = load_config()
    save_config(config)
    
    print("=" * 70)
    print("🎬 YT-SHORT-CLIPPER WEB SERVER")
    print("=" * 70)
    print(f"🌐 Server: http://0.0.0.0:7575")
    print(f"📁 Output: {OUTPUT_DIR}")
    print(f"🔑 API: OpenRouter (Llama 3.1 70B)")
    print(f"🎙️ Whisper: Local Model ({config.get('whisper_model', 'base')})")
    print(f"🔊 TTS: Edge TTS (Free)")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=7575, debug=False, threaded=True)
