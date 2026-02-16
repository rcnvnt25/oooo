"""
AI Highlight Finder using OpenRouter API
Finds engaging segments from video subtitles
"""

import requests
import json
import re
from datetime import timedelta

def parse_srt_file(srt_path):
    """Parse SRT subtitle file"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newline
    blocks = content.strip().split('\n\n')
    
    subtitles = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # Parse timestamp
            time_line = lines[1]
            match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})', time_line)
            
            if match:
                start_time = f"{match.group(1)}:{match.group(2)}:{match.group(3)},{match.group(4)}"
                end_time = f"{match.group(5)}:{match.group(6)}:{match.group(7)},{match.group(8)}"
                
                # Get text (can be multiple lines)
                text = ' '.join(lines[2:])
                
                subtitles.append({
                    'start': start_time,
                    'end': end_time,
                    'text': text
                })
    
    return subtitles

def srt_to_seconds(srt_time):
    """Convert SRT timestamp to seconds"""
    time_part = srt_time.split(',')[0]
    h, m, s = map(int, time_part.split(':'))
    ms = int(srt_time.split(',')[1])
    return h * 3600 + m * 60 + s + ms / 1000

def seconds_to_srt(seconds):
    """Convert seconds to SRT timestamp"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

def find_highlights(subtitle_path, num_clips, api_key, model="meta-llama/llama-3.1-70b-instruct"):
    """
    Find highlight segments using OpenRouter API
    
    Args:
        subtitle_path: Path to SRT subtitle file
        num_clips: Number of clips to generate
        api_key: OpenRouter API key
        model: Model to use (default: Llama 3.1 70B)
    
    Returns:
        list: List of highlight dictionaries
    """
    print(f"🤖 Finding highlights with AI ({model})...")
    
    # Parse subtitle
    subtitles = parse_srt_file(subtitle_path)
    
    if not subtitles:
        raise Exception("No subtitles found in file")
    
    # Create transcript with timestamps
    transcript_parts = []
    for i, sub in enumerate(subtitles):
        transcript_parts.append(f"[{sub['start']}] {sub['text']}")
    
    transcript = '\n'.join(transcript_parts)
    
    # Prepare prompt
    prompt = f"""Kamu adalah AI expert untuk menemukan momen viral dari video.

Tugas: Analisis transkrip video berikut dan temukan {num_clips} segmen paling menarik untuk dijadikan konten short-form (TikTok/Reels/Shorts).

KRITERIA SEGMEN MENARIK:
1. Momen lucu / punchline
2. Insight berharga / mind-blowing facts
3. Momen dramatis / emosional
4. Quote memorable
5. Story arc lengkap (ada pembukaan-klimaks-penutup)
6. Kontroversi / opini kuat
7. Tutorial / tips praktis

DURASI:
- Minimum: 30 detik
- Maximum: 120 detik
- Ideal: 60-90 detik

TRANSKRIP:
{transcript}

OUTPUT FORMAT (JSON):
{{
  "highlights": [
    {{
      "title": "Judul menarik (maks 60 karakter, clickbait tapi akurat)",
      "description": "Deskripsi singkat untuk caption (maks 150 karakter)",
      "hook_text": "Kalimat hook untuk opening (maks 10 kata, attention-grabbing)",
      "start_time": "HH:MM:SS,mmm",
      "end_time": "HH:MM:SS,mmm",
      "duration": durasi_dalam_detik,
      "reason": "Kenapa segmen ini menarik"
    }}
  ]
}}

PENTING:
- Pastikan start_time dan end_time valid sesuai transkrip
- Durasi harus 30-120 detik
- Hook text harus sangat menarik perhatian
- Title harus clickbait tapi tidak bohong
- Berikan {num_clips} segmen terbaik, urutkan dari yang paling menarik

RESPONSE HARUS PURE JSON, TANPA MARKDOWN ATAU PENJELASAN LAIN!"""

    # Call OpenRouter API
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            },
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content']
        
        # Clean response (remove markdown if any)
        ai_response = ai_response.strip()
        if ai_response.startswith('```json'):
            ai_response = ai_response[7:]
        if ai_response.startswith('```'):
            ai_response = ai_response[3:]
        if ai_response.endswith('```'):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()
        
        # Parse JSON
        data = json.loads(ai_response)
        highlights = data.get('highlights', [])
        
        if not highlights:
            raise Exception("No highlights found by AI")
        
        # Validate and process highlights
        valid_highlights = []
        for h in highlights:
            try:
                start_sec = srt_to_seconds(h['start_time'])
                end_sec = srt_to_seconds(h['end_time'])
                duration = end_sec - start_sec
                
                # Validate duration
                if duration < 30 or duration > 120:
                    print(f"⚠️ Skipping highlight: duration {duration}s not in range 30-120s")
                    continue
                
                h['duration'] = duration
                valid_highlights.append(h)
                
                print(f"✅ Highlight {len(valid_highlights)}: {h['title']} ({duration}s)")
                
            except Exception as e:
                print(f"⚠️ Error processing highlight: {e}")
                continue
        
        if not valid_highlights:
            raise Exception("No valid highlights after validation")
        
        return valid_highlights
        
    except requests.exceptions.Timeout:
        raise Exception("API timeout (>2 minutes)")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response: {str(e)}")
    except Exception as e:
        raise Exception(f"Highlight finder error: {str(e)}")

def generate_highlights_fallback(subtitle_path, num_clips):
    """
    Fallback method: Generate highlights by splitting video evenly
    Used when AI API fails
    """
    print("⚠️ Using fallback method (even split)")
    
    subtitles = parse_srt_file(subtitle_path)
    
    if not subtitles:
        raise Exception("No subtitles found")
    
    # Get total duration
    total_seconds = srt_to_seconds(subtitles[-1]['end'])
    
    # Target clip duration (60-90 seconds)
    target_duration = 75
    
    highlights = []
    current_time = 30  # Start after 30 seconds intro
    
    for i in range(num_clips):
        if current_time + target_duration > total_seconds - 30:
            break
        
        start_time = seconds_to_srt(current_time)
        end_time = seconds_to_srt(current_time + target_duration)
        
        highlights.append({
            "title": f"Highlight {i+1}",
            "description": f"Segmen menarik {i+1} dari video",
            "hook_text": f"Momen menarik ke-{i+1}",
            "start_time": start_time,
            "end_time": end_time,
            "duration": target_duration,
            "reason": "Auto-generated segment"
        })
        
        current_time += target_duration + 30  # 30s gap between clips
    
    return highlights

if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python highlight_finder.py <srt_file> <api_key> [num_clips]")
        sys.exit(1)
    
    srt_file = sys.argv[1]
    api_key = sys.argv[2]
    num_clips = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    try:
        highlights = find_highlights(srt_file, num_clips, api_key)
        print(f"\n✅ Found {len(highlights)} highlights:")
        for h in highlights:
            print(f"  - {h['title']} ({h['duration']}s)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
