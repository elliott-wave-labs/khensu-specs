"""nu-media rebuilt to 4K on the receiver: the ladder's nu-media outputs at the shown bitrates go through one more
Neural Engine super-resolution pass on the iPhone (2x), then Lanczos to the 4K display size on the Mac.

The bits on the wire are unchanged, so the bitrate is the ladder's. VMAF is scored at the source size after a
downscale, because there is no 4K original to score against; the 4K tile is for looking at.

  uv run python to4k.py --clip reel --device <id> --app <NuBench.app>
"""

import argparse
import json
from pathlib import Path

from iphone import dims, ff, vmaf
from ladder import CLIPS, USBPhone, frames, pass_kbps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True, choices=list(CLIPS))
    ap.add_argument("--device", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--out", default="out")
    ap.add_argument("--reuse", action="store_true", help="use the last phone run in <out>/4k instead of running again")
    a = ap.parse_args()
    c = CLIPS[a.clip]
    out = Path(a.out) / ("ladder" if a.clip == "nasa4k" else f"ladder-{a.clip}")
    resf = out / f"results-ladder-{a.clip}.json"
    res = json.loads(resf.read_text())
    full = out / "full.mov"
    sw, sh = dims(full)
    tw, th = (2160, 3840) if sh > sw else (3840, 2160)
    work = out / "4k"
    work.mkdir(exist_ok=True)
    phone = USBPhone(a.device, a.app)

    by_rate = {p["target_kbps"]: p for p in res["codecs"]["nu-media"]["points"]}
    jobs, plan = [], {}
    for r in c["show"]:
        src = out / by_rate[r]["file"]
        w, h = dims(src)
        name = f"4k-{a.clip}-{r}"
        if not a.reuse:
            phone.put(src, f"{name}-in{src.suffix}")
        jobs.append({"input": f"{name}-in{src.suffix}", "output": f"{name}-sr.mov", "codec": "sr", "kbps": pass_kbps(w * 2, h * 2)})
        plan[r] = (name, src, (w, h))
    if not a.reuse:
        phone.batch(jobs, work)
    ios = {x["output"]: x for x in json.loads((work / "results-ios.json").read_text())["results"]}

    tdir = out / "tiles"
    for r, (name, src, (w, h)) in plan.items():
        sr = work / f"{name}-sr.mov"
        ok = ios.get(sr.name, {}).get("frames", 0) > 0
        if ok:
            phone.get(sr.name, sr)
        stage = sr if ok else src
        dst = tdir / f"{r}-nu-media-4k.mp4"
        ff("-i", str(stage), "-vf", f"setpts=PTS-STARTPTS,scale={tw}:{th}:flags=lanczos,format=yuv420p",
           "-an", "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-level", "5.1", "-movflags", "+faststart", str(dst))
        ff("-ss", "2", "-i", str(dst), "-frames:v", "1", "-q:v", "2", str(tdir / f"{r}-nu-media-4k.jpg"))
        t = res["tiles"]["rates"][str(r)]["nu-media"]
        rec = {"file": dst.name, "actual_kbps": t["actual_kbps"], "dropped": max(0, res["source_frames"] - frames(dst)),
               "vmaf": round(vmaf(dst, full, res["vmaf_model"], (sw, sh)), 2), "size": [tw, th], "base": [w, h],
               "neural_pass": f"{w} x {h} to {w * 2} x {h * 2}" if ok else None,
               "neural_fps_iphone": round(ios[sr.name]["fps"]) if ok else None}
        res["tiles"]["rates"][str(r)]["nu-media-4k"] = rec
        print(r, rec, flush=True)
    resf.write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
