"""nu-score: a video test that keeps working where VMAF stops.

VMAF alone isn't enough for nu-media: its models stop at 3840 x 2160, assume 8-bit SDR at ordinary frame rates,
average away a few bad frames, and can't see dropped frames, banding or stalls. nu-score reports, for any
resolution and any frame rate:

  size       bytes, mean bitrate, peak bitrate over any 1 s window, bits per pixel per frame (bpp)
  timing     frames in and out, dropped and duplicated frames, longest stall, effective fps, decode fps
  resolution native width x height of the source and of the encode; scoring always happens at the source size
  quality    per frame, at native resolution in tiles of at most 3840 x 2160 (so 8K, 11K and 42K work):
             VMAF (4K model per tile), PSNR-Y, MS-SSIM and CAMBI banding; mean, worst 1% of frames and worst tile
  verdict    "same as the original" only when every gate passes (GATES below), not on one average

HDR (PQ or HLG) and high-frame-rate perception are scored with ColorVideoVDP when it is installed
(`--cvvdp`, pip install cvvdp); its JOD scale (10 = identical) covers HDR, display size and frame rate.

  uv run python nuscore.py --ref source.mov --dist encode.mp4 [--bits encode.mp4] [--encode-fps 54] [--json out.json]
"""

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

TILE = (3840, 2160)
# First gates for "same as the original"; calibrated against a viewer test (ITU-T P.910) as results come in.
GATES = {
    "vmaf_mean": 95.0,       # VMAF 4K model, mean over frames and tiles
    "vmaf_p1": 90.0,         # worst 1% of frames
    "ms_ssim_p1": 0.985,     # worst 1% of frames
    "cambi_max": 3.0,        # worst frame; Netflix's CAMBI is 0 for no banding, about 5 and up is visible
    "dropped": 0,
    "stall_frames": 1.5,     # longest gap between shown frames, in frame durations
    "cvvdp_jod": 9.5,        # only when ColorVideoVDP runs
}


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def probe(path):
    s = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,pix_fmt,color_transfer,codec_name:format=duration,size", "-of", "json", str(path)]))
    st, fm = s["streams"][0], s["format"]
    n, d = st["r_frame_rate"].split("/")
    return {"w": st["width"], "h": st["height"], "fps": float(n) / float(d), "pix_fmt": st.get("pix_fmt"),
            "transfer": st.get("color_transfer"), "codec": st.get("codec_name"), "duration": float(fm["duration"]), "bytes": int(fm["size"])}


def packets(path):
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time,size", "-of", "csv=p=0", str(path)])
    pk = []
    for line in out.splitlines():
        t, s = (line.split(",") + [""])[:2]
        if t and s and t != "N/A":
            pk.append((float(t), int(s)))
    return sorted(pk)


def timing(path, src_frames, fps):
    pk = packets(path)
    times = [t for t, _ in pk]
    dur = 1 / fps
    gaps = [b - a for a, b in zip(times, times[1:])]
    dup = sum(1 for g in gaps if g < dur * 0.5)
    stall = max(gaps) / dur if gaps else 0
    # Peak bitrate over any 1 s window of presentation time.
    peak, j, acc = 0, 0, 0
    for i, (t, s) in enumerate(pk):
        acc += s
        while pk[j][0] <= t - 1.0:
            acc -= pk[j][1]
            j += 1
        peak = max(peak, acc)
    return {"frames": len(pk), "dropped": max(0, src_frames - len(pk)), "duplicated": dup,
            "stall_frames": round(stall, 2), "peak_kbps_1s": round(peak * 8 / 1000, 1)}


def decode_fps(path, frames):
    t0 = time.monotonic()
    run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"])
    return round(frames / (time.monotonic() - t0), 1)


def tiles(w, h):
    nx, ny = math.ceil(w / TILE[0]), math.ceil(h / TILE[1])
    tw, th = math.ceil(w / nx / 2) * 2, math.ceil(h / ny / 2) * 2
    return [(min(tw, w - x), min(th, h - y), x, y) for y in range(0, h, th) for x in range(0, w, tw)]


def score_tile(dist, ref, size, tile, model, threads):
    w, h = size
    tw, th, x, y = tile
    up = f"scale={w}:{h}:flags=lanczos," if probe(dist)["w"] != w or probe(dist)["h"] != h else ""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        log = f.name
    chain = (f"[0:v]setpts=PTS-STARTPTS,{up}crop={tw}:{th}:{x}:{y},format=yuv420p10le[d];"
             f"[1:v]setpts=PTS-STARTPTS,crop={tw}:{th}:{x}:{y},format=yuv420p10le[r];"
             f"[d][r]libvmaf=model=version={model}:feature=name=psnr|name=float_ms_ssim|name=cambi:n_threads={threads}:log_fmt=json:log_path={log}")
    subprocess.run(["ffmpeg", "-hide_banner", "-i", str(dist), "-i", str(ref), "-lavfi", chain, "-f", "null", "-"], check=True, capture_output=True)
    frames = json.loads(Path(log).read_text())["frames"]
    Path(log).unlink()
    return [{"vmaf": m["vmaf"], "psnr_y": m["psnr_y"], "ms_ssim": m["float_ms_ssim"], "cambi": m["cambi"]} for m in (fr["metrics"] for fr in frames)]


