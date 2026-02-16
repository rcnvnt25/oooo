"""
Hook Generator Module
Adds intro scene with text overlay and AI voiceover (Edge TTS - Free)
"""

import subprocess
import os
from pathlib import Path
import asyncio
import edge_tts

async def generate_tts_audio(text, output_path, voice="id-ID-ArdiNeural"):
    """
    Generate TTS audio using Edge TTS (Microsoft - Free)
    
    Args:
        text: Text to convert to speech
        output_path: Path to save audio
        voice: Voice ID (Indonesian voices: id-ID-ArdiNeural, id-ID-GadisNeural)
    """
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def add_hook(video_path, hook_text, output_dir):
    """
    Add hook intro scene to video
    
    Args:
        video_path: Path to input video
        hook_text: Hook text to display
        output_dir: Directory to save output
    
    Returns:
        str: Path to hooked video
    """
    if not hook_text or len(hook_text.strip()) == 0:
        print("⚠️ No hook text, skipping hook generation")
        return video_path
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "hooked.mp4"
    hook_video_path = output_dir / "hook_scene.mp4"
    tts_audio_path = output_dir / "hook_voice.mp3"
    first_frame_path = output_dir / "first_frame.jpg"
    
    print(f"🎣 Adding hook: '{hook_text}'")
    
    try:
        # Step 1: Extract first frame
        print("  📸 Extracting first frame...")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vframes", "1",
            "-y",
            str(first_frame_path)
        ]
        
        subprocess.run(cmd, capture_output=True, timeout=30)
        
        if not first_frame_path.exists():
            raise Exception("Failed to extract first frame")
        
        # Step 2: Generate TTS voiceover
        print("  🔊 Generating voiceover...")
        
        # Use asyncio to run Edge TTS
        asyncio.run(generate_tts_audio(hook_text, str(tts_audio_path)))
        
        if not tts_audio_path.exists():
            raise Exception("Failed to generate TTS audio")
        
        # Get TTS duration
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(tts_audio_path)
        ]
        
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        tts_duration = float(result.stdout.strip())
        
        # Add padding (0.5s at start, 0.3s at end)
        hook_duration = tts_duration + 0.8
        
        print(f"  ⏱️ Hook duration: {hook_duration:.1f}s")
        
        # Step 3: Create hook scene video
        print("  🎨 Creating hook scene...")
        
        # Clean hook text for drawtext (escape special chars)
        clean_text = hook_text.replace("'", "\\'").replace(":", "\\:")
        
        # Split text into multiple lines if too long
        max_chars_per_line = 25
        words = clean_text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > max_chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Join lines with newline
        multiline_text = '\\n'.join(lines)
        
        # FFmpeg command to create hook scene
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", str(first_frame_path),
            "-i", str(tts_audio_path),
            "-filter_complex",
            f"[0:v]scale=1080:1920,gblur=sigma=20,eq=brightness=-0.2[blurred];"
            f"[blurred]drawtext="
            f"text='{multiline_text}':"
            f"fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"fontsize=60:"
            f"fontcolor=white:"
            f"borderw=4:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"box=1:"
            f"boxcolor=black@0.5:"
            f"boxborderw=20[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-t", str(hook_duration),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-shortest",
            "-y",
            str(hook_video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if not hook_video_path.exists():
            raise Exception(f"Failed to create hook scene: {result.stderr}")
        
        # Step 4: Concatenate hook + original video
        print("  🔗 Merging hook with video...")
        
        concat_file = output_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            f.write(f"file '{hook_video_path.absolute()}'\n")
            f.write(f"file '{Path(video_path).absolute()}'\n")
        
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            "-y",
            str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True, timeout=120)
        
        # Cleanup temp files
        for path in [first_frame_path, tts_audio_path, hook_video_path, concat_file]:
            if path.exists():
                path.unlink()
        
        if not output_path.exists():
            raise Exception("Failed to create final output")
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Hook added: {output_path} ({file_size:.2f} MB)")
        
        return str(output_path)
        
    except Exception as e:
        # Cleanup on error
        for path in [first_frame_path, tts_audio_path, hook_video_path]:
            if path.exists():
                path.unlink()
        
        raise Exception(f"Hook generation failed: {str(e)}")

def test_edge_tts():
    """Test Edge TTS installation and available voices"""
    async def list_voices():
        voices = await edge_tts.list_voices()
        print("Available Indonesian voices:")
        for voice in voices:
            if voice['Locale'].startswith('id-'):
                print(f"  - {voice['ShortName']}: {voice['Gender']}")
    
    asyncio.run(list_voices())

if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python hook_generator.py <video_path> <hook_text>")
        print("\nOr test voices:")
        print("python hook_generator.py --test-voices")
        sys.exit(1)
    
    if sys.argv[1] == "--test-voices":
        test_edge_tts()
    else:
        video = sys.argv[1]
        hook = sys.argv[2]
        
        try:
            output = add_hook(video, hook, "test_output")
            print(f"✅ Success: {output}")
        except Exception as e:
            print(f"❌ Error: {e}")
