#!/usr/bin/env python
"""Image and video detection / frame extraction.

Architecture is ready for future PDF / audio preview plugins:
register additional checkers via the same pattern (is_* + extract).
"""
from __future__ import annotations

import os
from typing import Optional

from PIL import Image

_IMAGE_EXTENSIONS = frozenset(
    {
        ".bmp",
        ".dib",
        ".gif",
        ".ico",
        ".im",
        ".jpg",
        ".jpeg",
        ".jpe",
        ".pcx",
        ".png",
        ".ppm",
        ".pbm",
        ".pgm",
        ".tif",
        ".tiff",
        ".webp",
    }
)

_VIDEO_EXTENSIONS = frozenset(
    {
        ".avi",
        ".mp4",
        ".mov",
        ".mkv",
        ".webm",
        ".flv",
        ".wmv",
        ".mpg",
        ".mpeg",
        ".3gp",
        ".m4v",
    }
)


def is_image(path: str) -> bool:
    if not path or not os.path.isfile(path):
        return False
    if os.path.splitext(path)[1].lower() not in _IMAGE_EXTENSIONS:
        return False
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def is_video(path: str) -> bool:
    if not path or not os.path.isfile(path):
        return False
    if os.path.splitext(path)[1].lower() not in _VIDEO_EXTENSIONS:
        return False
    try:
        import cv2

        cap = cv2.VideoCapture(path)
        valid = cap.isOpened()
        cap.release()
        return valid
    except Exception:
        return False


def get_video_frame(path: str, frame_number: int = 0) -> Optional[Image.Image]:
    """Return a PIL Image of a single video frame, or None."""
    if not path or not os.path.isfile(path):
        return None

    try:
        import cv2
    except ImportError:
        return None

    try:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return None

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total_frames > 0:
            if frame_number < 0:
                frame_number = max(total_frames // 2, 0)
            elif frame_number >= total_frames:
                frame_number = max(total_frames - 1, 0)
        else:
            frame_number = 0

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        if not ret or frame is None:
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)
    except Exception:
        return None


def thumbnail_image(path: str, size: tuple[int, int] = (32, 32)) -> Optional[Image.Image]:
    """Open an image and return a thumbnail, or None on failure."""
    if not path or not os.path.isfile(path):
        return None
    try:
        with Image.open(path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            return img.copy()
    except Exception:
        return None
