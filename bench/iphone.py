"""Rate-quality benchmark with the encodes done on a real iPhone.

H.264 and HEVC are encoded by the iPhone's hardware encoder (bench/ios, NuBench) at live-call
settings: real time, no frame reordering, bitrate capped per second. The iPhone has no AV1 encoder,
so the AV1 rows are SVT-AV1 on the Mac at real-time call settings (CBR, low delay), as in codecs.py.
The nu-media rows are the base layer only, at half width and height with a Lanczos upscale; the
Neural Engine enhancement doesn't exist yet. Everything is scored with VMAF on the Mac.

  uv run python iphone.py --device 00008150-000079CC2678401C --app /tmp/nubench-dd/Build/Products/Release-iphoneos/NuBench.app \\
      --clip aurora=SRC.mp4@24 --clip reel=SRC.mp4@8 --out out/
"""

import argparse
import json
import math
import re
import subprocess
import time
from pathlib import Path

BUNDLE = "nu.khensu.bench"
SECONDS = 6

CLIPS = {
    # 3840 x 2160 landscape; VMAF's 4K model; tiles are 1:1 crops of 960 x 540.
    "aurora": {"rates": [2000, 4000, 8000, 16000], "show": 4000, "model": "vmaf_4k_v0.6.1", "crop": "960:540:1440:420", "row": 3},
    # 720 x 1280 portrait; tiles are 1:1 crops of 360 x 640.
    "reel": {"rates": [250, 500, 1000, 2000], "show": 500, "model": "vmaf_v0.6.1", "crop": "360:640:180:160", "row": 6},
}

PHONE = {
    "h264-hw": {"label": "H.264, iPhone hardware", "codec": "h264", "input": "full"},
    "hevc-hw": {"label": "HEVC, iPhone hardware", "codec": "hevc", "input": "full"},
    "nu-base": {"label": "nu-media base layer, HEVC iPhone hardware at half size", "codec": "hevc", "input": "half"},
}
MAC = {
    "av1-svt-rt": {"label": "AV1, SVT-AV1 real time on the Mac (no iPhone AV1 encoder)", "input": "full"},
    "nu-base-av1": {"label": "nu-media base layer, SVT-AV1 real time on the Mac at half size", "input": "half"},
}
GRID = ["h264-hw", "hevc-hw", "av1-svt-rt", "nu-base", "nu-base-av1"]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def ff(*args):
    return run(["ffmpeg", "-hide_banner", "-y", "-loglevel", "error", *args])


def kbps(path):
    return path.stat().st_size * 8 / 1000 / SECONDS


def dims(path):
    w, h = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)]).stdout.strip().split(",")
    return int(w), int(h)


def vmaf(dist, ref, model, size):
    w, h = size
    post = f"scale={w}:{h}:flags=lanczos," if dims(dist) != size else ""
    chain = (f"[0:v]{post}setpts=PTS-STARTPTS,format=yuv420p[d];[1:v]setpts=PTS-STARTPTS,format=yuv420p[r];"
             f"[d][r]libvmaf=model=version={model}:n_threads=10")
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(dist), "-i", str(ref), "-lavfi", chain, "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    return float(re.search(r"VMAF score: ([\d.]+)", err).group(1))


class Phone:
    def __init__(self, device, app):
        self.device = device
        run(["xcrun", "devicectl", "device", "install", "app", "--device", device, app])

    def _dc(self, *args):
        return run(["xcrun", "devicectl", *args, "--device", self.device], timeout=3600)

    def put(self, local, name):
        self._dc("device", "copy", "to", "--source", str(local), "--destination", f"Documents/{name}",
                 "--domain-type", "appDataContainer", "--domain-identifier", BUNDLE)

    def get(self, name, local):
        self._dc("device", "copy", "from", "--source", f"Documents/{name}", "--destination", str(local),
                 "--domain-type", "appDataContainer", "--domain-identifier", BUNDLE)

    def encode(self, jobs, out):
        """Runs jobs [{input, output, codec, kbps}] on the phone and copies the outputs back."""
        f = out / "jobs.json"
        f.write_text(json.dumps(jobs))
        self.put(f, "jobs.json")
        r = run(["xcrun", "devicectl", "device", "process", "launch", "--device", self.device, "--terminate-existing", "--console", BUNDLE], timeout=3600)
        print(r.stdout[-2000:], flush=True)
        self.get("results-ios.json", out / "results-ios.json")
        report = json.loads((out / "results-ios.json").read_text())
        for j in jobs:
            self.get(j["output"], out / j["output"])
        return report


def steer(points, want):
    """Target to ask for so the encoder lands on `want` actual kbit/s, from (target, actual) pairs."""
    pts = sorted(points)
    for (t0, a0), (t1, a1) in zip(pts, pts[1:]):
        if a0 <= want <= a1:
            f = (math.log(want) - math.log(a0)) / (math.log(a1) - math.log(a0))
            return round(math.exp(math.log(t0) + f * (math.log(t1) - math.log(t0))))
    t, a = min(pts, key=lambda p: abs(math.log(p[1] / want)))
    return round(t * want / a)


def av1(src, dst, rate):
    ff("-i", str(src), "-an", "-pix_fmt", "yuv420p", "-c:v", "libsvtav1", "-preset", "10", "-b:v", f"{rate}k",
       "-svtav1-params", "rc=2:pred-struct=1", str(dst))


