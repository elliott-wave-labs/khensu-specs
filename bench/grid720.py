"""720p comparison at one low bitrate: the original, nu-media, and every codec, all shown at 720 x 1280.

Top row, encoded on the iPhone: nu-media (hardware HEVC at 360 x 640, then Apple's low-latency super
resolution on the Neural Engine back to 720 x 1280), H.264 and HEVC hardware at 720 x 1280.
Bottom row, encoded on the Mac at 720 x 1280: AV1 real time, AV1 best quality, VP9 real time and
HEVC software (x265). Every encoder is steered to the same actual bitrate.

  uv run python grid720.py --device ID --app NuBench.app --source reel.mp4 --start 8 --sweep out/reel/results-reel.json --out out/
"""

import argparse
import json
from pathlib import Path

from iphone import CLIPS, SECONDS, Phone, dims, ff, kbps, steer, vmaf

WANT = 500
CROP = CLIPS["reel"]["crop"]
MODEL = CLIPS["reel"]["model"]

MAC = {
    "av1-rt": ("AV1, SVT-AV1 real time", lambda r: ["-c:v", "libsvtav1", "-preset", "10", "-b:v", f"{r}k", "-svtav1-params", "rc=2:pred-struct=1"]),
    "av1-best": ("AV1, SVT-AV1 best quality (preset 4, lookahead; not live)", lambda r: ["-c:v", "libsvtav1", "-preset", "4", "-b:v", f"{r}k", "-svtav1-params", "rc=1"]),
    "vp9-rt": ("VP9, libvpx real time", lambda r: ["-c:v", "libvpx-vp9", "-deadline", "realtime", "-cpu-used", "8", "-row-mt", "1",
                                                     "-b:v", f"{r}k", "-minrate", f"{r}k", "-maxrate", f"{r}k"]),
    "hevc-x265": ("HEVC, x265 software (preset slow)", lambda r: ["-c:v", "libx265", "-preset", "slow", "-b:v", f"{r}k", "-x265-params", "log-level=error"]),
}
ROW1 = ["original", "nu-media", "h264-hw", "hevc-hw"]
ROW2 = list(MAC)


def mac_encode(key, src, out):
    enc = MAC[key][1]
    f = out / f"g720-{key}.mp4"
    target = WANT
    for _ in range(5):
        ff("-i", str(src), "-an", "-pix_fmt", "yuv420p", *enc(round(target)), str(f))
        got = kbps(f)
        if abs(got - WANT) / WANT < 0.03:
            break
        target *= WANT / got
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--start", type=float, default=8)
    ap.add_argument("--sweep", required=True, help="results-reel.json from iphone.py, used to steer the phone encoders")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    out = Path(a.out) / "g720"
    out.mkdir(parents=True, exist_ok=True)
    sweep = json.loads(Path(a.sweep).read_text())

    full, half = out / "full.mov", out / "half.mov"
    ff("-ss", str(a.start), "-t", str(SECONDS), "-i", a.source, "-an", "-vf", "format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(full))
    ff("-i", str(full), "-vf", "scale=360:640:flags=lanczos,format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(half))
    size = dims(full)

    phone = Phone(a.device, a.app)
    phone.put(full, "g720-full.mov")
    phone.put(half, "g720-half.mov")
    t = {k: steer([(p["target_kbps"], p["actual_kbps"]) for p in sweep["codecs"][k]["points"]], WANT) for k in ["h264-hw", "hevc-hw", "nu-base"]}
    jobs = [
        {"input": "g720-full.mov", "output": "g720-h264-hw.mp4", "codec": "h264", "kbps": t["h264-hw"]},
        {"input": "g720-full.mov", "output": "g720-hevc-hw.mp4", "codec": "hevc", "kbps": t["hevc-hw"]},
        {"input": "g720-half.mov", "output": "g720-nu-base.mp4", "codec": "hevc", "kbps": t["nu-base"]},
        {"input": "g720-nu-base.mp4", "output": "g720-nu-sr.nv12", "codec": "sr", "kbps": 0},
    ]
    report = phone.encode(jobs, out)
    fps = {r["output"]: round(r["fps"]) for r in report["results"]}
    sr = out / "g720-nu-media.mkv"
    ff("-f", "rawvideo", "-pix_fmt", "nv12", "-s", f"{size[0]}x{size[1]}", "-r", "30", "-i", str(out / "g720-nu-sr.nv12"), "-c:v", "ffv1", str(sr))
    (out / "g720-nu-sr.nv12").unlink()

    files = {"original": full, "nu-media": sr, "h264-hw": out / "g720-h264-hw.mp4", "hevc-hw": out / "g720-hevc-hw.mp4"}
    for k in MAC:
        files[k] = mac_encode(k, full, out)
        print("mac", k, flush=True)

    res = {"clip": "reel", "source": Path(a.source).name, "start": a.start, "seconds": SECONDS, "size": f"{size[0]}x{size[1]}",
           "want_kbps": WANT, "device": report["device"], "os": report["os"], "vmaf_model": MODEL, "tiles": {}}
    labels = {"original": "Source", "nu-media": "nu-media: HEVC iPhone hardware at 360 x 640 + Apple low-latency super resolution (Neural Engine)",
              "h264-hw": "H.264, iPhone hardware", "hevc-hw": "HEVC, iPhone hardware", **{k: v[0] for k, v in MAC.items()}}
    bits = {"nu-media": out / "g720-nu-base.mp4"}
    for k in ROW1[1:] + ROW2:
        b = bits.get(k, files[k])
        res["tiles"][k] = {"label": labels[k], "actual_kbps": round(kbps(b), 1), "vmaf": round(vmaf(files[k], full, MODEL, size), 2)}
        print(k, res["tiles"][k], flush=True)
    res["tiles"]["nu-base-lanczos"] = {"label": "nu-media base with a Lanczos upscale instead of super resolution",
                                       "actual_kbps": res["tiles"]["nu-media"]["actual_kbps"], "vmaf": round(vmaf(bits["nu-media"], full, MODEL, size), 2)}
    res["iphone_fps"] = {"h264-hw": fps["g720-h264-hw.mp4"], "hevc-hw": fps["g720-hevc-hw.mp4"], "nu-base": fps["g720-nu-base.mp4"],
                         "super_resolution": fps["g720-nu-sr.nv12"]}
    print("lanczos", res["tiles"]["nu-base-lanczos"], "fps", res["iphone_fps"], flush=True)

    ins, chains = [], []
    for i, k in enumerate(ROW1 + ROW2):
        ins += ["-i", str(files[k])]
        chains.append(f"[{i}:v]crop={CROP},setpts=PTS-STARTPTS,format=yuv420p[t{i}]")
    graph = ";".join(chains + ["[t0][t1][t2][t3]hstack=4[r0]", "[t4][t5][t6][t7]hstack=4[r1]", "[r0][r1]vstack=2[v]"])
    grid = out / "compare-720p.mp4"
    ff(*ins, "-filter_complex", graph, "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(grid))
    ff("-ss", "2", "-i", str(grid), "-frames:v", "1", "-q:v", "3", str(out / "compare-720p.jpg"))
    (out / "results-720p.json").write_text(json.dumps(res, indent=2))
    for f in [full, half, sr, *out.glob("g720-*.mp4")]:
        f.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
