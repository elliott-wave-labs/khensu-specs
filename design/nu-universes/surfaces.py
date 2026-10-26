"""Surface maps and named features for the close-up view in nu.universes.

Maps (equirectangular, east longitude increasing to the right, longitude 0 in the middle):
  Solar System Scope (INOVE), CC BY 4.0, made from NASA data: the Sun, the planets, the Moon, Saturn's rings.
  USGS Astrogeology, public domain: Io, Europa, Ganymede, Callisto (Voyager and Galileo global mosaics).
  NASA/JPL via Wikimedia Commons, public domain: Mercury is from Solar System Scope; Titan, Enceladus, Tethys,
  Dione, Rhea, Iapetus (Cassini), Triton (Voyager 2), Pluto and Charon (New Horizons), Ceres and Vesta (Dawn).
Features: the IAU Gazetteer of Planetary Nomenclature (USGS, public domain), largest named features per body,
  with the origin of each name.

Writes, into khensu-site sites/khensu-nu/public/universes/surfaces:
  <slug>.webp     4096 x 2048 (or the source's size if smaller), for the close-up view
  <slug>-1k.webp  1024 x 512, for the globe drawn in the map
  surfaces.json   {"bodies": {name: {map, maps: {layer: file}, credit, features: [[name, lat, lon, km, type, origin]]}}}
and the 1k maps with surfaces.json into khensu-apple Waves/Universes/Surfaces.

Needs ImageMagick (magick) and cwebp. Downloads are cached in ~/Library/Caches/nu-universes-surfaces.
"""

import io
import json
import struct
import subprocess
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

UA = "nu.universes-data/1.0 (https://khensu.nu; e@khensu.nu)"
CACHE = Path.home() / "Library/Caches/nu-universes-surfaces"
SITE = Path.home() / "Documents/GitHub/khensu/khensu-site/sites/khensu-nu/public/universes/surfaces"
APP = Path.home() / "Documents/GitHub/khensu/khensu-apple/Waves/Universes/Surfaces"

SSS = "https://www.solarsystemscope.com/textures/download/"
USGS = "https://planetarymaps.usgs.gov/mosaic/"
SSS_CREDIT = "Map: Solar System Scope (INOVE), CC BY 4.0, from NASA data."
COMMONS_CREDIT = "Map: NASA/JPL, public domain (Wikimedia Commons)."
USGS_CREDIT = "Map: USGS Astrogeology, NASA Voyager and Galileo, public domain."

