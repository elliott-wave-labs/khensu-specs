"""Production formats against nu-media: size and quality of the big mezzanine codecs on the same 4K clip.

ProRes (Apple, prores_ks) and DNxHR (Avid, the 4K successor to DNxHD) are encoded on the Mac with ffmpeg from
the ladder's 3840 x 2160 ProRes 422 source, then scored with VMAF (4K model) like every other run. DNxHD itself
only exists at 1920 x 1080, so it is measured on a 1080p downscale and marked as such.

  uv run python formats.py --ladder out/ladder --out out/formats
"""

import argparse
import json
from pathlib import Path

from iphone import SECONDS, dims, ff, kbps, vmaf

MODEL = "vmaf_4k_v0.6.1"
# ProRes 4444 XQ is left out: ffmpeg's prores_ks accepts the profile but codes it at the 4444 rate.
FORMATS = [
    ("prores-proxy", "Apple ProRes 422 Proxy", ["-c:v", "prores_ks", "-profile:v", "0", "-pix_fmt", "yuv422p10le"]),
    ("prores-lt", "Apple ProRes 422 LT", ["-c:v", "prores_ks", "-profile:v", "1", "-pix_fmt", "yuv422p10le"]),
    ("prores-422", "Apple ProRes 422", ["-c:v", "prores_ks", "-profile:v", "2", "-pix_fmt", "yuv422p10le"]),
    ("prores-hq", "Apple ProRes 422 HQ", ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"]),
    ("prores-4444", "Apple ProRes 4444", ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuv444p10le"]),
    ("dnxhr-lb", "Avid DNxHR LB", ["-c:v", "dnxhd", "-profile:v", "dnxhr_lb", "-pix_fmt", "yuv422p"]),
    ("dnxhr-sq", "Avid DNxHR SQ", ["-c:v", "dnxhd", "-profile:v", "dnxhr_sq", "-pix_fmt", "yuv422p"]),
    ("dnxhr-hq", "Avid DNxHR HQ", ["-c:v", "dnxhd", "-profile:v", "dnxhr_hq", "-pix_fmt", "yuv422p"]),
    ("dnxhr-hqx", "Avid DNxHR HQX", ["-c:v", "dnxhd", "-profile:v", "dnxhr_hqx", "-pix_fmt", "yuv422p10le"]),
    ("dnxhr-444", "Avid DNxHR 444", ["-c:v", "dnxhd", "-profile:v", "dnxhr_444", "-pix_fmt", "yuv444p10le"]),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ladder", default="out/ladder")
    ap.add_argument("--out", default="out/formats")
    a = ap.parse_args()
    lad = Path(a.ladder)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    full = lad / "full.mov"
    size = dims(full)
    path = out / "results-formats.json"
    res = {"source": "ladder full.mov: NASA aurora, 3840 x 2160, 29.97 fps, 6 s, ProRes 422 from YouTube's VP9 stream", "vmaf_model": MODEL,
           "encoder": "ffmpeg on an Apple M1 Pro", "formats": {}}
    if path.exists():
        res["formats"] = json.loads(path.read_text())["formats"]
    for k, label, args in FORMATS:
        if k in res["formats"]:
            continue
        f = out / f"{k}.mov"
        ff("-i", str(full), "-an", *args, str(f))
        res["formats"][k] = {"label": label, "kbps": round(kbps(f), 1), "gb_per_hour": round(kbps(f) * 3600 / 8 / 1e6, 1),
                             "vmaf": round(vmaf(f, full, MODEL, size), 2), "size": f"{size[0]}x{size[1]}"}
        print(k, res["formats"][k], flush=True)
        f.unlink()
        path.write_text(json.dumps(res, indent=2))
    # DNxHD 1080p 220x (10-bit 4:2:2 at 29.97 fps is the 220x profile), scored against the 4K source after a Lanczos upscale.
    f = out / "dnxhd-220x.mov"
    ff("-i", str(full), "-an", "-vf", "scale=1920:1080:flags=lanczos", "-c:v", "dnxhd", "-b:v", "220M", "-pix_fmt", "yuv422p10le", str(f))
    res["formats"]["dnxhd-220x"] = {"label": "Avid DNxHD 220x (1080p only)", "kbps": round(kbps(f), 1), "gb_per_hour": round(kbps(f) * 3600 / 8 / 1e6, 1),
                                    "vmaf": round(vmaf(f, full, MODEL, size), 2), "size": "1920x1080"}
    print("dnxhd-220x", res["formats"]["dnxhd-220x"], flush=True)
    f.unlink()
    path.write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
