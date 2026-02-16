"""
YT Short Clipper - Core Modules
"""

__version__ = "1.0.0"
__author__ = "YT Short Clipper Team"

from .downloader import download_video
from .highlight_finder import find_highlights
from .video_clipper import clip_video
from .portrait_converter import convert_to_portrait
from .caption_generator import add_captions
from .hook_generator import add_hook

__all__ = [
    'download_video',
    'find_highlights',
    'clip_video',
    'convert_to_portrait',
    'add_captions',
    'add_hook'
]
