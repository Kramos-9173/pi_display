#!/usr/bin/env python3
"""
slideshow.py  –  edge-to-edge slideshow for a 1024×600 panel
 • Plays every image / video in ~/pi_display/media/
 • Fade transition, loop forever
 • Runs perfectly from an SSH shell (no X11 required)
"""

import sys, random, subprocess
from pathlib import Path

# ---------- USER SETTINGS ----------
MEDIA_DIR = Path(__file__).parent / "media"
SECONDS_PER_IMAGE = 5
SHUFFLE = False
TRANSITION = "fade"          # fade, wipeleft, etc.
# -----------------------------------

EXT_IMG = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
EXT_VID = {".mp4", ".mov", ".mkv", ".avi"}

MPV_FLAGS = [
    "--fs",
    "--geometry=1024x600",
    "--no-osc",
    "--really-quiet",
    "--vo=gpu",
    "--gpu-context=drm",     # <= draw directly to HDMI framebuffer
    f"--image-display-duration={SECONDS_PER_IMAGE}",
    "--loop-playlist=inf",
    "--no-terminal",
    # scale up, keep aspect, crop center = “cover” fit
    "--vf=scale=1024:600:force_original_aspect_ratio=increase,crop=1024:600",
    f"--transition-style={TRANSITION}",
]

def build_playlist() -> list[str]:
    files = [p for p in MEDIA_DIR.iterdir()
             if p.suffix.lower() in EXT_IMG.union(EXT_VID)]
    if not files:
        sys.exit(f"No media found in {MEDIA_DIR}")
    files.sort()
    if SHUFFLE:
        random.shuffle(files)
    return [str(p) for p in files]

def main() -> None:
    playlist = build_playlist()
    cmd = ["mpv", *MPV_FLAGS, *playlist]
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        sys.exit("mpv missing – sudo apt install mpv")

if __name__ == "__main__":
    main()



