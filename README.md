# YT SHORT CLIPPER - PANDUAN INSTALASI LENGKAP

## 🎯 FITUR SISTEM

### ✅ 100% GRATIS (Tanpa Biaya API)
- **OpenRouter API**: Llama 3.1 70B (sudah included API key Anda)
- **Whisper Local**: Transcription subtitle lokal (offline)
- **Edge TTS**: Microsoft Text-to-Speech gratis unlimited

### ✨ Fitur Lengkap
1. **Multi-Platform Support**:
   - ✅ YouTube
   - ✅ TikTok
   - ✅ Instagram
   - ✅ Facebook
   - ✅ Twitch

2. **AI-Powered Processing**:
   - Auto-detect highlight menarik dengan AI
   - Generate hook text yang engaging
   - Subtitle akurat word-by-word
   - Face tracking untuk portrait conversion

3. **Output Profesional**:
   - Portrait 9:16 (1080x1920)
   - CapCut-style captions
   - Hook intro dengan voiceover AI
   - Ready untuk TikTok/Reels/Shorts

---

## 🚀 INSTALASI DI VPS

### 1. Update System & Install Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# Install yt-dlp
sudo pip3 install yt-dlp
```

### 2. Download & Setup Project

```bash
# Masuk ke home directory
cd /home/

# Clone atau upload project
# Jika dari GitHub:
# git clone <your-repo-url> yt-clipper-web

# Atau upload manual via SFTP/SCP
# Pastikan folder yt-clipper-web sudah ada

cd yt-clipper-web
```

### 3. Install Python Dependencies

```bash
# Install semua dependencies
pip3 install -r requirements.txt

# Jika error dengan opencv, coba:
pip3 install opencv-python-headless --break-system-packages
```

### 4. Test Installation

```bash
# Test FFmpeg
ffmpeg -version

# Test yt-dlp
yt-dlp --version

# Test Python modules
python3 -c "import whisper; import cv2; import edge_tts; print('All modules OK!')"
```

### 5. Jalankan Server

```bash
# Jalankan dengan screen (agar tetap running)
screen -S clipper

# Atau jalankan langsung
python3 app.py
```

Server akan running di: **http://YOUR_VPS_IP:7575**

---

## 🔥 CARA MENGGUNAKAN

### Via Web Browser:

1. Buka: `http://YOUR_VPS_IP:7575`
2. Paste URL video (YouTube/TikTok/Instagram/Facebook/Twitch)
3. Pilih jumlah klip (1-10)
4. Centang opsi:
   - ✅ Tambah Subtitle (Whisper)
   - ✅ Tambah Hook Intro (Edge TTS)
5. Klik **"Mulai Proses"**
6. Tunggu proses selesai (progress bar real-time)
7. Download atau preview hasil klip

### API Mode (untuk automation):

```bash
# Start processing
curl -X POST http://localhost:7575/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=xxxxx",
    "num_clips": 5,
    "add_captions": true,
    "add_hook": true
  }'

# Check status
curl http://localhost:7575/api/status

# List clips
curl http://localhost:7575/api/clips

# Download clip
curl http://localhost:7575/api/clips/FOLDER_NAME/video -o clip.mp4
```

---

## ⚙️ KONFIGURASI

### Config File: `config.json`

```json
{
  "openrouter_api_key": "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",
  "default_num_clips": 5,
  "add_captions": true,
  "add_hook": true,
  "model": "meta-llama/llama-3.1-70b-instruct",
  "whisper_model": "base"
}
```

### Whisper Model Options:
- **tiny**: Paling cepat, akurasi 60-70%
- **base**: Balanced, akurasi 70-80% (RECOMMENDED)
- **small**: Lebih akurat, akurasi 80-85%
- **medium**: Sangat akurat, akurasi 85-90%
- **large**: Terbaik, akurasi 90-95% (butuh RAM besar)

### AI Model Options (OpenRouter):
- **meta-llama/llama-3.1-70b-instruct**: Gratis/murah, kualitas bagus (RECOMMENDED)
- **meta-llama/llama-3.1-405b-instruct**: Premium, kualitas terbaik
- **google/gemini-flash-1.5**: Alternatif gratis dari Google

---

## 📁 STRUKTUR OUTPUT

