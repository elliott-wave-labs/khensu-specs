"""Build the nu.universes flight catalogue from public survey data.

    python3 catalog.py OUT_DIR [--src DIR]

Downloads (or reads from --src) three catalogues and writes compact little-endian float32
files. Every position is equatorial J2000 Cartesian in parsecs, Sun at the origin:
+x toward RA 0h Dec 0, +y toward RA 6h Dec 0, +z toward the north celestial pole.

  stars.bin     HYG v4.1 (Hipparcos, Yale Bright Star, Gliese; astronexus, CC BY-SA 4.0)
                x, y, z, absolute V magnitude, B-V colour index. Stars brighter than
                apparent magnitude 8, plus every star within 25 pc.
  stars.json    proper names: [[index into stars.bin, name], ...]
  local.json    Updated Nearby Galaxy Catalog (Karachentsev+ 2013, VizieR J/AJ/145/101):
                [name, x, y, z, diameter pc, inclination deg, absolute B mag, T-type].
                Distances are measured (TRGB, Cepheids, ...), not redshift.
  survey.bin    2MASS Redshift Survey (Huchra+ 2012, VizieR J/ApJS/199/26):
                x, y, z, absolute Ks magnitude. Distance = cz / H0 with H0 = 70 km/s/Mpc,
                so peculiar velocities smear the nearest few Mpc; local.json covers those.
"""

import json
import math
import struct
import sys
import urllib.request
from pathlib import Path

HYG = "https://raw.githubusercontent.com/astronexus/HYG-Database/main/hyg/CURRENT/hygdata_v41.csv"
VIZ = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-out.max=unlimited&-source="
UNGC = VIZ + "J/AJ/145/101/catalog&-out=Name,RAJ2000,DEJ2000,Dist,A26,i,BMag,TT"
TWOMRS = VIZ + "J/ApJS/199/26/table3&-out=RAJ2000,DEJ2000,cz,Ktmag"
H0 = 70.0
C_KMS = 299_792.458


def fetch(url, cache):
    if cache.exists():
        return cache.read_text()
    text = urllib.request.urlopen(url, timeout=120).read().decode()
    cache.write_text(text)
    return text


def xyz(ra_deg, dec_deg, d):
    ra, dec = math.radians(ra_deg), math.radians(dec_deg)
    return d * math.cos(dec) * math.cos(ra), d * math.cos(dec) * math.sin(ra), d * math.sin(dec)


def hms(s):
    h, m, sec = (float(p) for p in s.split())
    return 15 * (h + m / 60 + sec / 3600)


def dms(s):
    sign = -1 if s.strip().startswith("-") else 1
    d, m, sec = (abs(float(p)) for p in s.split())
    return sign * (d + m / 60 + sec / 3600)


def tsv_rows(text):
    rows = [r for r in text.splitlines() if r and not r.startswith("#")]
    return [r.split("\t") for r in rows[3:]]  # header, units, dashes


def stars(text, out):
    import csv
    data, names = bytearray(), []
    for row in csv.DictReader(text.splitlines()):
        if row["id"] == "0":
            continue  # the Sun is drawn separately
        dist, mag = float(row["dist"]), float(row["mag"])
        if dist >= 100_000 or not (mag <= 8.0 or dist <= 25):
            continue
        ci = float(row["ci"]) if row["ci"] else 0.65
        data += struct.pack("<5f", float(row["x"]), float(row["y"]), float(row["z"]), float(row["absmag"]), ci)
        if row["proper"]:
            names.append([len(data) // 20 - 1, row["proper"]])
    (out / "stars.bin").write_bytes(data)
    (out / "stars.json").write_text(json.dumps(names, separators=(",", ":")))
    return len(data) // 20


def local(text, out):
    rows = []
    for r in tsv_rows(text):
        name, ra, dec, dist, a26, inc, bmag, tt = (c.strip() for c in r[:8])
        if not dist:
            continue
        d = float(dist) * 1e6
        x, y, z = xyz(hms(ra), dms(dec), d)
        rows.append([name, round(x, 1), round(y, 1), round(z, 1),
                     round(float(a26) * 1000) if a26 else 0, int(inc) if inc else 0,
                     float(bmag) if bmag else -14.0, int(tt) if tt else 10])
    (out / "local.json").write_text(json.dumps(rows, separators=(",", ":")))
    return len(rows)


def survey(text, out):
    data = bytearray()
    for r in tsv_rows(text):
        try:
            ra, dec, cz, k = float(r[0]), float(r[1]), float(r[2]), float(r[3])
        except (ValueError, IndexError):
            continue
        if cz < 500:
            continue
        d = cz / H0 * 1e6
        x, y, z = xyz(ra, dec, d)
        data += struct.pack("<4f", x, y, z, k - 5 * math.log10(d / 10))
    (out / "survey.bin").write_bytes(data)
    return len(data) // 16


def main():
    out = Path(sys.argv[1])
    src = Path(sys.argv[sys.argv.index("--src") + 1]) if "--src" in sys.argv else out / ".src"
    out.mkdir(parents=True, exist_ok=True)
    src.mkdir(parents=True, exist_ok=True)
    print("stars", stars(fetch(HYG, src / "hyg.csv"), out))
    print("local galaxies", local(fetch(UNGC, src / "ungc.tsv"), out))
    print("survey galaxies", survey(fetch(TWOMRS, src / "2mrs.tsv"), out))


if __name__ == "__main__":
    main()
