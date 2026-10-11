"""Photo and Live Photo sizes at equal quality, measured on a Mac with Apple's encoders.

JPEG and HEIC come from ImageIO (sips); Live Photo motion is HEVC from Apple's hardware encoder
(hevc_videotoolbox). nu-media is measured as it works today: the same Apple encoders at half width and
height, scaled back up with Lanczos (no Neural Engine enhancement yet). Every file is scored with VMAF
against the original, and nu-media is shrunk until it matches the Apple file's score.

  uv run python photo.py --src SOURCE.mov --start 4 --out out/photo
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

W, H = 2622, 1206  # iPhone 18 Pro screen
LIVE_SECONDS = 3
MODEL = "vmaf_v0.6.1"


def run(*cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def ff(*args):
    return run("ffmpeg", "-hide_banner", "-y", "-loglevel", "error", *args)


def vmaf(dist, ref, up=False):
    post = f"scale={W}:{H}:flags=lanczos," if up else ""
    chain = (f"[0:v]{post}setpts=PTS-STARTPTS,format=yuv420p[d];[1:v]setpts=PTS-STARTPTS,format=yuv420p[r];"
             f"[d][r]libvmaf=model=version={MODEL}:n_threads=10")
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(dist), "-i", str(ref), "-lavfi", chain, "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"VMAF score: ([\d.]+)", err).group(1))


def sips(src, dst, fmt, quality, size=None):
    cmd = ["sips", "-s", "format", fmt, "-s", "formatOptions", str(quality)]
    if size:
        cmd += ["-z", str(size[1]), str(size[0])]
    run(*cmd, str(src), "--out", str(dst))
    png = dst.with_suffix(dst.suffix + ".png")
    run("sips", "-s", "format", "png", str(dst), "--out", str(png))
    return dst.stat().st_size, png


def hevc(src, dst, kbps, size=None):
    vf = f"scale={size[0]}:{size[1]}:flags=lanczos," if size else ""
    ff("-i", str(src), "-an", "-vf", f"{vf}format=yuv420p", "-c:v", "hevc_videotoolbox", "-b:v", f"{kbps}k",
       "-tag:v", "hvc1", str(dst))
    return dst.stat().st_size


def match(score_at, want, lo, hi, steps=9):
    """Smallest setting in [lo, hi] whose score reaches `want` (score rises with the setting)."""
    best = None
    for _ in range(steps):
        mid = (lo + hi) / 2
        size, score = score_at(mid)
        if score >= want:
            best, hi = (mid, size, score), mid
        else:
            lo = mid
    if best is None:
        size, score = score_at(hi)
        best = (hi, size, score)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--start", type=float, default=0)
    ap.add_argument("--out", default="out/photo")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    crop = f"crop={W}:{H}:(in_w-{W})/2:(in_h-{H})/2"

    ref = out / "ref.png"
    ff("-ss", str(a.start), "-i", a.src, "-frames:v", "1", "-vf", crop, str(ref))
    clip = out / "live.mov"
    ff("-ss", str(a.start), "-t", str(LIVE_SECONDS), "-i", a.src, "-an", "-vf", f"{crop},format=yuv422p10le",
       "-c:v", "prores_ks", "-profile:v", "2", str(clip))
    half = (W // 2, H // 2)
    res = {"size": f"{W}x{H}", "vmaf_model": MODEL, "source": Path(a.src).name, "start": a.start}

    jpg, jpg_png = sips(ref, out / "photo.jpg", "jpeg", 85)
    heic, heic_png = sips(ref, out / "photo.heic", "heic", 85)
    res["jpeg"] = {"bytes": jpg, "vmaf": round(vmaf(jpg_png, ref), 2), "settings": "ImageIO quality 0.85"}
    res["heic"] = {"bytes": heic, "vmaf": round(vmaf(heic_png, ref), 2), "settings": "ImageIO quality 0.85"}

    def nu_photo(q):
        size, png = sips(ref, out / "nu.heic", "heic", round(q), half)
        return size, vmaf(png, ref, up=True)

    for k in ("jpeg", "heic"):
        q, size, score = match(nu_photo, res[k]["vmaf"], 5, 100)
        res[f"nu-vs-{k}"] = {"bytes": size, "vmaf": round(score, 2), "heic_quality_half_size": round(q)}

    # Live Photo: Apple's pair is the full-size HEIC plus 3 s of full-size HEVC; nu-media sends both at half size.
    mov = out / "apple.mov"
    apple_kbps = 8000
    apple_mov = hevc(clip, mov, apple_kbps)
    apple_v = vmaf(mov, clip)
    res["live-apple"] = {"bytes": heic + apple_mov, "video_kbps": apple_kbps, "video_vmaf": round(apple_v, 2)}

    def nu_live(kb):
        size = hevc(clip, out / "nu.mov", round(kb), half)
        return size, vmaf(out / "nu.mov", clip, up=True)

    kb, size, score = match(nu_live, apple_v, 100, apple_kbps)
    nu_still = res["nu-vs-heic"]["bytes"]
    res["live-nu"] = {"bytes": nu_still + size, "video_kbps": round(kb), "video_vmaf": round(score, 2)}

    (out / "results-photo.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