```
output/
├── _temp/                          # Temporary files
│   ├── source.mp4                  # Downloaded video
│   ├── source.id.srt               # Subtitle
│   └── video_info.json             # Metadata
│
├── 20240216-120000-clip01/         # Clip folder
│   ├── master.mp4                  # Final output
│   └── data.json                   # Clip metadata
│
├── 20240216-120030-clip02/
│   ├── master.mp4
│   └── data.json
│
└── ...
```

### data.json Format:

```json
{
  "title": "🔥 Judul Menarik dari AI",
  "description": "Deskripsi singkat untuk caption",
  "hook_text": "Hook text untuk intro",
  "start_time": "00:15:23,000",
  "end_time": "00:17:05,000",
  "duration_seconds": 102.0,
  "original_url": "https://...",
  "original_title": "Video Asli",
  "has_hook": true,
  "has_captions": true,
  "created_at": "2024-02-16T12:00:00"
}
```

---

## 🔧 TROUBLESHOOTING

### Error: "FFmpeg not found"
```bash
sudo apt install ffmpeg
ffmpeg -version  # Test
```

### Error: "yt-dlp not found"
```bash
sudo pip3 install yt-dlp
yt-dlp --version  # Test
```

### Error: "No module named 'whisper'"
```bash
pip3 install openai-whisper --break-system-packages
```

### Error: "OpenCV error"
```bash
pip3 install opencv-python-headless --break-system-packages
```

### Error: "Port 7575 already in use"
```bash
# Cari proses yang menggunakan port
sudo lsof -i :7575

# Kill proses
sudo kill -9 <PID>

# Atau ubah port di app.py (line terakhir):
# app.run(host='0.0.0.0', port=8080)
```

### Error: "Permission denied"
```bash
# Berikan permission execute
chmod +x app.py

# Atau jalankan dengan sudo
sudo python3 app.py
```

### Proses Lambat / Timeout
```bash
# Gunakan Whisper model lebih kecil
# Edit config.json:
"whisper_model": "tiny"  # Dari "base" ke "tiny"

# Atau nonaktifkan subtitle sementara
```

---

## 🎯 TIPS OPTIMASI

### 1. Performance
- Gunakan Whisper **base** untuk balanced speed/accuracy
- Nonaktifkan captions jika tidak perlu (lebih cepat)
- Proses video maksimal 2 jam durasi

### 2. Quality
- Untuk subtitle terbaik: gunakan Whisper **medium**
- Untuk hasil maksimal: aktifkan semua fitur (hook + captions)
- Video sumber minimal 720p untuk hasil terbaik

### 3. Cost Saving
- OpenRouter API sudah gratis/murah (Llama 3.1)
- Whisper lokal = gratis unlimited
- Edge TTS = gratis unlimited
- **Total biaya: $0 per video!**

---

## 🔐 KEAMANAN

### Firewall (Recommended):
```bash
# Allow port 7575
sudo ufw allow 7575/tcp

# Enable firewall
sudo ufw enable
```

### Password Protect (Optional):
Tambahkan basic auth di `app.py`:

```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.verify_password
def verify(username, password):
    return username == 'admin' and password == 'your_password'

@app.route('/')
@auth.login_required
def index():
    return render_template('index.html')
```

---

## 📊 MONITORING

### Check Server Status:
```bash
# Via API
curl http://localhost:7575/health

# Via browser
http://YOUR_VPS_IP:7575/health
```

### View Logs:
```bash
# Jika menggunakan screen
screen -r clipper

# View system logs
journalctl -u clipper -f
```

### Auto-restart with Systemd:
```bash
# Create service file
sudo nano /etc/systemd/system/clipper.service

# Paste:
[Unit]
Description=YT Short Clipper Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/yt-clipper-web
ExecStart=/usr/bin/python3 /home/yt-clipper-web/app.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable & start
sudo systemctl daemon-reload
sudo systemctl enable clipper
sudo systemctl start clipper
sudo systemctl status clipper
```

---

## 🎉 SELESAI!

Server sudah running di: **http://YOUR_VPS_IP:7575**

**API Key OpenRouter sudah included di system**, jadi tidak perlu setup API key lagi!

Selamat menggunakan! 🚀

---

## 📞 SUPPORT

Jika ada masalah:
1. Check logs: `screen -r clipper`
2. Test dependencies: `python3 -c "import whisper; import cv2; print('OK')"`
3. Restart server: `sudo systemctl restart clipper`

Enjoy creating viral shorts! 🎬✨
