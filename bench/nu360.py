"""nu-360 prototype and benchmark: viewport-adaptive 360 video against whole-sphere equirectangular video.

Baselines code the whole equirectangular frame (3840 x 1920) at each rate: H.264 and HEVC on the Mac's VideoToolbox
hardware encoder (constant bit rate) and SVT-AV1 real time (CBR, low delay, preset 10).

nu-360 reprojects the sphere to an equi-angular cubemap (EAC, 3 x 2 faces of 960 px, 2880 x 1920: the same 10.7 px
per degree as the source at the equator, 25% fewer pixels), cuts it into 24 tiles of 480 x 480 (2 x 2 per face) and
codes every tile as its own hardware HEVC stream at two rates, plus a low-resolution whole sphere (EAC 720 x 480).
A viewer always receives the same number of objects per 1 s segment, whatever it looks at: the sphere, 4 core tiles at
the high rate and 4 margin tiles at the medium rate. Every segment of a slot class is padded to that class's largest
segment, so the bytes on the wire don't depend on where the viewer looks. The receiver composites the tiles over the
upscaled sphere and renders its viewport.

Bit rates are "wire" rates: the stealth constant-rate rule applied to every method alike (each 1 s segment padded to
the largest segment of its slot class). nu-360's wire rate counts only what one viewer receives; the broadcaster's
upload (every tile at both rates) is reported separately.

Scoring:
  viewport  each viewer renders a 1280 x 720 viewport (90 x 58.7 degrees) with ffmpeg v360; VMAF (vmaf_v0.6.1) and
            PSNR-Y against the same viewport rendered from the source. Six fixed viewers (front, right, back, left,
            up, down) and one turning its head at 30 degrees a second, whose tiles are chosen 0.5 s before each segment
            from a gyro-style prediction, so it sees the low-resolution sphere where its prediction falls short.
  ws-psnr   WS-PSNR (luma, cos-latitude weights) of the whole sphere back in the source equirectangular frame;
            for nu-360 the sphere a front viewer received.

  uv run --with numpy --with pillow python nu360.py --clip metro --source out/360/src/metro.webm --out out/360
  uv run --with numpy --with pillow python nu360.py --clip bled --source out/360/src/bled.webm --out out/360
"""

import argparse
import json
import math
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image

CLIPS = {
    "metro": {
        "source": "Moscow metro train Sokolniki interior shot on spherical camera 2023-03 (Svetlov Artem), Wikimedia Commons, CC0: "
                  "VP9, 3840 x 1920 equirectangular, 30 fps, 11.2 Mbit/s",
        "url": "https://commons.wikimedia.org/wiki/File:Moscow_metro_train_Sokolniki_interior_shot_on_spherical_camera_2023-03.MP4.webm",
        "sha256": "e90506bb9e3f7a12d4fe7e6a53271a73225a51db14fbe2e9c2df32ae5fa941c4", "start": 10, "seconds": 8,
    },
    "bled": {
        "source": "Video 360°. Timelapse. Bled Lake in Slovenia (Fabio Casati), Wikimedia Commons, CC BY 3.0: "
                  "VP9, 3840 x 1920 equirectangular, 29.9 fps, 16.2 Mbit/s",
        "url": "https://commons.wikimedia.org/wiki/File:Video_360%C2%B0._Timelapse._Bled_Lake_in_Slovenia..webm",
        "sha256": "a426060918287da43cb6b24737d284f3825308a53ae44b953c2f3b220bd2fcea", "start": 0, "seconds": 8,
    },
}
RATES = [1000, 2000, 4000, 8000, 16000]
SHOW = [2000, 4000]
FPS = 30
SEG = 1.0                        # segment and GOP length, seconds
LEAD = 0.5                       # tiles for a segment are requested this long before it plays
SRC = (3840, 1920)
EAC = (2880, 1920)
TILE = 480
LQ = (720, 480)                  # whole sphere, EAC with 240 px faces
VP = (1280, 720, 90.0, 2 * math.degrees(math.atan(math.tan(math.radians(45)) * 720 / 1280)))
MARGIN_FOV = (130.0, 100.0)
CORE, MARGIN = 4, 4
LQ_SHARE, CORE_SHARE, MARGIN_SHARE = 0.2, 0.8 * 2 / 3 / CORE, 0.8 / 3 / MARGIN
PAN_SPEED = 30.0                 # degrees per second
VIEWERS = {"front": (0, 0), "right": (90, 0), "back": (180, 0), "left": (-90, 0), "up": (0, 60), "down": (0, -55), "pan": None}
METHODS = {
    "h264-hw": "H.264 equirectangular, VideoToolbox hardware, CBR",
    "hevc-hw": "HEVC equirectangular, VideoToolbox hardware, CBR",
    "av1-svt-rt": "AV1 equirectangular, SVT-AV1 real time (CBR, low delay, preset 10)",
    "eac-hevc": "HEVC equi-angular cubemap, whole sphere, VideoToolbox hardware, CBR (projection only, no tiles)",
    "nu-360": "nu-360: EAC tiles, HEVC hardware, 4 core + 4 margin tiles + low-resolution sphere, constant-rate",
}
ORDER = ["h264-hw", "hevc-hw", "av1-svt-rt", "eac-hevc", "nu-360"]
KEYS = ["-g", str(int(FPS * SEG)), "-force_key_frames", f"expr:eq(mod(n,{int(FPS * SEG)}),0)"]


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, **kw)


