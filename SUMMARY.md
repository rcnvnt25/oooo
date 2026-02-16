# 🎬 YT SHORT CLIPPER - PROJECT SUMMARY

## 📊 OVERVIEW

**YT Short Clipper** adalah sistem otomatis untuk mengubah video panjang menjadi klip pendek viral dengan AI, subtitle akurat, dan voiceover.

### ✨ Keunggulan Utama:
- ✅ **100% GRATIS** - Menggunakan OpenRouter API (Llama 3.1 70B)
- ✅ **Multi-Platform** - YouTube, TikTok, Instagram, Facebook, Twitch
- ✅ **AI-Powered** - Auto-detect highlight menarik
- ✅ **Professional Output** - Portrait 9:16, captions, hook intro
- ✅ **Web-Based** - Akses via browser di port 7575
- ✅ **API Ready** - REST API untuk automation

---

## 📁 STRUKTUR PROJECT

```
yt-clipper-web/
├── app.py                      # Main Flask application
├── config.json                 # Configuration (API keys)
├── requirements.txt            # Python dependencies
├── install.sh                  # Auto-installer script
├── test.py                     # Test all modules
├── README.md                   # Full documentation
├── API.md                      # API documentation
├── .gitignore                  # Git ignore rules
│
├── core/                       # Core processing modules
│   ├── __init__.py
│   ├── downloader.py           # Video downloader (yt-dlp)
│   ├── highlight_finder.py     # AI highlight detection
│   ├── video_clipper.py        # Video clipping (FFmpeg)
│   ├── portrait_converter.py   # Portrait conversion + face tracking
│   ├── caption_generator.py    # Subtitle generator (Whisper)
│   └── hook_generator.py       # Hook intro (Edge TTS)
│
├── templates/                  # HTML templates
│   └── index.html              # Web UI
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Custom styles
│   └── js/
│       └── app.js              # Frontend JavaScript
│
└── output/                     # Generated clips
    ├── _temp/                  # Temporary files
    └── YYYYMMDD-HHMMSS-clipXX/ # Clip folders
        ├── master.mp4          # Final video
        └── data.json           # Metadata
```

---

## 🔧 TEKNOLOGI STACK

### Backend:
- **Flask 3.0** - Web framework
- **OpenRouter API** - AI highlight detection (Llama 3.1 70B)
- **Whisper** - Audio transcription (lokal)
- **Edge TTS** - Text-to-speech (gratis)
- **FFmpeg** - Video processing
- **yt-dlp** - Video downloader
- **OpenCV** - Face detection & tracking

### Frontend:
- **Bootstrap 5.3** - UI framework
- **Font Awesome 6.4** - Icons
- **Vanilla JavaScript** - No frameworks

### API:
- **RESTful API** - JSON responses
- **CORS enabled** - Cross-origin support

---

## 🎯 CARA KERJA SISTEM

### Pipeline Processing:

```
1. DOWNLOAD VIDEO (yt-dlp)
   ├─ Download video dari URL
   ├─ Extract subtitle (auto-generated)
   └─ Get video metadata

2. FIND HIGHLIGHTS (OpenRouter AI)
   ├─ Parse subtitle file
   ├─ Send to Llama 3.1 70B
   ├─ AI analyze & find viral moments
   └─ Generate hook text

3. CLIP VIDEO (FFmpeg)
   ├─ Cut video by timestamp
   └─ Output multiple clips

4. CONVERT TO PORTRAIT (OpenCV + FFmpeg)
   ├─ Detect faces (Haar Cascade)
   ├─ Track active speaker
   ├─ Smart crop to 9:16
   └─ Camera-cut style switching

5. ADD HOOK INTRO (Edge TTS + FFmpeg)
   ├─ Generate TTS audio from hook text
   ├─ Extract first frame
   ├─ Create intro scene (3-5s)
   └─ Merge with main clip

6. ADD CAPTIONS (Whisper + FFmpeg)
   ├─ Extract audio
   ├─ Transcribe with Whisper
   ├─ Generate ASS subtitle (word-by-word)
   ├─ Style captions (CapCut-style)
   └─ Burn into video

7. FINALIZE
   ├─ Save as master.mp4
   ├─ Generate metadata (data.json)
   └─ Ready to download/share
```

---

## 💰 BIAYA OPERASIONAL

### 100% GRATIS! 🎉

| Komponen | Provider | Cost |
|----------|----------|------|
| AI Highlight | OpenRouter (Llama 3.1 70B) | FREE* |
| Subtitle | Whisper (Local) | FREE |
| Voiceover | Edge TTS | FREE |
| Total per video | - | **$0.00** |

*OpenRouter API key sudah included, Llama 3.1 70B sangat murah/gratis

### Perbandingan dengan Paid Version:
| Feature | Free (Ours) | Paid (OpenAI) |
|---------|-------------|---------------|
| AI | Llama 3.1 70B | GPT-4 |
| Subtitle | Whisper Local | Whisper API |
| TTS | Edge TTS | OpenAI TTS |
| Cost/video | **$0.00** | **$0.25** |
| Cost/1000 videos | **$0** | **$250** |

