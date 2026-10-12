"""How low can video go? A bitrate ladder measured on a real iPhone over USB.

H.264 and HEVC are the iPhone's hardware encoders at the source size, live-call settings (bench/ios, NuBench).
nu-media sends a smaller base layer, also hardware HEVC, and the receiving iPhone enlarges it with Apple's
low-latency super resolution on the Neural Engine, 2x per pass. On iPhone Air (iOS 26.6.1) the scaler refuses
1920 x 1080 input, so for 4K its largest output is 1920 x 1080 and the last step is a Lanczos upscale.
Each pass is written out near-losslessly so the Mac can score exactly what the scaler produced.
AV1 is SVT-AV1 real time on the Mac (the iPhone has no AV1 encoder).

Every encode is scored with VMAF against the source and its frames are counted: at very low bitrates the
hardware encoder drops frames, and a dropped frame is scored as the previous frame held.
"Same as the original" means VMAF 93 or more with no dropped frames.

  uv run python ladder.py --clip nasa4k --device ID --app NuBench.app --source nasa4k.mp4 --out out/
  uv run python ladder.py --clip reel --device ID --app NuBench.app --source deemsterhotline.mp4 --out out/
  add --resume to rescore the phone's last run without encoding again
"""

import argparse
import json
import math
from pathlib import Path

from iphone import Phone, av1, dims, ff, run, vmaf

CLIPS = {
    "nasa4k": {
        "source": "NASA, Stunning Aurora Borealis from Space in Ultra-High Definition (4K), youtube.com/watch?v=PBJAR3-UvSQ, "
                  "VP9 2160p stream, 2:45 to 2:51 (about 16 Mbit/s)",
        "start": 0, "seconds": 6, "model": "vmaf_4k_v0.6.1",
        "rates": [32, 64, 128, 250, 500, 1000, 2000, 4000],
        "bases": {"1080p": (1920, 1080, 1), "540p": (960, 540, 2), "270p": (480, 270, 3)},
        "reference": ("hevc-hw", 4000), "show": [4000, 500, 64], "tile": (2560, 1440),
    },
    "reel": {
        "source": "@deemsterhotline on Instagram: H.264 High profile, 720 x 1280, 30 fps, 2.44 Mbit/s video, whole clip",
        "start": 0, "seconds": None, "model": "vmaf_v0.6.1", "fps": "30",
        "rates": [64, 128, 250, 500, 1000, 2000],
        "bases": {"720p": (720, 1280, 0), "360p": (360, 640, 1), "180p": (180, 320, 2)},
        "reference": ("hevc-hw", 2000), "show": [2000, 500, 64], "tile": (720, 1280),
    },
    "iss720": {
        "source": "NASA ISS Expedition 29 aurora time-lapse, 17 September 2011 (iss029_aurora_20110917_h265_720p.mp4): "
                  "HEVC Main, 1280 x 720, 30 fps, 1.64 Mbit/s, whole clip",
        "start": 0, "seconds": None, "model": "vmaf_v0.6.1", "fps": "30",
        "rates": [64, 128, 250, 500, 1000, 2000],
        "bases": {"720p": (1280, 720, 0), "360p": (640, 360, 1), "180p": (320, 180, 2)},
        "reference": ("hevc-hw", 2000), "show": [2000, 500, 64], "tile": (1280, 720),
    },
    "square": {
        "source": "Samsung QLED 8K 1:1 by MANU (vimeo.com/434700542), Wikimedia Commons, CC BY 3.0: VP9, 1080 x 1080, 25 fps, "
                  "4.87 Mbit/s, whole clip",
        "start": 0, "seconds": None, "model": "vmaf_v0.6.1", "fps": "25",
        "rates": [64, 128, 250, 500, 1000, 2000, 4000],
        "bases": {"1080p": (1080, 1080, 0), "540p": (540, 540, 1), "270p": (270, 270, 2)},
        "reference": ("hevc-hw", 4000), "show": [4000, 500, 64], "tile": (1080, 1080),
    },
}
TRANSPARENT = 93
ORDER = ["nu-media", "h264-hw", "hevc-hw", "av1-svt-rt"]
FPS = "30000/1001"


class USBPhone(Phone):
    def batch(self, jobs, out):
        f = out / "jobs.json"
        f.write_text(json.dumps(jobs))
        self.put(f, "jobs.json")
        r = run(["xcrun", "devicectl", "device", "process", "launch", "--device", self.device, "--terminate-existing", "--console",
                 "nu.khensu.bench"], timeout=7200)
        print(r.stdout[-3000:], flush=True)
        self.get("results-ios.json", out / "results-ios.json")


def frames(path):
    return int(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets",
                    "-of", "csv=p=0", str(path)]).stdout.strip())


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).stdout.strip())


