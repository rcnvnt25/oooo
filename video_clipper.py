"""
Video Clipper Module
Clips video based on highlight timestamps
"""

import subprocess
import os
from pathlib import Path

def srt_to_seconds(srt_time):
    """Convert SRT timestamp to seconds"""
    time_part = srt_time.split(',')[0]
    h, m, s = map(int, time_part.split(':'))
    ms = int(srt_time.split(',')[1])
    return h * 3600 + m * 60 + s + ms / 1000

def clip_video(video_path, highlight, output_dir):
    """
    Clip video segment using FFmpeg
    
    Args:
        video_path: Path to source video
        highlight: Highlight dictionary with start_time and end_time
        output_dir: Directory to save clip
    
    Returns:
        str: Path to clipped video
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    start_time = highlight['start_time']
    end_time = highlight['end_time']
    
    # Calculate duration
    start_sec = srt_to_seconds(start_time)
    end_sec = srt_to_seconds(end_time)
    duration = end_sec - start_sec
    
    # Output path
    output_path = output_dir / "clipped.mp4"
    
    print(f"✂️ Clipping video: {start_time} -> {end_time} ({duration}s)")
    
    # FFmpeg command
    # Using -ss before -i for faster seeking
    # Using -t for duration instead of -to
    cmd = [
        "ffmpeg",
        "-ss", str(start_sec),  # Start time
        "-i", video_path,  # Input
        "-t", str(duration),  # Duration
        "-c:v", "libx264",  # Video codec
        "-preset", "fast",  # Encoding speed
        "-crf", "23",  # Quality (18-28, lower = better)
        "-c:a", "aac",  # Audio codec
        "-b:a", "128k",  # Audio bitrate
        "-movflags", "+faststart",  # Web optimization
        "-y",  # Overwrite
        str(output_path)
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        if not output_path.exists():
            raise Exception("Output file not created")
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print(f"✅ Clip created: {output_path} ({file_size:.2f} MB)")
        
        return str(output_path)
        
    except subprocess.TimeoutExpired:
        raise Exception("Clipping timeout (>5 minutes)")
    except Exception as e:
        raise Exception(f"Clipping failed: {str(e)}")

def merge_videos(video_paths, output_path):
    """
    Merge multiple videos into one
    
    Args:
        video_paths: List of video paths
        output_path: Output path for merged video
    
    Returns:
        str: Path to merged video
    """
    # Create concat file
    concat_file = Path(output_path).parent / "concat.txt"
    
    with open(concat_file, 'w') as f:
        for video in video_paths:
            f.write(f"file '{video}'\n")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        "-y",
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=180)
        
        if concat_file.exists():
            concat_file.unlink()
        
        return str(output_path)
    except:
        if concat_file.exists():
            concat_file.unlink()
        raise

if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python video_clipper.py <video_path> <start_time> <end_time>")
        sys.exit(1)
    
    video = sys.argv[1]
    start = sys.argv[2]
    end = sys.argv[3]
    
    highlight = {
        "start_time": start,
        "end_time": end
    }
    
    try:
        output = clip_video(video, highlight, "test_output")
        print(f"✅ Success: {output}")
    except Exception as e:
        print(f"❌ Error: {e}")