# name: (layers {layer: source}, credit, IAU nomenclature target or None)
# A source is ("sss", file), ("usgs", file) or ("commons", file).
BODIES = {
    "Sun": ({"surface": ("sss", "8k_sun.jpg")}, SSS_CREDIT, None),
    "Mercury": ({"surface": ("sss", "8k_mercury.jpg")}, SSS_CREDIT, "MERCURY"),
    "Venus": ({"surface": ("sss", "4k_venus_atmosphere.jpg"), "radar": ("sss", "8k_venus_surface.jpg")}, SSS_CREDIT, "VENUS"),
    "Earth": ({"surface": ("sss", "8k_earth_daymap.jpg"), "night": ("sss", "8k_earth_nightmap.jpg"), "clouds": ("sss", "8k_earth_clouds.jpg")}, SSS_CREDIT, None),
    "Moon": ({"surface": ("sss", "8k_moon.jpg")}, SSS_CREDIT, "MOON"),
    "Mars": ({"surface": ("sss", "8k_mars.jpg")}, SSS_CREDIT, "MARS"),
    "Jupiter": ({"surface": ("sss", "8k_jupiter.jpg")}, SSS_CREDIT, None),
    "Saturn": ({"surface": ("sss", "8k_saturn.jpg"), "rings": ("sss", "8k_saturn_ring_alpha.png")}, SSS_CREDIT, None),
    "Uranus": ({"surface": ("sss", "2k_uranus.jpg")}, SSS_CREDIT, None),
    "Neptune": ({"surface": ("sss", "2k_neptune.jpg")}, SSS_CREDIT, None),
    "Io": ({"surface": ("usgs", "Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_1km.tif")}, USGS_CREDIT, "IO"),
    "Europa": ({"surface": ("usgs", "Europa_Voyager_GalileoSSI_global_mosaic_500m.tif")}, USGS_CREDIT, "EUROPA"),
    "Ganymede": ({"surface": ("usgs", "Ganymede_Voyager_GalileoSSI_global_mosaic_1km.tif")}, USGS_CREDIT, "GANYMEDE"),
    "Callisto": ({"surface": ("usgs", "Callisto_Voyager_GalileoSSI_global_mosaic_1km.tif")}, USGS_CREDIT, "CALLISTO"),
    "Titan": ({"surface": ("commons", "Titan map April 2011 full.png")}, COMMONS_CREDIT, "TITAN"),
    "Enceladus": ({"surface": ("commons", "Enceladus Color Map.jpg")}, COMMONS_CREDIT, "ENCELADUS"),
    "Tethys": ({"surface": ("commons", "Tethys map June 2008 PIA08416 moon only.jpg")}, COMMONS_CREDIT, "TETHYS"),
    "Dione": ({"surface": ("commons", "Dione Color Map.jpg")}, COMMONS_CREDIT, "DIONE"),
    "Rhea": ({"surface": ("commons", "PIA12561 Rhea Map.jpg")}, COMMONS_CREDIT, "RHEA"),
    "Iapetus": ({"surface": ("commons", "Iapetus Color Map.jpg")}, COMMONS_CREDIT, "IAPETUS"),
    "Triton": ({"surface": ("commons", "Triton Map.jpg")}, COMMONS_CREDIT, "TRITON"),
    "Pluto": ({"surface": ("commons", "Pluto color mapmosaic.jpg")}, COMMONS_CREDIT, "PLUTO"),
    "Charon": ({"surface": ("commons", "Cpmap cyl PS717 HR 180.jpg")}, COMMONS_CREDIT, "CHARON"),
    "Ceres": ({"surface": ("commons", "PIA20354-Ceres-DwarfPlanet-MercatorMap-HAMO-20160322-0DegreeLongitude.jpg")}, COMMONS_CREDIT, "CERES"),
    "Vesta": ({"surface": ("commons", "Vesta map for GeoHack.png")}, COMMONS_CREDIT, "VESTA"),
}
# East longitude at the middle of each map, where it is not 0. Checked against IAU features: Xanadu and Menrva on
# Titan, Iapetus's dark leading side, Dione's wispy trailing side, Tirawa on Rhea, Belton Regio and Sputnik Planitia
# on Pluto; Vesta's map states its left edge is 330°. Tethys (2008), Triton, Charon, Ceres (Occator) and the USGS
# and Solar System Scope maps are centred on 0°.
CENTER = {"Titan": 180, "Enceladus": 180, "Dione": 180, "Rhea": 180, "Iapetus": 180, "Pluto": 180, "Vesta": 150}
# Enhanced-colour maps of nearly grey worlds, shown in grey: Dawn's Ceres map also fills its poles in false colour.
GRAY = {"Ceres"}
FEATURES = 48
MOON_FEATURES = 70
# Small but famous: always named, whatever their size. Landing sites (Statio) on the Moon are kept as well.
FAMOUS = {
    "MOON": {"Tycho", "Copernicus", "Kepler", "Aristarchus", "Plato", "Clavius", "Grimaldi", "Shackleton", "Tsiolkovskiy", "Apollo", "Von Kármán"},
    "MARS": {"Olympus Mons", "Valles Marineris", "Gale", "Jezero", "Arsia Mons", "Pavonis Mons", "Ascraeus Mons", "Elysium Mons", "Hellas Planitia", "Gusev", "Meridiani Planum"},
    "MERCURY": {"Caloris Planitia", "Rachmaninoff", "Beethoven"},
    "IO": {"Pele", "Loki Patera", "Prometheus", "Tvashtar Paterae"},
    "EUROPA": {"Pwyll", "Conamara Chaos", "Thera Macula", "Thrace Macula"},
    "GANYMEDE": {"Tros", "Osiris", "Galileo Regio"},
    "CALLISTO": {"Valhalla", "Asgard"},
    "TITAN": {"Kraken Mare", "Ligeia Mare", "Punga Mare", "Ontario Lacus", "Selk", "Menrva", "Xanadu"},
    "ENCELADUS": {"Baghdad Sulcus", "Damascus Sulcus", "Cairo Sulcus", "Alexandria Sulcus", "Camphor Sulcus"},
    "PLUTO": {"Sputnik Planitia", "Wright Mons", "Piccard Mons", "Tombaugh Regio"},
    "CERES": {"Occator", "Ahuna Mons", "Kerwan", "Urvara", "Yalode"},
    "VESTA": {"Rheasilvia", "Veneneia", "Marcia"},
    "IAPETUS": {"Cassini Regio", "Turgis", "Engelier"},
    "TETHYS": {"Odysseus", "Ithaca Chasma", "Penelope"},
    "RHEA": {"Tirawa", "Inktomi"},
    "DIONE": {"Evander", "Aeneas", "Creusa"},
}


def fetch(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  downloading {url}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=600) as r, open(dest.with_suffix(".part"), "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    dest.with_suffix(".part").rename(dest)
    return dest


def commons_url(name: str) -> str:
    q = urllib.parse.urlencode({"action": "query", "titles": "File:" + name, "prop": "imageinfo", "iiprop": "url", "format": "json"})
    req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q, headers={"User-Agent": UA})
    pages = json.load(urllib.request.urlopen(req, timeout=60))["query"]["pages"]
    return next(iter(pages.values()))["imageinfo"][0]["url"]


def source(kind: str, name: str) -> Path:
    url = SSS + name if kind == "sss" else USGS + name if kind == "usgs" else commons_url(name)
    return fetch(url, CACHE / kind / name.replace(" ", "_"))


