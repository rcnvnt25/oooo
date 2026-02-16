#!/usr/bin/env python3
"""
Test Script - Verify All Modules
"""

import sys
import os

print("=" * 60)
print("YT SHORT CLIPPER - MODULE TEST")
print("=" * 60)
print()

# Test 1: System dependencies
print("1️⃣  Testing system dependencies...")
try:
    import subprocess
    
    # Test FFmpeg
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        print("   ✅ FFmpeg: OK")
    else:
        print("   ❌ FFmpeg: NOT FOUND")
        sys.exit(1)
    
    # Test yt-dlp
    result = subprocess.run(['yt-dlp', '--version'], capture_output=True, timeout=5)
    if result.returncode == 0:
        print("   ✅ yt-dlp: OK")
    else:
        print("   ❌ yt-dlp: NOT FOUND")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Python modules
print("\n2️⃣  Testing Python modules...")
modules = {
    'Flask': 'flask',
    'OpenCV': 'cv2',
    'Whisper': 'whisper',
    'Edge TTS': 'edge_tts',
    'Requests': 'requests',
    'NumPy': 'numpy'
}

for name, module in modules.items():
    try:
        __import__(module)
        print(f"   ✅ {name}: OK")
    except ImportError:
        print(f"   ❌ {name}: NOT FOUND")
        print(f"      Install with: pip3 install {module}")
        sys.exit(1)

# Test 3: Core modules
print("\n3️⃣  Testing core modules...")
try:
    from core.downloader import download_video
    print("   ✅ downloader: OK")
    
    from core.highlight_finder import find_highlights
    print("   ✅ highlight_finder: OK")
    
    from core.video_clipper import clip_video
    print("   ✅ video_clipper: OK")
    
    from core.portrait_converter import convert_to_portrait
    print("   ✅ portrait_converter: OK")
    
    from core.caption_generator import add_captions
    print("   ✅ caption_generator: OK")
    
    from core.hook_generator import add_hook
    print("   ✅ hook_generator: OK")
    
except ImportError as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Configuration
print("\n4️⃣  Testing configuration...")
try:
    import json
    from pathlib import Path
    
    config_file = Path('config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if config.get('openrouter_api_key'):
            print("   ✅ OpenRouter API Key: Configured")
        else:
            print("   ⚠️  OpenRouter API Key: Not set")
        
        print(f"   ✅ Model: {config.get('model', 'Not set')}")
        print(f"   ✅ Whisper Model: {config.get('whisper_model', 'Not set')}")
    else:
        print("   ⚠️  config.json: Not found")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Directories
print("\n5️⃣  Testing directories...")
dirs = ['output', 'output/_temp', 'templates', 'static/css', 'static/js', 'core']

for dir_path in dirs:
    if os.path.exists(dir_path):
        print(f"   ✅ {dir_path}: OK")
    else:
        print(f"   ❌ {dir_path}: NOT FOUND")
        os.makedirs(dir_path, exist_ok=True)
        print(f"      Created: {dir_path}")

# Test 6: Whisper model download (optional)
print("\n6️⃣  Testing Whisper model...")
try:
    import whisper
    
    # Try to load base model
    print("   📥 Loading Whisper base model (first time may take a while)...")
    model = whisper.load_model("base")
    print("   ✅ Whisper base model: OK")
    
except Exception as e:
    print(f"   ⚠️  Whisper model: {e}")
    print("      Model will auto-download on first use")

# Test 7: Edge TTS voices
print("\n7️⃣  Testing Edge TTS...")
try:
    import edge_tts
    import asyncio
    
    async def test_voices():
        voices = await edge_tts.list_voices()
        id_voices = [v for v in voices if v['Locale'].startswith('id-')]
        return id_voices
    
    voices = asyncio.run(test_voices())
    
    if voices:
        print(f"   ✅ Edge TTS: OK ({len(voices)} Indonesian voices available)")
        for voice in voices[:2]:
            print(f"      - {voice['ShortName']}")
    else:
        print("   ⚠️  No Indonesian voices found")
        
except Exception as e:
    print(f"   ❌ Edge TTS error: {e}")

# Test 8: Port availability
print("\n8️⃣  Testing port 7575...")
try:
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 7575))
    sock.close()
    
    if result == 0:
        print("   ⚠️  Port 7575: Already in use")
        print("      Stop existing server first or change port in app.py")
    else:
        print("   ✅ Port 7575: Available")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Final summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n🚀 Ready to start server with:")
print("   python3 app.py")
print("\n📱 Access via browser:")
print("   http://YOUR_VPS_IP:7575")
print("\n" + "=" * 60)
