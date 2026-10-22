"""Build the nu.universes small-body catalogue from the NASA/JPL Small-Body Database.

    python3 small_bodies.py OUT_DIR

Writes two files beside catalog.py's:

  bodies.json   named dwarf planets, asteroids and comets, full-precision osculating elements:
                {"epoch": JD, "bodies": [[name, kind, a au, e, i, node, peri, M at epoch (deg), note], ...]}
  belt.bin      a real sample of the main belt, Jupiter's Trojans and the Kuiper belt, float32:
                a au, e, i, node, peri, M at the common epoch (deg), class (0 belt, 1 Trojan, 2 Kuiper belt).

Angles are ecliptic J2000 degrees. Elements are propagated to one epoch with two-body mean motion,
so positions drift slowly from the true ones; fine for a map, not for navigation.
Source: NASA/JPL SBDB API and SBDB Query API (ssd-api.jpl.nasa.gov), public domain.
"""

import json
import struct
import sys
import urllib.parse
import urllib.request
from pathlib import Path

EPOCH = 2461200.5  # 2026-Jun-10, the epoch JPL currently publishes for numbered asteroids
K = 0.985_607_668_6  # Gaussian mean motion, deg/day for a = 1 au

# (SBDB search string, display name, kind, note)
NAMED = [
    ("1", "Ceres", "Dwarf planet · asteroid belt", "The largest body in the asteroid belt. Visited by Dawn, 2015–2018."),
    ("4", "Vesta", "Asteroid", "Second-largest in the belt. Visited by Dawn, 2011–2012."),
    ("2", "Pallas", "Asteroid", "Third-largest in the belt, on a steeply tilted orbit."),
    ("10", "Hygiea", "Asteroid", "Fourth-largest in the belt; nearly round."),
    ("3", "Juno", "Asteroid", "One of the first four asteroids found, 1804."),
    ("16", "Psyche", "Asteroid", "A metal-rich asteroid. NASA's Psyche arrives in 2029."),
    ("433", "Eros", "Asteroid · near-Earth", "First asteroid orbited and landed on, by NEAR Shoemaker, 2001."),
    ("101955", "Bennu", "Asteroid · near-Earth", "OSIRIS-REx brought its rocks to Earth in 2023."),
    ("162173", "Ryugu", "Asteroid · near-Earth", "Hayabusa2 brought samples home in 2020."),
    ("25143", "Itokawa", "Asteroid · near-Earth", "Hayabusa's target; first asteroid sample, 2010."),
    ("99942", "Apophis", "Asteroid · near-Earth", "Passes 32,000 km from Earth on 13 April 2029, inside the orbits of some satellites."),
    ("65803", "Didymos", "Asteroid · near-Earth", "DART struck its moon Dimorphos in 2022 and shortened its orbit."),
    ("134340", "Pluto", "Dwarf planet · Kuiper belt", "Visited by New Horizons in 2015."),
    ("136199", "Eris", "Dwarf planet · scattered disc", "About as massive as Pluto; its discovery led to the definition of a planet."),
    ("136108", "Haumea", "Dwarf planet · Kuiper belt", "Spins every four hours into an egg shape, and has a ring."),
    ("136472", "Makemake", "Dwarf planet · Kuiper belt", "Bright, red, icy world beyond Pluto."),
    ("225088", "Gonggong", "Dwarf planet · scattered disc", "One of the largest bodies beyond Neptune."),
    ("50000", "Quaoar", "Kuiper belt object", "Has a ring far outside where rings should hold."),
    ("90482", "Orcus", "Kuiper belt object", "Pluto's opposite: same orbit period, opposite side."),
    ("90377", "Sedna", "Detached object", "Never comes closer than 76 au; one orbit takes about 11,000 years."),
    ("486958", "Arrokoth", "Kuiper belt object", "The most distant world visited, by New Horizons in 2019."),
    ("1P", "Halley's Comet", "Comet", "Returns every 76 years; next in 2061."),
    ("2P", "Comet Encke", "Comet", "The shortest known period of a bright comet: 3.3 years."),
    ("9P", "Comet Tempel 1", "Comet", "Deep Impact struck it in 2005."),
    ("19P", "Comet Borrelly", "Comet", "Deep Space 1 flew past in 2001."),
    ("67P", "Comet 67P/Churyumov–Gerasimenko", "Comet", "Rosetta orbited it and Philae landed, 2014–2016."),
    ("81P", "Comet Wild 2", "Comet", "Stardust brought its dust to Earth in 2006."),
    ("103P", "Comet Hartley 2", "Comet", "EPOXI flew past in 2010."),
    ("109P", "Comet Swift–Tuttle", "Comet", "Parent of the Perseid meteors. Back in 2126."),
    ("55P", "Comet Tempel–Tuttle", "Comet", "Parent of the Leonid meteors."),
    ("12P", "Comet Pons–Brooks", "Comet", "The 'devil comet' of 2024. Back in 2095."),
    ("C/1995 O1", "Comet Hale–Bopp", "Comet", "The great comet of 1997. Back in about 2,400 years."),
]

CLASSES = [("MBA", 0, 4000), ("TJN", 1, 800), ("TNO", 2, 1500)]


def get(url):
    return json.loads(urllib.request.urlopen(url, timeout=120).read().decode())


def at_epoch(a, ma, epoch):
    return (ma + K / a ** 1.5 * (EPOCH - epoch)) % 360


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    bodies = []
    for sstr, name, kind, note in NAMED:
        d = get("https://ssd-api.jpl.nasa.gov/sbdb.api?full-prec=1&sstr=" + urllib.parse.quote(sstr))
        el = {e["name"]: float(e["value"]) for e in d["orbit"]["elements"] if e["value"] is not None}
        epoch = float(d["orbit"]["epoch"])
        if el["e"] >= 1:
            continue
        a = el["a"]
        bodies.append([name, kind, a, el["e"], el["i"], el["om"], el["w"], round(at_epoch(a, el["ma"], epoch), 6), note])
        print(name, a, file=sys.stderr)
    (out / "bodies.json").write_text(json.dumps({"epoch": EPOCH, "bodies": bodies}, ensure_ascii=False, separators=(",", ":")))

    data = bytearray()
    for cls, code, limit in CLASSES:
        q = get(f"https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=a,e,i,om,w,ma,epoch&sb-class={cls}&limit={limit}")
        n = 0
        for row in q["data"]:
            try:
                a, e, i, om, w, ma, epoch = map(float, row)
            except (TypeError, ValueError):
                continue
            if e >= 1:
                continue
            data += struct.pack("<7f", a, e, i, om, w, at_epoch(a, ma, epoch), code)
            n += 1
        print(cls, n, file=sys.stderr)
    (out / "belt.bin").write_bytes(bytes(data))


if __name__ == "__main__":
    main()
