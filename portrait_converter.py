"""
Portrait Converter Module
Converts landscape video (16:9) to portrait (9:16) with face tracking
"""

import cv2
import subprocess
import numpy as np
from pathlib import Path
import os

def convert_to_portrait(video_path, output_dir):
    """
    Convert landscape video to portrait with smart face tracking
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save output
    
    Returns:
        str: Path to portrait video
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "portrait.mp4"
    
    print(f"📱 Converting to portrait: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise Exception("Failed to open video file")
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"  Input: {width}x{height} @ {fps}fps ({total_frames} frames)")
    
    # Output dimensions (portrait 9:16)
    out_width = 1080
    out_height = 1920
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # Processing parameters
    crop_width = int(height * 9 / 16)  # Width of crop window
    
    # Track center position
    current_center = width // 2
    target_center = width // 2
    smoothing_factor = 0.1  # Lower = smoother
    
    # Temporary output (without audio)
    temp_output = output_dir / "temp_portrait.mp4"
    
    # Video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(
        str(temp_output),
        fourcc,
        fps,
        (out_width, out_height)
    )
    
    frame_count = 0
    last_face_center = None
    frames_since_face = 0
    
    print(f"  Processing frames...")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Face detection (every 5 frames for performance)
            if frame_count % 5 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                if len(faces) > 0:
                    # Get largest face
                    largest_face = max(faces, key=lambda f: f[2] * f[3])
                    x, y, w, h = largest_face
                    
                    face_center_x = x + w // 2
                    last_face_center = face_center_x
                    frames_since_face = 0
                    
                    # Update target
                    target_center = face_center_x
                else:
                    frames_since_face += 5
                    
                    # If no face for 3 seconds, center the crop
                    if frames_since_face > fps * 3:
                        target_center = width // 2
            
            # Smooth transition
            current_center += (target_center - current_center) * smoothing_factor
            current_center = int(current_center)
            
            # Calculate crop boundaries
            left = max(0, current_center - crop_width // 2)
            right = min(width, left + crop_width)
            
            # Adjust if at edge
            if right == width:
                left = width - crop_width
            
            # Crop frame
            cropped = frame[:, left:right]
            
            # Resize to output dimensions
            resized = cv2.resize(cropped, (out_width, out_height))
            
            # Write frame
            out.write(resized)
            
            # Progress
            if frame_count % 100 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"    Progress: {progress:.1f}% ({frame_count}/{total_frames})")
        
        cap.release()
        out.release()
        
        print(f"  ✅ Video processing complete")
        
        # Add audio from original video
        print(f"  🔊 Adding audio...")
        
        cmd = [
            "ffmpeg",
            "-i", str(temp_output),
            "-i", video_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0?",  # Optional audio
            "-shortest",
            "-y",
            str(output_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        
        # Cleanup temp file
        if temp_output.exists():
            temp_output.unlink()
        
        if not output_path.exists():
            raise Exception("Failed to create final output")
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"✅ Portrait video created: {output_path} ({file_size:.2f} MB)")
        
        return str(output_path)
        
    except Exception as e:
        cap.release()
        out.release()
        
        if temp_output.exists():
            temp_output.unlink()
        
        raise Exception(f"Portrait conversion failed: {str(e)}")

def simple_center_crop(video_path, output_path):
    """
    Simple center crop without face tracking (faster)
    """
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", "crop=ih*9/16:ih,scale=1080:1920",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "copy",
        "-y",
        str(output_path)
    ]
    
    subprocess.run(cmd, capture_output=True, timeout=180)
    
    return str(output_path)

if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python portrait_converter.py <video_path>")
        sys.exit(1)
    
    video = sys.argv[1]
    
    try:
        output = convert_to_portrait(video, "test_output")
        print(f"✅ Success: {output}")
    except Exception as e:
        print(f"❌ Error: {e}")