def pct(xs, p):
    s = sorted(xs)
    return s[max(0, min(len(s) - 1, int(math.floor(p / 100 * (len(s) - 1)))))]


def cvvdp(dist, ref, display):
    if not shutil.which("cvvdp"):
        return None
    out = subprocess.run(["cvvdp", "--test", str(dist), "--ref", str(ref), "--display", display, "--quiet"], capture_output=True, text=True).stdout
    m = re.search(r"([\d.]+)\s*\[JOD\]", out) or re.search(r"([\d.]+)\s*$", out.strip())
    return float(m.group(1)) if m else None


def nuscore(ref, dist, bits=None, encode_fps=None, threads=10, use_cvvdp=False, display="standard_4k"):
    ref, dist = Path(ref), Path(dist)
    bits = Path(bits) if bits else dist
    r, d, b = probe(ref), probe(dist), probe(bits)
    src_frames = len(packets(ref))
    model = "vmaf_4k_v0.6.1" if max(r["w"], r["h"]) > 1920 else "vmaf_v0.6.1"
    per_tile = [score_tile(dist, ref, (r["w"], r["h"]), t, model, threads) for t in tiles(r["w"], r["h"])]
    frames = [{k: sum(t[i][k] for t in per_tile) / len(per_tile) for k in per_tile[0][0]} for i in range(min(len(t) for t in per_tile))]
    cambi_frames = [max(t[i]["cambi"] for t in per_tile) for i in range(len(frames))]
    tile_means = [sum(f["vmaf"] for f in t) / len(t) for t in per_tile]
    tm = timing(bits, src_frames, r["fps"])
    kbps = b["bytes"] * 8 / 1000 / r["duration"]
    res = {
        "source": {"file": ref.name, "resolution": f"{r['w']}x{r['h']}", "fps": round(r["fps"], 3), "frames": src_frames,
                   "pix_fmt": r["pix_fmt"], "transfer": r["transfer"]},
        "encode": {"file": bits.name, "codec": b["codec"], "resolution": f"{b['w']}x{b['h']}", "shown_at": f"{r['w']}x{r['h']}"},
        "size": {"bytes": b["bytes"], "mean_kbps": round(kbps, 1), "peak_kbps_1s": tm.pop("peak_kbps_1s"),
                 "bpp": round(kbps * 1000 / (r["w"] * r["h"] * r["fps"]), 5)},
        "timing": {**tm, "effective_fps": round(tm["frames"] / r["duration"], 2), "encode_fps": encode_fps,
                   "decode_fps": decode_fps(dist, len(frames))},
        "quality": {
            "tiles": len(per_tile), "model": model,
            "vmaf_mean": round(sum(f["vmaf"] for f in frames) / len(frames), 2), "vmaf_p1": round(pct([f["vmaf"] for f in frames], 1), 2),
            "vmaf_worst_tile": round(min(tile_means), 2),
            "psnr_y_mean": round(sum(f["psnr_y"] for f in frames) / len(frames), 2),
            "ms_ssim_mean": round(sum(f["ms_ssim"] for f in frames) / len(frames), 4), "ms_ssim_p1": round(pct([f["ms_ssim"] for f in frames], 1), 4),
            "cambi_mean": round(sum(cambi_frames) / len(cambi_frames), 2), "cambi_max": round(max(cambi_frames), 2),
            "cvvdp_jod": cvvdp(dist, ref, display) if use_cvvdp else None,
        },
    }
    q, t = res["quality"], res["timing"]
    checks = {"vmaf_mean": q["vmaf_mean"] >= GATES["vmaf_mean"], "vmaf_p1": q["vmaf_p1"] >= GATES["vmaf_p1"],
              "ms_ssim_p1": q["ms_ssim_p1"] >= GATES["ms_ssim_p1"], "cambi_max": q["cambi_max"] <= GATES["cambi_max"],
              "dropped": t["dropped"] <= GATES["dropped"], "stall_frames": t["stall_frames"] <= GATES["stall_frames"]}
    if q["cvvdp_jod"] is not None:
        checks["cvvdp_jod"] = q["cvvdp_jod"] >= GATES["cvvdp_jod"]
    res["verdict"] = {"same_as_original": all(checks.values()), "failed": [k for k, ok in checks.items() if not ok], "gates": GATES}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True)
    ap.add_argument("--dist", required=True, help="what the viewer sees (for nu-media, the enhanced output)")
    ap.add_argument("--bits", help="what crossed the network, if different from --dist (for nu-media, the base layer)")
    ap.add_argument("--encode-fps", type=float)
    ap.add_argument("--threads", type=int, default=10)
    ap.add_argument("--cvvdp", action="store_true")
    ap.add_argument("--display", default="standard_4k")
    ap.add_argument("--json")
    a = ap.parse_args()
    res = nuscore(a.ref, a.dist, a.bits, a.encode_fps, a.threads, a.cvvdp, a.display)
    print(json.dumps(res, indent=2))
    if a.json:
        Path(a.json).write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
