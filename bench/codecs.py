"""Rate-quality benchmark: Apple hardware H.264 and HEVC, SVT-AV1, and the nu-media base layer.

Encodes one 1080p clip at several bitrates, scores each with VMAF against the source, and writes
results.json plus a 3 x 2 comparison video at one bitrate (the source and 1:1 pixel crops of each
decoded result).

The nu-media rows are the base layer only: hardware HEVC or real-time SVT-AV1 at 960 x 540, upscaled
with Lanczos for scoring. The Neural Engine enhancement doesn't exist yet, so these are floors, not
nu-media's result. Encode fps is wall clock on the machine that ran it.

  uv run python codecs.py SOURCE.mov --start 60 --seconds 8 --out out/
"""

import argparse
import json
import re
import subprocess
import time
from pathlib import Path

RATES = [250, 500, 1000, 2000, 4000]  # kbit/s
SHOW_RATE = 500
CROP = "640:360:300:140"  # w:h:x:y on the 1920 x 1080 frame

CODECS = {
    "h264-hw": {
        "label": "H.264, Apple hardware",
        "enc": lambda r: ["-c:v", "h264_videotoolbox", "-allow_sw", "0", "-b:v", f"{r}k", "-maxrate", f"{r}k", "-bufsize", f"{2 * r}k"],
        "ext": "mp4",
    },
    "hevc-hw": {
        "label": "HEVC, Apple hardware",
        "enc": lambda r: ["-c:v", "hevc_videotoolbox", "-allow_sw", "0", "-tag:v", "hvc1", "-b:v", f"{r}k", "-maxrate", f"{r}k", "-bufsize", f"{2 * r}k"],
        "ext": "mp4",
    },
    "av1-svt": {
        "label": "AV1, SVT-AV1 software (preset 8)",
        "enc": lambda r: ["-c:v", "libsvtav1", "-preset", "8", "-b:v", f"{r}k", "-svtav1-params", "rc=1"],
        "ext": "mp4",
    },
    "av1-svt-rt": {
        "label": "AV1, SVT-AV1 software, real-time call settings (CBR, low delay)",
        "enc": lambda r: ["-c:v", "libsvtav1", "-preset", "10", "-b:v", f"{r}k", "-svtav1-params", "rc=2:pred-struct=1"],
        "ext": "mp4",
    },
    "nu-base": {
        "label": "nu-media base layer (HEVC hardware at 960 x 540, Lanczos upscale)",
        "pre": ["-vf", "scale=960:540:flags=lanczos"],
        "enc": lambda r: ["-c:v", "hevc_videotoolbox", "-allow_sw", "0", "-tag:v", "hvc1", "-b:v", f"{r}k", "-maxrate", f"{r}k", "-bufsize", f"{2 * r}k"],
        "post": "scale=1920:1080:flags=lanczos",
        "ext": "mp4",
    },
    "nu-base-av1": {
        "label": "nu-media base layer, AV1 option (SVT-AV1 real-time at 960 x 540, Lanczos upscale)",
        "pre": ["-vf", "scale=960:540:flags=lanczos"],
        "enc": lambda r: ["-c:v", "libsvtav1", "-preset", "10", "-b:v", f"{r}k", "-svtav1-params", "rc=2:pred-struct=1"],
        "post": "scale=1920:1080:flags=lanczos",
        "ext": "mp4",
    },
}
GRID = ["h264-hw", "hevc-hw", "av1-svt-rt", "nu-base", "nu-base-av1"]


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def ff(*args):
    return run(["ffmpeg", "-hide_banner", "-y", "-loglevel", "error", *args])


def vmaf(dist, ref, post=None):
    chain = f"[0:v]{post + ',' if post else ''}setpts=PTS-STARTPTS,format=yuv420p[d];[1:v]setpts=PTS-STARTPTS,format=yuv420p[r];[d][r]libvmaf=n_threads=8"
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(dist), "-i", str(ref), "-lavfi", chain, "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    return float(re.search(r"VMAF score: ([\d.]+)", out).group(1))


def kbps(path, seconds):
    return path.stat().st_size * 8 / 1000 / seconds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--start", type=float, default=60)
    ap.add_argument("--seconds", type=float, default=8)
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    ref = out / "ref.y4m"
    ff("-ss", str(a.start), "-t", str(a.seconds), "-i", a.source, "-an", "-vf", "scale=1920:1080:flags=lanczos,format=yuv420p", str(ref))

    results = {"source": Path(a.source).name, "start": a.start, "seconds": a.seconds, "rates_kbps": RATES, "codecs": {}}
    for key, c in CODECS.items():
        rows = []
        for r in RATES:
            f = out / f"{key}-{r}.{c['ext']}"
            t0 = time.monotonic()
            ff("-i", str(ref), *c.get("pre", []), *c["enc"](r), "-an", str(f))
            fps = a.seconds * 24 / (time.monotonic() - t0)
            rows.append({"target_kbps": r, "actual_kbps": round(kbps(f, a.seconds), 1), "vmaf": round(vmaf(f, ref, c.get("post")), 2), "encode_fps": round(fps)})
            print(key, rows[-1], flush=True)
        results["codecs"][key] = {"label": c["label"], "points": rows}
    (out / "results.json").write_text(json.dumps(results, indent=2))

    tiles = [out / "tile-original.y4m"]
    ff("-i", str(ref), "-vf", f"crop={CROP},format=yuv420p", str(tiles[0]))
    results["grid"] = {"want_kbps": SHOW_RATE, "codecs": {}}
    for key in GRID:
        c = CODECS[key]
        f = out / f"grid-{key}.mp4"
        target = SHOW_RATE
        for _ in range(4):  # encoders miss their target in both directions; steer to equal actual bits
            ff("-i", str(ref), *c.get("pre", []), *c["enc"](round(target)), "-an", str(f))
            got = kbps(f, a.seconds)
            if abs(got - SHOW_RATE) / SHOW_RATE < 0.03:
                break
            target *= SHOW_RATE / got
        results["grid"]["codecs"][key] = {"actual_kbps": round(got, 1), "vmaf": round(vmaf(f, ref, c.get("post")), 2)}
        print("grid", key, results["grid"]["codecs"][key], flush=True)
        post = c.get("post")
        t = out / f"tile-{key}.y4m"
        ff("-i", str(f), "-vf", f"{post + ',' if post else ''}crop={CROP},format=yuv420p", str(t))
        tiles.append(t)
    (out / "results.json").write_text(json.dumps(results, indent=2))
    grid = out / f"compare-{SHOW_RATE}k.mp4"
    ff(*sum((["-i", str(t)] for t in tiles), []),
       "-filter_complex", "[0:v][1:v][2:v]hstack=3[top];[3:v][4:v][5:v]hstack=3[bot];[top][bot]vstack",
       "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(grid))
    ff("-i", str(ref), "-vf", f"crop={CROP}", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out / "original-crop.mp4"))
    ff("-ss", "2", "-i", str(grid), "-frames:v", "1", "-q:v", "3", str(out / f"compare-{SHOW_RATE}k.jpg"))


if __name__ == "__main__":
    main()
