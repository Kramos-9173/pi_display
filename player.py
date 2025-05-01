#!/usr/bin/env python3
import json, os, socket, subprocess, time, pathlib, sys
MEDIA_DIR = pathlib.Path(__file__).parent / "media"
PLAYLIST  = pathlib.Path(__file__).parent / "playlist.json"
SOCK      = "/tmp/mpv-sock"

MPV_BASE = [
    "mpv", "--idle=yes", "--fs", "--geometry=1024x600",
    "--no-osc", "--really-quiet",
    "--vo=gpu", "--gpu-context=drm",          # works headless
    f"--input-ipc-server={SOCK}",             # open JSON IPC
    "--vf=scale=1024:600:force_original_aspect_ratio=increase,crop=1024:600",
]

def load_playlist():
    with open(PLAYLIST) as f:
        return json.load(f)

def send(cmd):
    with socket.socket(socket.AF_UNIX) as s:
        s.connect(SOCK)
        s.sendall((json.dumps({"command":cmd})+"\n").encode())

def build_and_send():
    send(["playlist-clear"])
    for item in load_playlist():
        path = str(MEDIA_DIR / item["file"])
        send(["loadfile", path, "append-play"])
        # set per-item properties
        send(["set", "vf", f"lavfi=[fade={item['transition']}]"])
        send(["show-text", f"Duration {item['secs']}s"])
        if pathlib.Path(path).suffix.lower() in {".jpg",".jpeg",".png",".bmp",".gif"}:
            send(["set", "image-display-duration", item["secs"]])

def main():
    subprocess.Popen(MPV_BASE)          # start mpv in the back-ground
    time.sleep(1)                       # give MPV a sec to create the socket
    build_and_send()                    # first load
    last = PLAYLIST.stat().st_mtime
    while True:
        time.sleep(1)
        new = PLAYLIST.stat().st_mtime
        if new != last:                 # playlist file changed
            last = new
            build_and_send()

if __name__ == "__main__":
    main()





