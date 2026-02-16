# API DOCUMENTATION - YT SHORT CLIPPER

Base URL: `http://YOUR_VPS_IP:7575`

---

## 📋 ENDPOINTS

### 1. Health Check
**GET** `/health`

Check if server is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-02-16T12:00:00.000Z"
}
```

---

### 2. Get Configuration
**GET** `/api/config`

Get current system configuration.

**Response:**
```json
{
  "has_api_key": true,
  "default_num_clips": 5,
  "add_captions": true,
  "add_hook": true,
  "model": "meta-llama/llama-3.1-70b-instruct",
  "whisper_model": "base"
}
```

---

### 3. Update Configuration
**POST** `/api/config`

Update system configuration.

**Request Body:**
```json
{
  "openrouter_api_key": "sk-or-v1-...",
  "default_num_clips": 5,
  "add_captions": true,
  "add_hook": true,
  "model": "meta-llama/llama-3.1-70b-instruct",
  "whisper_model": "base"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Konfigurasi berhasil disimpan"
}
```

---

### 4. Start Processing
**POST** `/api/process`

Start video processing.

**Request Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=xxxxx",
  "num_clips": 5,
  "add_captions": true,
  "add_hook": true
}
```

**Supported Platforms:**
- YouTube: `youtube.com`, `youtu.be`
- TikTok: `tiktok.com`
- Instagram: `instagram.com`
- Facebook: `facebook.com`
- Twitch: `twitch.tv`

**Response:**
```json
{
  "success": true,
  "message": "Proses dimulai"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "URL tidak boleh kosong"
}
```

---

### 5. Get Processing Status
**GET** `/api/status`

Get real-time processing status.

**Response:**
```json
{
  "is_processing": true,
  "current_step": "✂️ Memproses klip 2/5...",
  "progress": 45,
  "current_clip": 2,
  "total_clips": 5,
  "error": null,
  "clips": [
    {
      "folder": "20240216-120000-clip01",
      "title": "Highlight 1",
      "duration": 75.5
    }
  ]
}
```

**Status Steps:**
- `📥 Mengunduh video...` (5-15%)
- `🤖 Mencari highlight dengan AI...` (20-30%)
- `✂️ Memproses klip X/Y...` (30-90%)
- `📱 Konversi ke portrait...`
- `🎣 Menambahkan hook...`
- `📝 Menambahkan subtitle...`
- `✅ Selesai!` (100%)

---

### 6. List All Clips
**GET** `/api/clips`

Get list of all generated clips.

**Response:**
```json
{
  "clips": [
    {
      "folder": "20240216-120000-clip01",
      "file_size_mb": 15.3,
      "metadata": {
        "title": "🔥 Momen Kocak Saat...",
        "description": "Deskripsi singkat",
        "hook_text": "Hook text intro",
        "start_time": "00:15:23,000",
        "end_time": "00:17:05,000",
        "duration_seconds": 102.0,
        "original_url": "https://...",
        "original_title": "Video Asli",
        "has_hook": true,
        "has_captions": true,
        "created_at": "2024-02-16T12:00:00"
      }
    }
  ]
}
```

---

### 7. Get Specific Clip
**GET** `/api/clips/<folder_name>`

Get metadata for specific clip.

**Example:** `/api/clips/20240216-120000-clip01`

**Response:**
```json
{
  "title": "🔥 Momen Kocak...",
  "description": "Deskripsi",
  "hook_text": "Hook text",
  "start_time": "00:15:23,000",
  "end_time": "00:17:05,000",
  "duration_seconds": 102.0,
  "original_url": "https://...",
  "has_hook": true,
  "has_captions": true,
  "created_at": "2024-02-16T12:00:00"
}
```

---

### 8. Download Clip
**GET** `/api/clips/<folder_name>/video`

Download clip video file.

**Example:** `/api/clips/20240216-120000-clip01/video`

**Response:** MP4 video file (download)

---

### 9. Stream Clip
**GET** `/api/clips/<folder_name>/stream`

Stream clip video for preview.

**Example:** `/api/clips/20240216-120000-clip01/stream`

**Response:** MP4 video stream

---

### 10. Delete Clip
**DELETE** `/api/clips/<folder_name>`

Delete a clip and its metadata.

**Example:** `DELETE /api/clips/20240216-120000-clip01`