def pass_kbps(w, h):
    """Bitrate for a near-lossless scoring copy of one super-resolution pass."""
    return min(150000, round(w * h * 30 * 0.5 / 1000))


def at_quality(points, q):
    """Lowest actual kbit/s reaching VMAF q with no dropped frames, interpolated on log bitrate."""
    pts = sorted((p["actual_kbps"], p["vmaf"]) for p in points if p["vmaf"] is not None and p["dropped"] == 0)
    if pts and pts[0][1] >= q:
        return {"kbps": pts[0][0], "bound": "at most"}
    for (r0, v0), (r1, v1) in zip(pts, pts[1:]):
        if v0 < q <= v1:
            f = (q - v0) / (v1 - v0)
            return {"kbps": round(math.exp(math.log(r0) + f * (math.log(r1) - math.log(r0))), 1), "bound": "interpolated"}
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True, choices=list(CLIPS))
    ap.add_argument("--device", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    c = CLIPS[a.clip]
    name = a.clip
    out = Path(a.out) / ("ladder" if name == "nasa4k" else f"ladder-{name}")
    out.mkdir(parents=True, exist_ok=True)
    full = out / "full.mov"
    phone = USBPhone(a.device, a.app)
    pre = "ladder" if name == "nasa4k" else f"l-{name}"

    chains = {}
    jobs = []
    for k, codec in (("h264-hw", "h264"), ("hevc-hw", "hevc")):
        for r in c["rates"]:
            jobs.append({"input": f"{pre}-full.mov", "output": f"{pre}-{k}-{r}.mp4", "codec": codec, "kbps": r})
    for b, (w, h, passes) in c["bases"].items():
        for r in c["rates"]:
            tag = f"{pre}-nu-{b}-{r}"
            stages = [f"{tag}.mp4"]
            src = f"{pre}-full.mov" if passes == 0 else f"{pre}-{b}.mov"
            jobs.append({"input": src, "output": stages[0], "codec": "hevc", "kbps": r})
            ww, hh = w, h
            for p in range(passes):
                ww, hh = ww * 2, hh * 2
                stages.append(f"{tag}-sr{p + 1}.mov")
                jobs.append({"input": stages[-2], "output": stages[-1], "codec": "sr", "kbps": pass_kbps(ww, hh)})
            chains[(b, r)] = stages

    if not a.resume:
        t = ["-t", str(c["seconds"])] if c["seconds"] else []
        ff("-ss", str(c["start"]), *t, "-i", a.source, "-an", "-vf", "format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(full))
        phone.put(full, f"{pre}-full.mov")
        for b, (w, h, passes) in c["bases"].items():
            if passes:
                f = out / f"{b}.mov"
                ff("-i", str(full), "-vf", f"scale={w}:{h}:flags=lanczos,format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(f))
                phone.put(f, f"{pre}-{b}.mov")
        phone.batch(jobs, out)
    report = json.loads((out / "results-ios.json").read_text())
    ios = {x["output"]: x for x in report["results"]}
    size = dims(full)
    src_frames = frames(full)
    secs = duration(full)
    model = c["model"]

    def fetch(n):
        f = out / n
        if not f.exists() and ios.get(n, {}).get("frames", 0) > 0:
            phone.get(n, f)
        return f

    res = {"clip": name, "source": c["source"], "seconds": round(secs, 2), "size": f"{size[0]}x{size[1]}", "source_frames": src_frames,
           "vmaf_model": model, "transparent_vmaf": TRANSPARENT, "device": report["device"], "os": report["os"], "codecs": {}}

    def point(r, bits_file, scored_file, extra=None):
        n = frames(bits_file)
        p = {"target_kbps": r, "actual_kbps": round(bits_file.stat().st_size * 8 / 1000 / secs, 1), "frames": n,
             "dropped": max(0, src_frames - n), "vmaf": round(vmaf(scored_file, full, model, size), 2), **(extra or {})}
        print(bits_file.name, p, flush=True)
        return p

    for k, label in (("h264-hw", "H.264, iPhone hardware"), ("hevc-hw", "HEVC, iPhone hardware")):
        pts = []
        for r in c["rates"]:
            f = fetch(f"{pre}-{k}-{r}.mp4")
            pts.append(point(r, f, f, {"encode_fps_iphone": round(ios[f.name]["fps"], 1)}))
        res["codecs"][k] = {"label": label, "points": pts}

    pts = []
    for r in c["rates"]:
        f = out / f"{pre}-av1-svt-rt-{r}.mp4"
        if not f.exists():
            av1(full, f, r)
        pts.append(point(r, f, f))
    res["codecs"]["av1-svt-rt"] = {"label": "AV1, SVT-AV1 real time on the Mac (no iPhone AV1 encoder)", "points": pts}

    for b, (w, h, passes) in c["bases"].items():
        if passes == 0:
            continue
        sr_pts, lz_pts = [], []
        for r in c["rates"]:
            stages = chains[(b, r)]
            base = fetch(stages[0])
            done = [s for s in stages[1:] if ios.get(s, {}).get("frames", 0) > 0]
            lz_pts.append(point(r, base, base, {"file": base.name}))
            if done:
                last = fetch(done[-1])
                ow, oh = dims(last)
                sr_pts.append(point(r, base, last, {"neural_passes": len(done), "neural_output": f"{ow}x{oh}",
                                                    "neural_fps_iphone": [round(ios[s]["fps"]) for s in done], "file": last.name}))
        res["codecs"][f"nu-{b}-lanczos"] = {"label": f"nu-media base layer {w} x {h}, Lanczos upscale only", "base": [w, h], "points": lz_pts}
        if sr_pts:
            o = sr_pts[0]["neural_output"].replace("x", " x ")
            tail = "" if sr_pts[0]["neural_output"] == f"{size[0]}x{size[1]}" else f", then Lanczos to {size[0]} x {size[1]}"
            res["codecs"][f"nu-{b}"] = {"label": f"nu-media base layer {w} x {h}, Neural Engine super resolution to {o}{tail}",
                                        "base": [w, h], "points": sr_pts}
    # Full-size base: nu-media's base layer is then plain hardware HEVC, so it shares the HEVC encodes.
    full_base = [b for b, v in c["bases"].items() if v[2] == 0]
    if full_base:
        res["codecs"][f"nu-{full_base[0]}"] = {"label": f"nu-media base layer at full size ({size[0]} x {size[1]}), hardware HEVC",
                                               "base": list(size), "points": [{**p, "file": f"{pre}-hevc-hw-{p['target_kbps']}.mp4"}
                                                                              for p in res["codecs"]["hevc-hw"]["points"]]}

    # nu-media's ladder: at each bitrate, whichever base size and enhancement scored best without dropping frames.
    nu = []
    for r in c["rates"]:
        cands = [(k, p) for k, cc in res["codecs"].items() if k.startswith("nu-") for p in cc["points"] if p["target_kbps"] == r]
        k, p = max(cands, key=lambda x: (x[1]["dropped"] == 0, x[1]["vmaf"]))
        nu.append({**p, "from": k, "base": res["codecs"][k]["base"]})
    res["codecs"]["nu-media"] = {"label": "nu-media, best base size and enhancement at each bitrate", "points": nu}

    ref_k, ref_r = c["reference"]
    ref = next(p for p in res["codecs"][ref_k]["points"] if p["target_kbps"] == ref_r)
    res["same_as_reference"] = {"reference": f"{ref_k} at {ref_r} kbit/s", "vmaf": ref["vmaf"], "reference_kbps": ref["actual_kbps"],
                                "kbps": {k: at_quality(res["codecs"][k]["points"], ref["vmaf"]) for k in ORDER}}
    res["same_as_original"] = {"vmaf": TRANSPARENT, "kbps": {k: at_quality(res["codecs"][k]["points"], TRANSPARENT) for k in ORDER}}
    print("same as reference", res["same_as_reference"], "\nsame as original", res["same_as_original"], flush=True)
    (out / f"results-ladder-{name}.json").write_text(json.dumps(res, indent=2))

    # Whole-frame tiles, frame-aligned to the source (a dropped frame shows as a held frame).
    tdir = out / "tiles"
    tdir.mkdir(exist_ok=True)
    tw, th = c["tile"]

    def tile(src, n):
        dst = tdir / f"{n}.mp4"
        ff("-i", str(src), "-vf", f"setpts=PTS-STARTPTS,fps={c.get('fps', FPS)},scale={tw}:{th}:flags=lanczos,format=yuv420p", "-frames:v", str(src_frames),
           "-an", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dst))
        ff("-ss", "2", "-i", str(dst), "-frames:v", "1", "-q:v", "2", str(tdir / f"{n}.jpg"))
        return dst.name

    res["tiles"] = {"size": [tw, th], "order": ["original", *ORDER], "original": tile(full, "original"), "rates": {}}
    for want in c["show"]:
        row = {}
        for k in ORDER:
            p = next(p for p in res["codecs"][k]["points"] if p["target_kbps"] == want)
            src = out / (p["file"] if k == "nu-media" else f"{pre}-{k}-{want}.mp4")
            extra = {"base": p["base"], "neural": "neural_output" in p} if k == "nu-media" else {}
            row[k] = {"file": tile(src, f"{want}-{k}"), "actual_kbps": p["actual_kbps"], "vmaf": p["vmaf"], "dropped": p["dropped"], **extra}
        res["tiles"]["rates"][str(want)] = row
        print("tiles", want, {k: (v["actual_kbps"], v["vmaf"], v["dropped"]) for k, v in row.items()}, flush=True)
    (out / f"results-ladder-{name}.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
