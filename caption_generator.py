"""
Caption Generator Module
Adds CapCut-style captions using Whisper (local)
"""

import subprocess
import whisper
import os
from pathlib import Path
import json

def add_captions(video_path, output_dir, model_size="base"):
    """
    Add CapCut-style captions to video using Whisper
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save output
        model_size: Whisper model (tiny/base/small/medium/large)
    
    Returns:
        str: Path to captioned video
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "captioned.mp4"
    audio_path = output_dir / "audio.wav"
    srt_path = output_dir / "captions.srt"
    ass_path = output_dir / "captions.ass"
    
    print(f"📝 Adding captions with Whisper ({model_size})...")
    
    try:
        # Step 1: Extract audio
        print("  🔊 Extracting audio...")
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-y",
            str(audio_path)
        ]
        
        subprocess.run(cmd, capture_output=True, timeout=120)
        
        if not audio_path.exists():
            raise Exception("Failed to extract audio")
        
        # Step 2: Transcribe with Whisper
        print(f"  🤖 Transcribing audio (model: {model_size})...")
        
        model = whisper.load_model(model_size)
        result = model.transcribe(
            str(audio_path),
            language="id",  # Indonesian
            word_timestamps=True,
            verbose=False
        )
        
        # Step 3: Generate SRT with word-level timing
        print("  ✍️ Generating captions...")
        
        segments = []
        segment_id = 1
        
        for segment in result['segments']:
            if 'words' in segment:
                # Word-by-word captions
                for word_data in segment['words']:
                    word = word_data['word'].strip()
                    start = word_data['start']
                    end = word_data['end']
                    
                    segments.append({
                        'id': segment_id,
                        'start': start,
                        'end': end,
                        'text': word
                    })
                    segment_id += 1
            else:
                # Fallback: segment-level
                segments.append({
                    'id': segment_id,
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
                segment_id += 1
        
        # Write SRT file
        with open(srt_path, 'w', encoding='utf-8') as f:
            for seg in segments:
                start_time = format_timestamp(seg['start'])
                end_time = format_timestamp(seg['end'])
                
                f.write(f"{seg['id']}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{seg['text']}\n")
                f.write("\n")
        
        # Step 4: Convert to ASS with CapCut styling
        print("  🎨 Styling captions...")
        
        create_ass_file(segments, ass_path)
        
        # Step 5: Burn captions into video
        print("  🔥 Burning captions...")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"ass={ass_path}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "copy",
            "-y",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Cleanup
        if audio_path.exists():
            audio_path.unlink()
        
        if not output_path.exists():
            raise Exception(f"Failed to create output: {result.stderr}")
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Captions added: {output_path} ({file_size:.2f} MB)")
        
        return str(output_path)
        
    except Exception as e:
        # Cleanup on error
        for path in [audio_path, srt_path, ass_path]:
            if path.exists():
                path.unlink()
        
        raise Exception(f"Caption generation failed: {str(e)}")

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def create_ass_file(segments, output_path):
    """
    Create ASS subtitle file with CapCut-style formatting
    """
    # ASS header with styling
    ass_content = """[Script Info]
Title: CapCut Style Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial Black,70,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,10,10,350,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Add dialogue lines
    for seg in segments:
        start = format_ass_time(seg['start'])
        end = format_ass_time(seg['end'])
        text = seg['text'].replace('\n', ' ')
        
        # Highlight current word with yellow
        highlighted = f"{{\\c&H00FFFF&}}{text}{{\\c&HFFFFFF&}}"
        
        ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{highlighted}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)

def format_ass_time(seconds):
    """Convert seconds to ASS timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:01d}:{minutes:02d}:{secs:05.2f}"

if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python caption_generator.py <video_path> [model_size]")
        sys.exit(1)
    
    video = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "base"
    
    try:
        output = add_captions(video, "test_output", model)
        print(f"✅ Success: {output}")
    except Exception as e:
        print(f"❌ Error: {e}")
