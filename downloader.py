"""
Video Downloader Module
Supports: YouTube, TikTok, Instagram, Facebook, Twitch
"""

import os
import subprocess
import json
from pathlib import Path

def download_video(url, output_dir):
    """
    Download video from various platforms using yt-dlp
    
    Args:
        url: Video URL (YouTube, TikTok, Instagram, Facebook, Twitch)
        output_dir: Directory to save video
    
    Returns:
        tuple: (video_path, subtitle_path, video_info)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Output template
    video_output = str(output_dir / "source.%(ext)s")
    subtitle_output = str(output_dir / "source")
    
    print(f"📥 Downloading video from: {url}")
    
    # Download video with subtitles
    cmd = [
        "yt-dlp",
        "--format", "best[height<=1080]",  # Max 1080p
        "--write-auto-sub",  # Auto-generated subtitles
        "--write-sub",  # Manual subtitles
        "--sub-lang", "id,en",  # Indonesian and English
        "--convert-subs", "srt",  # Convert to SRT format
        "--output", video_output,
        "--no-warnings",
        "--no-progress",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ Download error: {result.stderr}")
            raise Exception(f"Failed to download video: {result.stderr}")
        
        # Find downloaded video file
        video_path = None
        for ext in ['mp4', 'webm', 'mkv']:
            potential_path = output_dir / f"source.{ext}"
            if potential_path.exists():
                video_path = str(potential_path)
                break
        
        if not video_path:
            raise Exception("Video file not found after download")
        
        # Find subtitle file
        subtitle_path = None
        for lang in ['id', 'en']:
            for ext in ['srt', 'vtt']:
                potential_sub = output_dir / f"source.{lang}.{ext}"
                if potential_sub.exists():
                    subtitle_path = str(potential_sub)
                    print(f"✅ Found subtitle: {lang}.{ext}")
                    break
            if subtitle_path:
                break
        
        # If no subtitle found, try to extract from video metadata or generate
        if not subtitle_path:
            print("⚠️ No subtitle found, will generate from audio later")
            subtitle_path = str(output_dir / "source.id.srt")
        
        # Get video info
        video_info = get_video_info(url)
        
        # Save video info
        info_path = output_dir / "video_info.json"
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(video_info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Video downloaded: {video_path}")
        print(f"✅ Subtitle: {subtitle_path}")
        
        return video_path, subtitle_path, video_info
        
    except subprocess.TimeoutExpired:
        raise Exception("Download timeout (>5 minutes)")
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

def get_video_info(url):
    """Get video metadata using yt-dlp"""
    try:
        cmd = [
            "yt-dlp",
            "--dump-json",
            "--no-warnings",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            info = json.loads(result.stdout)
            return {
                "title": info.get("title", "Unknown"),
                "description": info.get("description", ""),
                "duration": info.get("duration", 0),
                "uploader": info.get("uploader", "Unknown"),
                "upload_date": info.get("upload_date", ""),
                "view_count": info.get("view_count", 0)
            }
    except:
        pass
    
    return {
        "title": "Unknown Video",
        "description": "",
        "duration": 0,
        "uploader": "Unknown",
        "upload_date": "",
        "view_count": 0
    }

def extract_audio_for_transcription(video_path, output_dir):
    """Extract audio from video for transcription (if no subtitle)"""
    output_dir = Path(output_dir)
    audio_path = output_dir / "audio.wav"
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # WAV format
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",  # Mono
        "-y",  # Overwrite
        str(audio_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=120)
        if audio_path.exists():
            return str(audio_path)
    except:
        pass
    
    return None

if __name__ == "__main__":
    # Test download
    test_url = input("Enter video URL: ")
    output = Path("test_downloads")
    
    try:
        video, subtitle, info = download_video(test_url, output)
        print(f"\n✅ Success!")
        print(f"Video: {video}")
        print(f"Subtitle: {subtitle}")
        print(f"Info: {info}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