def ff(*args):
    return run(["ffmpeg", "-hide_banner", "-y", "-loglevel", "error", *args])


def vt(codec, r):
    tag = ["-tag:v", "hvc1"] if codec == "hevc" else []
    return ["-c:v", f"{codec}_videotoolbox", "-allow_sw", "0", "-constant_bit_rate", "1", "-b:v", f"{r}k", *KEYS, *tag]


def av1(r):
    return ["-c:v", "libsvtav1", "-preset", "10", "-b:v", f"{r}k", "-svtav1-params", "rc=2:pred-struct=1", *KEYS]


def segments(path, secs):
    """Bytes in each 1 s segment of the video stream."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time,size", "-of", "csv=p=0", str(path)],
              text=True).stdout
    seg = [0] * math.ceil(secs / SEG)
    for line in out.splitlines():
        t, s = (line.split(",") + [""])[:2]
        if t and s and t != "N/A":
            seg[min(len(seg) - 1, int(float(t) / SEG))] += int(s)
    return seg


def kb(bytes_per_seg):
    return round(bytes_per_seg * 8 / 1000 / SEG, 1)


# ---- viewers and tile choice

def direction(viewer, t):
    if viewer == "pan":
        return ((PAN_SPEED * t + 180) % 360) - 180, 0.0
    return VIEWERS[viewer]


def tile_ids():
    nx, ny = EAC[0] // TILE, EAC[1] // TILE
    return [(i % nx * TILE, i // nx * TILE) for i in range(nx * ny)]


def visible(idmap, yaw, pitch, hfov, vfov):
    """Pixel count of each tile in a viewport, from an EAC image whose tiles are painted with their index."""
    w, h = 320, round(320 * math.tan(math.radians(vfov / 2)) / math.tan(math.radians(hfov / 2)))
    raw = run(["ffmpeg", "-v", "error", "-i", str(idmap), "-vf",
               f"format=gray,v360=input=eac:output=flat:h_fov={hfov}:v_fov={vfov}:yaw={yaw}:pitch={pitch}:interp=near:w={w}:h={h}",
               "-f", "rawvideo", "-pix_fmt", "gray", "-"]).stdout
    u, c = np.unique(np.frombuffer(raw, np.uint8), return_counts=True)
    return {int(x) // 4 - 1: int(n) for x, n in zip(u, c) if x}


def choose(idmap, viewer, secs):
    """Core and margin tiles for every segment, chosen LEAD seconds early from the direction then plus angular velocity."""
    plan = []
    for s in range(math.ceil(secs / SEG)):
        t0 = max(0.0, s * SEG - LEAD)
        y0, p0 = direction(viewer, t0)
        y1, _ = direction(viewer, t0 + 0.1)
        vel = ((y1 - y0 + 180) % 360 - 180) / 0.1
        yaw = ((y0 + vel * (s * SEG + SEG / 2 - t0)) + 180) % 360 - 180
        inner = visible(idmap, yaw, p0, VP[2], VP[3])
        wide = visible(idmap, yaw, p0, *MARGIN_FOV)
        rank = sorted(wide, key=lambda k: (-inner.get(k, 0), -wide[k]))
        plan.append({"segment": s, "yaw": round(yaw, 1), "pitch": p0, "core": rank[:CORE], "margin": rank[CORE:CORE + MARGIN]})
    return plan


# ---- rendering and scoring

def v360(src_proj, viewer, cmdfile):
    w, h, hf, vf = VP
    base = f"v360@vp=input={src_proj}:output=flat:h_fov={hf}:v_fov={vf:.4f}:w={w}:h={h}:interp=cube"
    if viewer == "pan":
        return f"sendcmd=f={cmdfile},{base}"
    yaw, pitch = VIEWERS[viewer]
    return f"{base}:yaw={yaw}:pitch={pitch}"


def pan_commands(path, secs):
    lines = []
    for n in range(int(secs * FPS)):
        t = n / FPS
        lines.append(f"{t:.4f} v360@vp yaw {direction('pan', t)[0]:.3f};")
    path.write_text("\n".join(lines) + "\n")


def composite(inputs_offset, plan, tiles, lq_input, key):
    """Filter chain that rebuilds the EAC frame a viewer sees: upscaled sphere, margin tiles, then core tiles."""
    chain = [f"[{lq_input}:v]setpts=PTS-STARTPTS,scale={EAC[0]}:{EAC[1]}:flags=lanczos,format=yuv420p[{key}b0]"]
    used = []
    for cls in ("margin", "core"):
        ids = sorted({i for p in plan for i in p[cls]})
        for i in ids:
            segs = [p["segment"] for p in plan if i in p[cls]]
            used.append((cls, i, segs))
    files = []
    cur = f"{key}b0"
    for n, (cls, i, segs) in enumerate(used):
        x, y = tiles[i]
        en = "+".join(f"between(t,{s * SEG},{(s + 1) * SEG - 0.001})" for s in segs)
        idx = inputs_offset + n
        chain.append(f"[{idx}:v]setpts=PTS-STARTPTS[{key}t{n}]")
        chain.append(f"[{cur}][{key}t{n}]overlay=x={x}:y={y}:enable='{en}'[{key}b{n + 1}]")
        cur = f"{key}b{n + 1}"
        files.append((cls, i))
    return chain, cur, files


def vmaf_log(log):
    m = json.loads(Path(log).read_text())["pooled_metrics"]
    Path(log).unlink()
    return round(m["vmaf"]["mean"], 2), round(m["psnr_y"]["mean"], 2)


def score_viewport(inputs, chain, last, src_proj, viewer, ref, cmdfile, log):
    graph = ";".join(chain + [f"[{last}]format=yuv420p,{v360(src_proj, viewer, cmdfile)},format=yuv420p[d]",
                              f"[{len(inputs)}:v]setpts=PTS-STARTPTS,format=yuv420p[r]",
                              f"[d][r]libvmaf=model=version=vmaf_v0.6.1:feature=name=psnr:n_threads=4:log_fmt=json:log_path={log}"])
    args = sum((["-i", str(f)] for f in inputs), []) + ["-i", str(ref)]
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", *args, "-filter_complex", graph, "-f", "null", "-"])
    return vmaf_log(log)


def gray_frames(args, graph, step):
    w, h = SRC
    p = subprocess.Popen(["ffmpeg", "-v", "error", *args, "-filter_complex", f"{graph};[x]select='not(mod(n\\,{step}))',format=gray[o]",
                          "-map", "[o]", "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    try:
        while True:
            b = p.stdout.read(w * h)
            if len(b) < w * h:
                break
            yield np.frombuffer(b, np.uint8).reshape(h, w).astype(np.float32)
    finally:
        p.stdout.close()
        p.kill()
        p.wait()


def ws_psnr(dist_args, dist_graph, full, step=4):
    w, h = SRC
    wt = np.cos((np.arange(h) + 0.5 - h / 2) * math.pi / h).astype(np.float32)[:, None]
    tot = wt.sum() * w
    vals = []
    ref = gray_frames(["-i", str(full)], "[0:v]setpts=PTS-STARTPTS[x]", step)
    for d, r in zip(gray_frames(dist_args, dist_graph, step), ref):
        mse = float(((d - r) ** 2 * wt).sum() / tot)
        vals.append(99.0 if mse == 0 else 10 * math.log10(255 ** 2 / mse))
    return round(sum(vals) / len(vals), 2)


# ---- summaries

def interp(points, x_key, y_key, x):
    pts = sorted((p[x_key], p[y_key]) for p in points)
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            f = (math.log(x) - math.log(x0)) / (math.log(x1) - math.log(x0))
            return round(y0 + f * (y1 - y0), 2)
    return None


def kbps_for(points, key, q):
    pts = sorted((p[key], p["wire_kbps"]) for p in points)
    for (q0, r0), (q1, r1) in zip(pts, pts[1:]):
        if q0 <= q <= q1 and q1 > q0:
            f = (q - q0) / (q1 - q0)
            return round(math.exp(math.log(r0) + f * (math.log(r1) - math.log(r0))), 1)
    return None


def bd_rate(test, ref, key):
    """Mean bit-rate difference (%) of test against ref at equal quality, over their shared quality range."""
    lo = max(min(p[key] for p in test), min(p[key] for p in ref))
    hi = min(max(p[key] for p in test), max(p[key] for p in ref))
    if hi <= lo:
        return None
    qs = [lo + (hi - lo) * i / 50 for i in range(51)]
    d = [math.log(kbps_for(test, key, q)) - math.log(kbps_for(ref, key, q)) for q in qs]
    return round((math.exp(sum(d) / len(d)) - 1) * 100, 1)


# ---- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", required=True, choices=list(CLIPS))
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", default="out/360")
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    c = CLIPS[a.clip]
    root = Path(a.out)
    out = root / a.clip
    out.mkdir(parents=True, exist_ok=True)
    secs = c["seconds"]
    full, eac, lqsrc = out / "full.mov", out / "eac.mov", out / "lq-src.mov"
    pro = ["-c:v", "prores_ks", "-profile:v", "3", "-pix_fmt", "yuv422p10le"]
    if not full.exists():
        ff("-ss", str(c["start"]), "-t", str(secs), "-i", a.source, "-an", "-vf", f"fps={FPS},scale={SRC[0]}:{SRC[1]}", *pro, str(full))
        ff("-i", str(full), "-vf", f"v360=input=e:output=eac:w={EAC[0]}:h={EAC[1]}:interp=lanc", *pro, str(eac))
        ff("-i", str(full), "-vf", f"scale={SRC[0] // 4}:{SRC[1] // 4}:flags=lanczos,v360=input=e:output=eac:w={LQ[0]}:h={LQ[1]}:interp=lanc",
           *pro, str(lqsrc))
    tiles = tile_ids()
    idmap = out / "tile-ids.png"
    img = np.zeros((EAC[1], EAC[0]), np.uint8)
    for i, (x, y) in enumerate(tiles):
        img[y:y + TILE, x:x + TILE] = 4 * (i + 1)
    Image.fromarray(img).save(idmap)
    cmdfile = out / "pan.cmd"
    pan_commands(cmdfile, secs)
    plans = {v: choose(idmap, v, secs) for v in VIEWERS}

    # Encodes.
    enc = {}
    for r in RATES:
        for k, src, args in (("h264-hw", full, vt("h264", r)), ("hevc-hw", full, vt("hevc", r)), ("av1-svt-rt", full, av1(r)),
                             ("eac-hevc", eac, vt("hevc", r))):
            f = out / f"{k}-{r}.mp4"
            if not f.exists():
                ff("-i", str(src), "-an", "-vf", "format=yuv420p", *args, str(f))
            enc[(k, r)] = f
        f = out / f"lq-{r}.mp4"
        if not f.exists():
            ff("-i", str(lqsrc), "-an", "-vf", "format=yuv420p", *vt("hevc", round(LQ_SHARE * r)), str(f))
    tile_rates = sorted({round(CORE_SHARE * r) for r in RATES} | {round(MARGIN_SHARE * r) for r in RATES})
    for tr in tile_rates:
        todo = [i for i in range(len(tiles)) if not (out / f"tile-{tr}-{i:02d}.mp4").exists()]
        for b in range(0, len(todo), 8):
            grp = todo[b:b + 8]
            graph = f"[0:v]format=yuv420p,split={len(grp)}" + "".join(f"[s{i}]" for i in grp) + ";" + ";".join(
                f"[s{i}]crop={TILE}:{TILE}:{tiles[i][0]}:{tiles[i][1]}[t{i}]" for i in grp)
            outs = sum((["-map", f"[t{i}]", *vt("hevc", tr), str(out / f"tile-{tr}-{i:02d}.mp4")] for i in grp), [])
            ff("-i", str(eac), "-filter_complex", graph, *outs)
        print("tiles", tr, "kbit/s done", flush=True)

    # Reference viewports.
    refs = {}
    for v in VIEWERS:
        f = out / f"ref-{v}.mkv"
        if not f.exists():
            ff("-i", str(full), "-vf", f"setpts=PTS-STARTPTS,format=yuv420p,{v360('e', v, cmdfile)}", "-c:v", "ffv1", str(f))
        refs[v] = f

    cache_f = out / "scores.json"
    cache = json.loads(cache_f.read_text()) if cache_f.exists() else {}

    def nu_inputs(r, v):
        cr, mr = round(CORE_SHARE * r), round(MARGIN_SHARE * r)
        chain, last, files = composite(1, plans[v], tiles, 0, "n")
        inputs = [out / f"lq-{r}.mp4"] + [out / f"tile-{cr if cls == 'core' else mr}-{i:02d}.mp4" for cls, i in files]
        return inputs, chain, last

    def job(k, r, v):
        key = f"{k}|{r}|{v}"
        if key in cache:
            return key, cache[key]
        log = out / f"vmaf-{k}-{r}-{v}.json"
        if k == "nu-360":
            inputs, chain, last = nu_inputs(r, v)
            res = score_viewport(inputs, chain, last, "eac", v, refs[v], cmdfile, log)
        else:
            res = score_viewport([enc[(k, r)]], ["[0:v]setpts=PTS-STARTPTS[x]"], "x", "eac" if k == "eac-hevc" else "e", v, refs[v], cmdfile, log)
        print(key, res, flush=True)
        return key, res

    with ThreadPoolExecutor(a.jobs) as pool:
        for key, res in pool.map(lambda t: job(*t), [(k, r, v) for k in ORDER for r in RATES for v in VIEWERS]):
            cache[key] = res
            cache_f.write_text(json.dumps(cache, indent=1))

    # Bits on the wire.
    def wire(r, k):
        if k != "nu-360":
            seg = segments(enc[(k, r)], secs)
            return {"wire_kbps": kb(max(seg)), "payload_kbps": round(sum(seg) * 8 / 1000 / secs, 1)}
        cr, mr = round(CORE_SHARE * r), round(MARGIN_SHARE * r)
        lq = segments(out / f"lq-{r}.mp4", secs)
        core = {i: segments(out / f"tile-{cr}-{i:02d}.mp4", secs) for i in range(len(tiles))}
        marg = {i: segments(out / f"tile-{mr}-{i:02d}.mp4", secs) for i in range(len(tiles))}
        core_pad = max(max(s) for s in core.values())
        marg_pad = max(max(s) for s in marg.values())
        # What a front viewer actually needs before padding, for reference.
        p = plans["front"]
        payload = sum(lq) + sum(core[i][q["segment"]] for q in p for i in q["core"]) + sum(marg[i][q["segment"]] for q in p for i in q["margin"])
        upload = sum(lq) + sum(sum(s) for s in core.values()) + sum(sum(s) for s in marg.values())
        return {"wire_kbps": kb(max(lq) + CORE * core_pad + MARGIN * marg_pad), "payload_kbps": round(payload * 8 / 1000 / secs, 1),
                "slot_kbps": {"sphere": kb(max(lq)), "core_tile": kb(core_pad), "margin_tile": kb(marg_pad)},
                "broadcaster_upload_kbps": round(upload * 8 / 1000 / secs, 1)}

    wsc_f = out / "ws-psnr.json"
    wsc = json.loads(wsc_f.read_text()) if wsc_f.exists() else {}
    for k in ORDER:
        for r in RATES:
            key = f"{k}|{r}"
            if key in wsc:
                continue
            if k in ("h264-hw", "hevc-hw", "av1-svt-rt"):
                wsc[key] = ws_psnr(["-i", str(enc[(k, r)])], "[0:v]setpts=PTS-STARTPTS[x]", full)
            elif k == "eac-hevc":
                wsc[key] = ws_psnr(["-i", str(enc[(k, r)])], f"[0:v]setpts=PTS-STARTPTS,v360=input=eac:output=e:w={SRC[0]}:h={SRC[1]}:interp=cube[x]", full)
            else:
                inputs, chain, last = nu_inputs(r, "front")
                wsc[key] = ws_psnr(sum((["-i", str(f)] for f in inputs), []),
                                   ";".join(chain + [f"[{last}]v360=input=eac:output=e:w={SRC[0]}:h={SRC[1]}:interp=cube[x]"]), full)
            print("ws-psnr", key, wsc[key], flush=True)
            wsc_f.write_text(json.dumps(wsc, indent=1))

    res = {"clip": a.clip, "source": c["source"], "url": c["url"], "sha256": c["sha256"], "start": c["start"], "seconds": secs,
           "size": f"{SRC[0]}x{SRC[1]}", "fps": FPS, "segment_s": SEG, "gop_frames": int(FPS * SEG),
           "viewport": {"size": f"{VP[0]}x{VP[1]}", "h_fov": VP[2], "v_fov": round(VP[3], 2), "vmaf_model": "vmaf_v0.6.1"},
           "nu360": {"projection": f"EAC {EAC[0]}x{EAC[1]}", "tile": TILE, "tiles": len(tiles), "core": CORE, "margin": MARGIN,
                     "sphere": f"EAC {LQ[0]}x{LQ[1]}", "shares": {"sphere": LQ_SHARE, "core_tile": round(CORE_SHARE, 4), "margin_tile": round(MARGIN_SHARE, 4)},
                     "lead_s": LEAD, "pan_deg_per_s": PAN_SPEED},
           "plans": {v: plans[v] for v in ("front", "up", "pan")},
           "encoder": "ffmpeg 7.1.1 on an Apple M1 Pro (macOS); VideoToolbox hardware HEVC and H.264, SVT-AV1",
           "methods": {}}
    for k in ORDER:
        pts = []
        for r in RATES:
            vs = {v: dict(zip(("vmaf", "psnr_y"), cache[f"{k}|{r}|{v}"])) for v in VIEWERS}
            fixed = [v for v in VIEWERS if v != "pan"]
            pts.append({"target_kbps": r, **wire(r, k),
                        "viewport_vmaf": round(sum(vs[v]["vmaf"] for v in VIEWERS) / len(VIEWERS), 2),
                        "viewport_vmaf_fixed": round(sum(vs[v]["vmaf"] for v in fixed) / len(fixed), 2),
                        "viewport_vmaf_pan": vs["pan"]["vmaf"],
                        "viewport_psnr_y": round(sum(vs[v]["psnr_y"] for v in VIEWERS) / len(VIEWERS), 2),
                        "ws_psnr": wsc[f"{k}|{r}"], "viewers": vs})
        res["methods"][k] = {"label": METHODS[k], "points": pts}
    hevc = res["methods"]["hevc-hw"]["points"]
    res["compare"] = {"bd_rate_vs_hevc_equirect_pct": {
        m: {q: bd_rate(res["methods"][m]["points"], hevc, q) for q in ("viewport_vmaf", "viewport_vmaf_fixed", "viewport_vmaf_pan", "ws_psnr")}
        for m in ORDER if m != "hevc-hw"},
        "vmaf_at_equal_wire_kbps": {str(r): {m: interp(res["methods"][m]["points"], "wire_kbps", "viewport_vmaf", r) for m in ORDER}
                                    for r in RATES}}
    (out / f"results-{a.clip}.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res["compare"], indent=2), flush=True)

    # Stills and clips for the site: front and pan viewports at the show rates, and the tiles a front viewer receives.
    tdir = root / "tiles" / a.clip
    tdir.mkdir(parents=True, exist_ok=True)
    x264 = ["-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an"]

    def still(mp4):
        ff("-ss", "4", "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(mp4.with_suffix(".jpg")))

    for v in ("front", "pan"):
        f = tdir / f"original-{v}.mp4"
        ff("-i", str(refs[v]), *x264, str(f))
        still(f)
        for r in SHOW:
            for k in ORDER:
                f = tdir / f"{r}-{k}-{v}.mp4"
                if k == "nu-360":
                    inputs, chain, last = nu_inputs(r, v)
                else:
                    inputs, chain, last = [enc[(k, r)]], ["[0:v]setpts=PTS-STARTPTS[x]"], "x"
                proj = "eac" if k in ("eac-hevc", "nu-360") else "e"
                ff(*sum((["-i", str(i)] for i in inputs), []), "-filter_complex",
                   ";".join(chain + [f"[{last}]format=yuv420p,{v360(proj, v, cmdfile)},format=yuv420p[o]"]), "-map", "[o]", *x264, str(f))
                still(f)
    # Tile map: the sphere a front viewer receives at the first show rate, core tiles outlined white, margin tiles grey.
    r = SHOW[0]
    inputs, chain, last = nu_inputs(r, "front")
    p = plans["front"][4]
    boxes = [f"drawbox=x={tiles[i][0]}:y={tiles[i][1]}:w={TILE}:h={TILE}:color=white@0.9:t=6" for i in p["core"]] + \
            [f"drawbox=x={tiles[i][0]}:y={tiles[i][1]}:w={TILE}:h={TILE}:color=gray@0.9:t=6" for i in p["margin"]]
    ff(*sum((["-i", str(i)] for i in inputs), []), "-filter_complex", ";".join(chain + [f"[{last}]trim=start=4,setpts=PTS-STARTPTS,{','.join(boxes)}[o]"]),
       "-map", "[o]", "-frames:v", "1", "-q:v", "2", str(tdir / f"tilemap-eac-{r}.jpg"))
    ff(*sum((["-i", str(i)] for i in inputs), []), "-filter_complex",
       ";".join(chain + [f"[{last}]trim=start=4,setpts=PTS-STARTPTS,{','.join(boxes)},v360=input=eac:output=e:w=1920:h=960:interp=cube[o]"]),
       "-map", "[o]", "-frames:v", "1", "-q:v", "2", str(tdir / f"tilemap-equirect-{r}.jpg"))
    ff("-ss", "4", "-i", str(full), "-vf", "scale=1920:960:flags=lanczos", "-frames:v", "1", "-q:v", "2", str(tdir / "original-equirect.jpg"))
    print("done", a.clip, flush=True)


if __name__ == "__main__":
    main()