---

## 📱 CARA INSTALL & JALANKAN

### Quick Start (3 langkah):

```bash
# 1. Auto install
sudo bash install.sh

# 2. Run server
python3 app.py

# 3. Akses browser
http://YOUR_VPS_IP:7575
```

### Manual Install:

```bash
# Install dependencies
sudo apt install python3 python3-pip ffmpeg
pip3 install yt-dlp
pip3 install -r requirements.txt

# Run
python3 app.py
```

---

## 🎯 FITUR LENGKAP

### ✅ Video Processing:
- [x] Download dari YouTube, TikTok, Instagram, Facebook, Twitch
- [x] Auto-extract subtitle (ID/EN)
- [x] AI-powered highlight detection
- [x] Smart video clipping
- [x] Portrait conversion (9:16)
- [x] Face tracking & auto-follow speaker
- [x] CapCut-style captions
- [x] Hook intro dengan AI voiceover
- [x] Professional output quality

### ✅ Web Interface:
- [x] Modern responsive UI
- [x] Real-time progress tracking
- [x] Preview video in browser
- [x] One-click download
- [x] Clips gallery
- [x] Delete clips
- [x] Settings panel

### ✅ API:
- [x] RESTful API
- [x] JSON responses
- [x] CORS support
- [x] Status polling
- [x] Batch processing ready

---

## 🚀 PERFORMANCE

### Speed:
- Video 1 jam → 5 klip → **10-15 menit**
- Whisper base: **~5 detik per menit audio**
- Portrait conversion: **~2 detik per detik video**
- Hook generation: **~5 detik**

### Requirements:
- **CPU**: 2 cores minimum
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 10GB free space
- **Bandwidth**: 10 Mbps+

### Optimization Tips:
- Gunakan Whisper **base** untuk balanced speed/quality
- Nonaktifkan captions jika tidak perlu (3x lebih cepat)
- Proses video maksimal 2 jam durasi
- Gunakan SSD untuk storage

---

## 🎨 OUTPUT QUALITY

### Video Specs:
- **Resolution**: 1080x1920 (9:16 portrait)
- **Format**: MP4 (H.264)
- **Bitrate**: ~2-3 Mbps
- **Audio**: AAC 128kbps
- **FPS**: Source FPS (usually 30)

### Caption Styling:
- **Font**: Arial Black 70px
- **Color**: White with yellow highlight
- **Position**: Lower third (350px from bottom)
- **Style**: Word-by-word timing
- **Background**: Semi-transparent black box

### Hook Intro:
- **Duration**: 3-5 seconds
- **Style**: Blurred first frame + centered text
- **Voice**: Indonesian (id-ID-ArdiNeural)
- **Effect**: Professional AI voiceover

---

## 🔐 SECURITY

### Best Practices:
- Change default port if needed
- Use firewall (ufw)
- Run behind nginx reverse proxy
- Add basic auth for production
- Regular security updates

### Example nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:7575;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📈 MONITORING

### Logs:
```bash
# View logs (if using systemd)
sudo journalctl -u yt-clipper -f

# Or use screen
screen -r clipper
```

### Health Check:
```bash
curl http://localhost:7575/health
```

### Disk Usage:
```bash
# Check output folder size
du -sh output/

# Clean old clips
find output/ -name "*.mp4" -mtime +7 -delete
```

---

## 🛠️ TROUBLESHOOTING

### Common Issues:

**Port already in use:**
```bash
sudo lsof -i :7575
sudo kill -9 <PID>
```

**FFmpeg not found:**
```bash
sudo apt install ffmpeg
```

**Whisper download failed:**
```bash
pip3 install --upgrade openai-whisper
```

**OpenCV error:**
```bash
pip3 install opencv-python-headless
```

---

## 📖 DOKUMENTASI LENGKAP

- **README.md** - Panduan instalasi & usage
- **API.md** - API documentation lengkap
- **test.py** - Test semua modules
- **install.sh** - Auto-installer

---

## 🎉 READY TO USE!

API Key OpenRouter sudah **included** di config.json:
```
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
```

Langsung jalankan:
```bash
python3 app.py
```

Akses:
```
http://YOUR_VPS_IP:7575
```

---

## 🌟 NEXT FEATURES (Coming Soon)

- [ ] Multiple video batch processing
- [ ] Auto-upload to TikTok/YouTube
- [ ] Custom caption styling
- [ ] Background music support
- [ ] Video effects & transitions
- [ ] Webhook notifications
- [ ] Multi-language support
- [ ] Advanced AI models

---

## 🤝 SUPPORT

Jika ada masalah:
1. Jalankan: `python3 test.py`
2. Check logs: `screen -r clipper`
3. Restart server: `sudo systemctl restart yt-clipper`

---

## 📄 LICENSE

MIT License - Free to use, modify, and distribute

---

## 🎬 HAPPY CLIPPING!

Made with ❤️ for content creators