def bench_clip(name, src, start, phone, root):
    c = CLIPS[name]
    out = root / name
    out.mkdir(parents=True, exist_ok=True)
    sw, sh = dims(Path(src))
    full = out / "full.mov"
    half = out / "half.mov"
    ff("-ss", str(start), "-t", str(SECONDS), "-i", src, "-an", "-vf", "format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(full))
    ff("-i", str(full), "-vf", f"scale={sw // 2}:{sh // 2}:flags=lanczos,format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(half))
    size = (sw, sh)
    inputs = {"full": full, "half": half}
    phone.put(full, f"{name}-full.mov")
    phone.put(half, f"{name}-half.mov")

    res = {"clip": name, "source": Path(src).name, "start": start, "seconds": SECONDS, "size": f"{sw}x{sh}",
           "vmaf_model": c["model"], "codecs": {}}

    jobs = [{"input": f"{name}-{p['input']}.mov", "output": f"{name}-{k}-{r}.mp4", "codec": p["codec"], "kbps": r}
            for k, p in PHONE.items() for r in c["rates"]]
    report = phone.encode(jobs, out)
    res["device"], res["os"] = report["device"], report["os"]
    fps = {r["output"]: r["fps"] for r in report["results"]}
    for k, p in PHONE.items():
        rows = []
        for r in c["rates"]:
            f = out / f"{name}-{k}-{r}.mp4"
            rows.append({"target_kbps": r, "actual_kbps": round(kbps(f), 1), "vmaf": round(vmaf(f, full, c["model"], size), 2),
                         "encode_fps_iphone": round(fps[f.name])})
            print(name, k, rows[-1], flush=True)
            f.unlink()
        res["codecs"][k] = {"label": p["label"], "points": rows}
    for k, m in MAC.items():
        rows = []
        for r in c["rates"]:
            f = out / f"{name}-{k}-{r}.mp4"
            av1(inputs[m["input"]], f, r)
            rows.append({"target_kbps": r, "actual_kbps": round(kbps(f), 1), "vmaf": round(vmaf(f, full, c["model"], size), 2)})
            print(name, k, rows[-1], flush=True)
            f.unlink()
        res["codecs"][k] = {"label": m["label"], "points": rows}

    # Equal-bitrate grid: steer every encoder to the same actual bitrate.
    want = c["show"]
    gjobs = []
    for k, p in PHONE.items():
        t = steer([(q["target_kbps"], q["actual_kbps"]) for q in res["codecs"][k]["points"]], want)
        gjobs.append({"input": f"{name}-{p['input']}.mov", "output": f"{name}-grid-{k}.mp4", "codec": p["codec"], "kbps": t})
    phone.encode(gjobs, out)
    for k, m in MAC.items():
        t = steer([(q["target_kbps"], q["actual_kbps"]) for q in res["codecs"][k]["points"]], want)
        av1(inputs[m["input"]], out / f"{name}-grid-{k}.mp4", t)
    res["grid"] = {"want_kbps": want, "codecs": {}}
    for k in GRID:
        f = out / f"{name}-grid-{k}.mp4"
        res["grid"]["codecs"][k] = {"actual_kbps": round(kbps(f), 1), "vmaf": round(vmaf(f, full, c["model"], size), 2)}
        print(name, "grid", k, res["grid"]["codecs"][k], flush=True)

    # Comparison video: the source and each grid encode, 1:1 crops, in rows of c["row"].
    tiles = [full] + [out / f"{name}-grid-{k}.mp4" for k in GRID]
    n = len(tiles)
    chains = []
    for i, t in enumerate(tiles):
        up = f"scale={sw}:{sh}:flags=lanczos," if dims(t) != size else ""
        chains.append(f"[{i}:v]{up}crop={c['crop']},setpts=PTS-STARTPTS,format=yuv420p[t{i}]")
    per = c["row"]
    rows = []
    for r0 in range(0, n, per):
        ids = "".join(f"[t{i}]" for i in range(r0, min(n, r0 + per)))
        rows.append(f"{ids}hstack={min(n, r0 + per) - r0}[r{r0}]")
    tail = "".join(f"[r{r0}]" for r0 in range(0, n, per))
    stack = f"{tail}vstack={len(rows)}[v]" if len(rows) > 1 else f"{tail}null[v]"
    grid = out / f"compare-{name}.mp4"
    ff(*sum((["-i", str(t)] for t in tiles), []), "-filter_complex", ";".join(chains + rows + [stack]), "-map", "[v]",
       "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(grid))
    ff("-ss", "2", "-i", str(grid), "-frames:v", "1", "-q:v", "3", str(out / f"compare-{name}.jpg"))
    (out / f"results-{name}.json").write_text(json.dumps(res, indent=2))
    for f in (full, half, *out.glob(f"{name}-grid-*.mp4")):
        f.unlink()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--clip", action="append", required=True, help="name=SOURCE@START_SECONDS")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    root = Path(a.out)
    phone = Phone(a.device, a.app)
    for spec in a.clip:
        name, rest = spec.split("=", 1)
        src, start = rest.rsplit("@", 1)
        t0 = time.monotonic()
        bench_clip(name, src, float(start), phone, root)
        print(f"{name} done in {time.monotonic() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
