"""nu-media photo with Apple super resolution, measured on a Mac.

The still is sent as a HEIC at half or quarter size, enhanced 4x with VTSuperResolutionScaler
(mac/nuenhance sr, the same model the iPhone runs on its Neural Engine), scaled to the screen size
and scored with VMAF against the original. Run photo.py first; this reads its ref.png and results.

  uv run python photo_sr.py --out out/photo
"""

import argparse
import json
from pathlib import Path

from photo import H, W, ff, match, sips, vmaf

NUENHANCE = Path(__file__).parent / "mac" / "nuenhance"


def enhance(png, out):
    one = out / "sr-in.mov"
    ff("-loop", "1", "-i", str(png), "-t", "0.1", "-r", "10", "-vf", "format=yuv422p10le",
       "-c:v", "prores_ks", "-profile:v", "3", str(one))
    up = out / "sr-out.mov"
    import subprocess
    subprocess.run([str(NUENHANCE), "sr", str(one), str(up), "400000"], check=True, capture_output=True)
    frame = out / "sr.png"
    ff("-i", str(up), "-frames:v", "1", str(frame))
    return frame


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="out/photo")
    a = ap.parse_args()
    out = Path(a.out)
    ref = out / "ref.png"
    res = json.loads((out / "results-photo.json").read_text())

    for name, div in (("half", 2), ("quarter", 4)):
        size = (W // div // 2 * 2, H // div // 2 * 2)

        def nu_sr(q, size=size):
            n, png = sips(ref, out / f"nu-{name}.heic", "heic", round(q), size)
            return n, vmaf(enhance(png, out), ref, up=True)

        for k in ("jpeg", "heic"):
            q, n, score = match(nu_sr, res[k]["vmaf"], 5, 100, steps=7)
            res[f"nu-sr-{name}-vs-{k}"] = {"bytes": n, "vmaf": round(score, 2), "heic_quality": round(q),
                                           "sent": f"{size[0]}x{size[1]}"}
            print(name, k, res[f"nu-sr-{name}-vs-{k}"], flush=True)

    (out / "results-photo.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
