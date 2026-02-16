# 🚀 QUICK START GUIDE

## Install di VPS (Ubuntu/Debian)

```bash
# 1. Upload folder yt-clipper-web ke VPS
# Via SCP:
scp -r yt-clipper-web root@YOUR_VPS_IP:/root/

# Atau extract tar.gz:
tar -xzf yt-clipper-web.tar.gz
cd yt-clipper-web

# 2. Run auto-installer
sudo bash install.sh

# 3. Start server
python3 app.py
```

## Akses Web Interface

Buka browser:
```
http://YOUR_VPS_IP:7575
```

## Cara Pakai

1. **Paste URL** video (YouTube/TikTok/Instagram/Facebook/Twitch)
2. **Pilih jumlah klip** (1-10)
3. **Centang opsi**:
   - ✅ Tambah Subtitle
   - ✅ Tambah Hook Intro
4. **Klik "Mulai Proses"**
5. **Tunggu** hingga selesai (progress bar real-time)
6. **Download** hasil klip

## API Key

✅ **Sudah included!** OpenRouter API key sudah dikonfigurasi di `config.json`

## Test Instalasi

```bash
python3 test.py
```

## File Penting

- `README.md` - Dokumentasi lengkap
- `API.md` - API documentation
- `SUMMARY.md` - Project overview
- `config.json` - Configuration (API key)

## Run as Service (Auto-start)

```bash
# Install service
sudo bash install.sh
# Pilih 'y' saat ditanya install systemd service

# Start
sudo systemctl start yt-clipper

# Status
sudo systemctl status yt-clipper

# Stop
sudo systemctl stop yt-clipper
```

## 🎉 Done!

Server running di `http://YOUR_VPS_IP:7575`

**100% FREE** - No API costs! 🎊
