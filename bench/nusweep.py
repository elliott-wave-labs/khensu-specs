"""nu-media measured end to end on the iPhone, at every bitrate of the 720p sweep.

Each point: the iPhone's hardware HEVC encodes the half-size base layer (360 x 640), the iPhone runs
Apple's low-latency super resolution on the Neural Engine back to 720 x 1280, and the Mac scores the
result with VMAF against the source. The bitrate is the base layer's; nothing else is sent.

  uv run python nusweep.py --device ID --app NuBench.app --source reel.mp4 --start 8 --data ../../khensu-site/sites/khensu-nu/src/data/iphone-reel.json
"""

import argparse
import json
from pathlib import Path

from iphone import CLIPS, SECONDS, Phone, dims, ff, kbps, vmaf

MODEL = CLIPS["reel"]["model"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--start", type=float, default=8)
    ap.add_argument("--rates", default="150,250,500,1000,2000")
    ap.add_argument("--data", required=True, help="iphone-reel.json to add the nu-sr curve to")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    out = Path(a.out) / "nusweep"
    out.mkdir(parents=True, exist_ok=True)

    full, half = out / "full.mov", out / "half.mov"
    ff("-ss", str(a.start), "-t", str(SECONDS), "-i", a.source, "-an", "-vf", "format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(full))
    ff("-i", str(full), "-vf", "scale=360:640:flags=lanczos,format=yuv422p10le", "-c:v", "prores_ks", "-profile:v", "2", str(half))
    size = dims(full)
    phone = Phone(a.device, a.app)
    phone.put(half, "nus-half.mov")

    points = []
    for r in [int(x) for x in a.rates.split(",")]:
        base, raw = f"nus-base-{r}.mp4", f"nus-sr-{r}.nv12"
        rep = phone.encode([{"input": "nus-half.mov", "output": base, "codec": "hevc", "kbps": r},
                            {"input": base, "output": raw, "codec": "sr", "kbps": 0}], out)
        fps = {x["output"]: round(x["fps"]) for x in rep["results"]}
        sr = out / f"nus-sr-{r}.mkv"
        ff("-f", "rawvideo", "-pix_fmt", "nv12", "-s", f"{size[0]}x{size[1]}", "-r", "30", "-i", str(out / raw), "-c:v", "ffv1", str(sr))
        (out / raw).unlink()
        p = {"target_kbps": r, "actual_kbps": round(kbps(out / base), 1), "vmaf": round(vmaf(sr, full, MODEL, size), 2),
             "encode_fps_iphone": fps[base], "sr_fps_iphone": fps[raw]}
        points.append(p)
        print(p, flush=True)
        sr.unlink()
        (out / base).unlink()

    d = json.loads(Path(a.data).read_text())
    d["codecs"]["nu-sr"] = {"label": "nu-media: HEVC iPhone hardware at half size + Apple low-latency super resolution (Neural Engine), all on iPhone",
                           "device": rep["device"], "os": rep["os"], "points": points}
    Path(a.data).write_text(json.dumps(d, indent=2))
    full.unlink()
    half.unlink()


if __name__ == "__main__":
    main()
