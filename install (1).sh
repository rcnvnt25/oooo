#!/bin/bash

# YT Short Clipper - Auto Installer Script
# Jalankan dengan: bash install.sh

echo "=================================================="
echo "  YT SHORT CLIPPER - AUTO INSTALLER"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Script ini memerlukan sudo access"
    echo "Jalankan dengan: sudo bash install.sh"
    exit 1
fi

echo "📦 Step 1: Installing system dependencies..."
apt update
apt install -y python3 python3-pip python3-venv ffmpeg git

echo ""
echo "📦 Step 2: Installing yt-dlp..."
pip3 install yt-dlp

echo ""
echo "📦 Step 3: Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🔍 Step 4: Testing installations..."

# Test FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg: OK"
else
    echo "❌ FFmpeg: NOT FOUND"
    exit 1
fi

# Test yt-dlp
if command -v yt-dlp &> /dev/null; then
    echo "✅ yt-dlp: OK"
else
    echo "❌ yt-dlp: NOT FOUND"
    exit 1
fi

# Test Python modules
python3 << EOF
try:
    import flask
    import whisper
    import cv2
    import edge_tts
    import requests
    print("✅ Python modules: OK")
except ImportError as e:
    print(f"❌ Python modules: MISSING - {e}")
    exit(1)
EOF

echo ""
echo "🔧 Step 5: Setting up directories..."
mkdir -p output/_temp
chmod 755 output

echo ""
echo "🎯 Step 6: Creating systemd service (optional)..."
read -p "Install as systemd service? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    CURRENT_DIR=$(pwd)
    
    cat > /etc/systemd/system/yt-clipper.service << EOF
[Unit]
Description=YT Short Clipper Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${CURRENT_DIR}
ExecStart=/usr/bin/python3 ${CURRENT_DIR}/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable yt-clipper
    
    echo "✅ Systemd service created!"
    echo "   Start with: sudo systemctl start yt-clipper"
    echo "   Stop with: sudo systemctl stop yt-clipper"
    echo "   Status: sudo systemctl status yt-clipper"
fi

echo ""
echo "=================================================="
echo "  ✅ INSTALLATION COMPLETE!"
echo "=================================================="
echo ""
echo "🚀 To start the server:"
echo "   1. Manual: python3 app.py"
echo "   2. Screen: screen -S clipper && python3 app.py"
echo "   3. Service: sudo systemctl start yt-clipper"
echo ""
echo "📱 Access via browser:"
echo "   http://YOUR_VPS_IP:7575"
echo ""
echo "🔑 API Key: Already configured!"
echo ""
echo "📖 Full documentation: README.md"
echo "=================================================="
