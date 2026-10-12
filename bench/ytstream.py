"""Saves exactly the video stream YouTube sends, for dev testing nu-media against real delivery streams.

Picks the best video-only format (highest resolution, then HDR, then frame rate, then bitrate) unless --format is
given, and copies the bytes without re-encoding. A section is cut on keyframes, also without re-encoding.
Writes <name>.<ext> and <name>.json with the format ID, codec, size, frame rate, dynamic range, bitrate, licence,
channel and SHA-256, so every test records what it ran on.

YouTube's terms allow viewing on YouTube; downloaded streams are for private dev testing only. Anything shown on
a public page needs the owner's permission or a licence that allows it (the JSON records the licence field).

  uv run python ytstream.py --list URL
  uv run python ytstream.py URL --section 60-80 --out testmedia/
  uv run python ytstream.py URL --full --out testmedia/
"""

import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

YTDLP = ["uvx", "yt-dlp", "--no-warnings"]


def info(url):
    return json.loads(subprocess.run([*YTDLP, "-J", url], check=True, capture_output=True, text=True).stdout)


def best(formats):
    v = [f for f in formats if f.get("vcodec") not in (None, "none") and f.get("acodec") in (None, "none") and f.get("protocol", "").startswith("http")]
    hdr = lambda f: 0 if (f.get("dynamic_range") or "SDR") == "SDR" else 1
    return max(v, key=lambda f: ((f.get("height") or 0) * (f.get("width") or 0), hdr(f), f.get("fps") or 0, f.get("tbr") or 0))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--format", help="YouTube format ID (itag); default is the best video-only stream")
    ap.add_argument("--section", default="0-10", help="START-END in seconds, cut on keyframes without re-encoding")
    ap.add_argument("--full", action="store_true", help="the whole video instead of a section")
    ap.add_argument("--out", default="testmedia")
    a = ap.parse_args()
    if a.list:
        subprocess.run([*YTDLP, "-F", a.url], check=True)
        return
    meta = info(a.url)
    fmt = next(f for f in meta["formats"] if f["format_id"] == a.format) if a.format else best(meta["formats"])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tag = "full" if a.full else a.section.replace("-", "to")
    name = f"{meta['id']}-{fmt['format_id']}-{fmt.get('height')}p-{tag}"
    cmd = [*YTDLP, "-f", fmt["format_id"], "-o", str(out / f"{name}.%(ext)s")]
    if not a.full:
        cmd += ["--download-sections", f"*{a.section}"]
    subprocess.run([*cmd, a.url], check=True)
    path = next(out.glob(f"{name}.*"))
    probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries",
                                       "stream=codec_name,profile,width,height,r_frame_rate,pix_fmt,color_transfer,color_primaries,nb_read_packets:format=duration,size",
                                       "-of", "json", str(path)], check=True, capture_output=True, text=True).stdout)
    st, fm = probe["streams"][0], probe["format"]
    rec = {
        "url": a.url, "id": meta["id"], "title": meta.get("title"), "channel": meta.get("channel"), "license": meta.get("license"),
        "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "section": None if a.full else a.section,
        "youtube_format": {k: fmt.get(k) for k in ("format_id", "vcodec", "width", "height", "fps", "dynamic_range", "tbr", "ext")},
        "file": {"name": path.name, "bytes": int(fm["size"]), "sha256": sha256(path), "duration": float(fm["duration"]),
                 "kbps": round(int(fm["size"]) * 8 / 1000 / float(fm["duration"]), 1), "codec": st.get("codec_name"), "profile": st.get("profile"),
                 "resolution": f"{st['width']}x{st['height']}", "fps": st.get("r_frame_rate"), "frames": int(st.get("nb_read_packets", 0)),
                 "pix_fmt": st.get("pix_fmt"), "transfer": st.get("color_transfer"), "primaries": st.get("color_primaries")},
        "note": "Private dev testing only; public use needs the owner's permission or a licence that allows it.",
    }
    (out / f"{name}.json").write_text(json.dumps(rec, indent=2))
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