**Response:**
```json
{
  "success": true,
  "message": "Clip berhasil dihapus"
}
```

---

## 🔧 CURL EXAMPLES

### Start Processing
```bash
curl -X POST http://localhost:7575/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "num_clips": 3,
    "add_captions": true,
    "add_hook": true
  }'
```

### Check Status (loop)
```bash
while true; do
  curl -s http://localhost:7575/api/status | jq
  sleep 2
done
```

### List Clips
```bash
curl http://localhost:7575/api/clips | jq
```

### Download Clip
```bash
curl -O http://localhost:7575/api/clips/20240216-120000-clip01/video
```

### Delete Clip
```bash
curl -X DELETE http://localhost:7575/api/clips/20240216-120000-clip01
```

---

## 🐍 PYTHON EXAMPLES

### Start Processing
```python
import requests
import json

url = "http://localhost:7575/api/process"
data = {
    "url": "https://www.youtube.com/watch?v=xxxxx",
    "num_clips": 5,
    "add_captions": True,
    "add_hook": True
}

response = requests.post(url, json=data)
print(response.json())
```

### Monitor Progress
```python
import requests
import time

status_url = "http://localhost:7575/api/status"

while True:
    response = requests.get(status_url)
    status = response.json()
    
    print(f"Progress: {status['progress']}% - {status['current_step']}")
    
    if not status['is_processing']:
        if status['error']:
            print(f"Error: {status['error']}")
        else:
            print(f"Done! {len(status['clips'])} clips created")
        break
    
    time.sleep(2)
```

### Download All Clips
```python
import requests
import os

clips_url = "http://localhost:7575/api/clips"
response = requests.get(clips_url)
clips = response.json()['clips']

os.makedirs('downloads', exist_ok=True)

for clip in clips:
    folder = clip['folder']
    download_url = f"http://localhost:7575/api/clips/{folder}/video"
    
    print(f"Downloading {folder}...")
    
    video = requests.get(download_url)
    with open(f"downloads/{folder}.mp4", 'wb') as f:
        f.write(video.content)
    
    print(f"✅ Downloaded: {folder}.mp4")
```

---

## 🔐 ERROR CODES

| Status Code | Meaning |
|------------|---------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 404 | Not Found (clip doesn't exist) |
| 409 | Conflict (already processing) |
| 500 | Server Error |

---

## 📊 RATE LIMITS

- **No rate limits** for local deployment
- Processing is queued (one at a time)
- API polling recommended: 1-2 seconds interval

---

## 🎯 BEST PRACTICES

1. **Poll status every 2 seconds** (not faster)
2. **Check is_processing** before starting new job
3. **Handle errors gracefully** with retry logic
4. **Clean up old clips** periodically to save disk space
5. **Use streaming endpoint** for preview (don't download full video)

---

## 🔄 AUTOMATION EXAMPLE

Complete automation script:

```python
import requests
import time
import sys

def process_video(url, num_clips=5):
    base_url = "http://localhost:7575/api"
    
    # Start processing
    print(f"Starting processing: {url}")
    response = requests.post(f"{base_url}/process", json={
        "url": url,
        "num_clips": num_clips,
        "add_captions": True,
        "add_hook": True
    })
    
    if not response.json()['success']:
        print(f"Failed to start: {response.json()['error']}")
        return False
    
    # Monitor progress
    while True:
        status = requests.get(f"{base_url}/status").json()
        
        progress = status['progress']
        step = status['current_step']
        
        print(f"[{progress:3.0f}%] {step}")
        
        if not status['is_processing']:
            if status['error']:
                print(f"❌ Error: {status['error']}")
                return False
            else:
                print(f"✅ Done! {len(status['clips'])} clips created")
                return True
        
        time.sleep(2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process.py <video_url> [num_clips]")
        sys.exit(1)
    
    url = sys.argv[1]
    num_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    success = process_video(url, num_clips)
    sys.exit(0 if success else 1)
```

Run:
```bash
python process.py "https://www.youtube.com/watch?v=xxxxx" 5
```

---

## 📱 WEBHOOK (Future Feature)

Coming soon: Webhook notification when processing is complete.

```json
POST https://your-webhook-url.com/notify
{
  "event": "processing_complete",
  "clips": [...],
  "timestamp": "2024-02-16T12:00:00"
}
```

---

## 🎉 HAPPY CLIPPING!

For more info, check `README.md`
