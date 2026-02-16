# 🖥️ INSTALL DI VPS TANPA GUI (HEADLESS)

## ✅ CONFIRMED: 100% COMPATIBLE!

Sistem ini **DIRANCANG** untuk VPS headless. Tidak perlu GUI sama sekali!

---

## 🚀 STEP-BY-STEP INSTALL

### 1️⃣ Login SSH ke VPS

```bash
ssh root@YOUR_VPS_IP
# Atau: ssh user@YOUR_VPS_IP
```

### 2️⃣ Upload Project ke VPS

**Option A: Via SCP (dari komputer Anda)**
```bash
# Di komputer lokal:
scp yt-clipper-web.tar.gz root@YOUR_VPS_IP:/root/
```

**Option B: Download langsung di VPS**
```bash
# Di VPS:
wget https://your-server.com/yt-clipper-web.tar.gz
# Atau upload manual via SFTP
```

### 3️⃣ Extract & Masuk Folder

```bash
cd /root/
tar -xzf yt-clipper-web.tar.gz
cd yt-clipper-web
```

### 4️⃣ Fix Requirements (PENTING!)

```bash
# Edit requirements.txt untuk headless
sed -i 's/opencv-python==/opencv-python-headless==/g' requirements.txt

# Atau manual:
nano requirements.txt
# Ganti: opencv-python==4.8.1.78
# Dengan: opencv-python-headless==4.8.1.78
```

### 5️⃣ Run Auto Installer

```bash
sudo bash install.sh
```

Installer akan:
- ✅ Install system dependencies (FFmpeg, Python, etc)
- ✅ Install yt-dlp
- ✅ Install Python packages (headless compatible)
- ✅ Test semua modules
- ✅ Setup systemd service (optional)

### 6️⃣ Start Server

**Option A: Direct (foreground)**
```bash
python3 app.py
```

**Option B: Screen (recommended)**
```bash
screen -S clipper
python3 app.py
# Tekan Ctrl+A+D untuk detach
# Untuk attach kembali: screen -r clipper
```

**Option C: Systemd Service (auto-restart)**
```bash
# Jika sudah install service saat install.sh
sudo systemctl start yt-clipper
sudo systemctl enable yt-clipper  # Auto-start on boot
sudo systemctl status yt-clipper  # Check status
```

**Option D: Nohup (background)**
```bash
nohup python3 app.py > server.log 2>&1 &
# View logs: tail -f server.log
```

---

## 🌐 AKSES WEB INTERFACE

### Dari Browser (komputer/HP):

```
http://YOUR_VPS_IP:7575
```

### Test dari VPS:

```bash
# Test health endpoint
curl http://localhost:7575/health

# Expected output:
# {"status":"healthy","version":"1.0.0","timestamp":"..."}
```

---

## 🔥 FIREWALL SETUP

Buka port 7575:

```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 7575/tcp
sudo ufw reload

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=7575/tcp
sudo firewall-cmd --reload
```

---

## 🧪 TEST INSTALASI

```bash
# Run test script
python3 test.py
```

Output harus:
```
✅ FFmpeg: OK
✅ yt-dlp: OK
✅ Flask: OK
✅ OpenCV: OK (headless)
✅ Whisper: OK
✅ Edge TTS: OK
✅ Port 7575: Available
```

---

## 🐛 TROUBLESHOOTING HEADLESS

### Error: "No module named 'cv2'"

```bash
pip3 uninstall opencv-python
pip3 install opencv-python-headless
```

### Error: "cannot open display"

Anda menggunakan `opencv-python` biasa. Harus pakai `opencv-python-headless`:

```bash
pip3 uninstall opencv-python
pip3 install opencv-python-headless --break-system-packages
```

### Error: "libGL.so.1: cannot open shared object"

Install library yang diperlukan:

```bash
sudo apt install -y libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1
```

### Error: "Port 7575 already in use"

```bash
# Cari process yang pakai port
sudo lsof -i :7575

# Kill process
sudo kill -9 <PID>
```

### Whisper model download lambat/gagal

```bash
# Download manual
python3 << EOF
import whisper
whisper.load_model("base")
EOF
```

---

## 📊 MONITORING SERVER

### Check if server running:

```bash
# Via systemd
sudo systemctl status yt-clipper

# Via screen
screen -ls
screen -r clipper

# Via process
ps aux | grep app.py

# Via port
netstat -tlnp | grep 7575
```

### View logs:

```bash
# Systemd logs
sudo journalctl -u yt-clipper -f

# Nohup logs
tail -f server.log

# Screen session
screen -r clipper
```

### Check disk usage:

```bash
# Output folder size
du -sh /root/yt-clipper-web/output/

# Clean old clips (older than 7 days)
find /root/yt-clipper-web/output/ -name "*.mp4" -mtime +7 -delete
```

---

## 🔄 RESTART SERVER

```bash
# Systemd
sudo systemctl restart yt-clipper

# Screen
screen -r clipper
# Ctrl+C to stop
python3 app.py
# Ctrl+A+D to detach

# Nohup
pkill -f app.py
nohup python3 app.py > server.log 2>&1 &
```

---

## 🔐 PRODUCTION TIPS

### 1. Run as Service (Auto-restart)

Systemd service sudah dibuat saat instalasi. Enable auto-start:

```bash
sudo systemctl enable yt-clipper
```

### 2. Reverse Proxy (nginx)

Agar bisa akses via domain:

```bash
# Install nginx
sudo apt install nginx

# Create config
sudo nano /etc/nginx/sites-available/clipper

# Paste:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7575;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        client_max_body_size 1G;
    }
}

# Enable & restart
sudo ln -s /etc/nginx/sites-available/clipper /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. SSL Certificate (HTTPS)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renew
sudo certbot renew --dry-run
```

---

## ✅ CHECKLIST FINAL

- [ ] SSH login ke VPS berhasil
- [ ] Project uploaded & extracted
- [ ] requirements.txt sudah di-fix (opencv-python-headless)
- [ ] install.sh berhasil dijalankan
- [ ] python3 test.py semua ✅
- [ ] Server running (systemd/screen/nohup)
- [ ] Port 7575 terbuka di firewall
- [ ] Web interface bisa diakses dari browser
- [ ] Test upload 1 video berhasil

---

## 🎉 DONE!

Server running di VPS tanpa GUI!

**Akses**: `http://YOUR_VPS_IP:7575`

**100% Compatible** dengan VPS headless! 🚀