def webp(src: Path, out: Path, width: int, alpha: bool = False, gray: bool = False) -> None:
    """Resize to width x width/2 (rings keep their own height) and encode as WebP."""
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".png")
    size = f"{width}x{max(16, width // 16)}!" if alpha else f"{width}x{width // 2}!"
    tone = ["-modulate", "100,0"] if gray else []
    subprocess.run(["magick", "-limit", "memory", "2GiB", f"{src}[0]", "-resize", size, *([] if alpha else ["-alpha", "off"]), *tone, "-colorspace", "sRGB", tmp], check=True)
    subprocess.run(["cwebp", "-quiet", *(["-lossless"] if alpha else ["-q", "82"]), "-m", "6", str(tmp), "-o", str(out)], check=True)
    tmp.unlink()


def source_width(src: Path) -> int:
    w = subprocess.run(["magick", "identify", "-format", "%w", f"{src}[0]"], capture_output=True, text=True, check=True).stdout
    return int(w.strip() or 0)


def dbf_rows(data: bytes) -> list[dict]:
    n, hl, rl = struct.unpack("<xxxxIHH", data[:12])
    fields = []
    for i in range(32, hl - 1, 32):
        fields.append((data[i:i + 11].split(b"\0")[0].decode(), data[i + 16]))
    rows = []
    for r in range(n):
        rec = data[hl + r * rl: hl + (r + 1) * rl]
        if rec[:1] == b"*":
            continue
        p, row = 1, {}
        for name, ln in fields:
            row[name] = rec[p:p + ln].decode("utf-8", "replace").strip()
            p += ln
        rows.append(row)
    return rows


def features(target: str, count: int) -> list[list]:
    z = fetch(f"https://asc-planetarynames-data.s3.us-west-2.amazonaws.com/{target}_nomenclature_center_pts.zip", CACHE / "iau" / f"{target}.zip")
    with zipfile.ZipFile(z) as zf:
        dbf = next(n for n in zf.namelist() if n.endswith(".dbf"))
        rows = dbf_rows(zf.read(dbf))
    rows = [r for r in rows if r.get("approval", "").startswith("Adopted") and r.get("diameter")]
    num = lambda r, k: float(r[k] or 0)
    rows.sort(key=lambda r: -num(r, "diameter"))
    # Long features are listed once per segment: keep the largest of each name.
    seen = set()
    rows = [r for r in rows if not (r["name"] in seen or seen.add(r["name"]))]
    famous = FAMOUS.get(target, set())
    keep = rows[:count]
    keep += [r for r in rows[count:] if r.get("code") == "ST" or r["name"] in famous]
    missing = famous - {r["name"] for r in keep}
    if missing:
        print(f"  not in the gazetteer as adopted: {', '.join(sorted(missing))}")
    out = []
    for r in keep:
        lon = num(r, "center_lon")
        lon = lon - 360 if lon > 180 else lon
        origin = (r.get("origin") or "").strip()
        if len(origin) > 240:
            origin = origin[:237].rsplit(" ", 1)[0] + "…"
        out.append([r["name"], round(num(r, "center_lat"), 3), round(lon, 3), round(num(r, "diameter")), r.get("type", "").split(",")[0], origin])
    return out


def main() -> None:
    import sys
    only = set(sys.argv[1:])  # re-encode just these bodies' maps; every body's entry is still written
    meta = {"source": "nu.universes surfaces.py", "bodies": {}}
    for name, (layers, credit, target) in BODIES.items():
        print(name, flush=True)
        slug = name.lower()
        files = {}
        for layer, (kind, file) in layers.items():
            base = slug if layer == "surface" else f"{slug}-{layer}"
            files[layer] = base
            if only and name not in only and (SITE / f"{base}-1k.webp").exists():
                continue
            src = source(kind, file)
            rings = layer == "rings"
            width = 2048 if rings else min(4096, max(1024, source_width(src) // 1024 * 1024))
            webp(src, SITE / f"{base}.webp", width, alpha=rings, gray=name in GRAY)
            webp(src, SITE / f"{base}-1k.webp", 1024, alpha=rings, gray=name in GRAY)
        feats = features(target, MOON_FEATURES if name == "Moon" else FEATURES) if target else []
        meta["bodies"][name] = {"maps": files, "credit": credit + (" Names: IAU Gazetteer of Planetary Nomenclature." if feats else ""), "features": feats}
        if name in CENTER:
            meta["bodies"][name]["center"] = CENTER[name]
    text = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
    (SITE / "surfaces.json").write_text(text)
    if APP.parent.exists():
        APP.mkdir(exist_ok=True)
        (APP / "surfaces.json").write_text(text)
        for f in SITE.glob("*-1k.webp"):
            (APP / f.name).write_bytes(f.read_bytes())
    total = sum(f.stat().st_size for f in SITE.glob("*.webp"))
    print(f"{len(meta['bodies'])} bodies, {sum(len(b['features']) for b in meta['bodies'].values())} named features, {total / 1e6:.1f} MB of maps")


if __name__ == "__main__":
    main()
