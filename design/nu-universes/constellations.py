"""The 88 IAU constellations for nu.universes: names, where to look, and the stick figures.

Source: d3-celestial by Olaf Frohn (BSD-3-Clause), data/constellations.json and constellations.lines.json.
The figures are given as sky positions of their stars; the map snaps each vertex to the real catalogue star,
so the figures are drawn in 3D and only look like themselves from near the Sun.

Writes constellations.json: {"source", "rows": [[abbr, name, genitive, ra, dec, scale, [[ra, dec, ...], ...]]]}
with ra in degrees 0–360, into khensu-site sites/khensu-nu/public/universes/data and
khensu-apple Waves/Universes/Data.
"""

import json
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/ofrohn/d3-celestial/master/data/"
COPIES = [
    Path.home() / "Documents/GitHub/khensu/khensu-site/sites/khensu-nu/public/universes/data",
    Path.home() / "Documents/GitHub/khensu/khensu-apple/Waves/Universes/Data",
]


def get(name: str) -> dict:
    with urllib.request.urlopen(BASE + name, timeout=60) as r:
        return json.load(r)


def ra360(lon: float) -> float:
    return round(lon % 360, 4)


def main() -> None:
    names = get("constellations.json")["features"]
    lines = {f["id"]: f["geometry"]["coordinates"] for f in get("constellations.lines.json")["features"]}
    rows, seen = [], set()
    for f in names:
        p = f["properties"]
        # Serpens is one IAU constellation in two parts (Caput and Cauda); the source lists it twice under one id.
        if f["id"] in seen:
            continue
        seen.add(f["id"])
        name = "Serpens" if f["id"] == "Ser" else p["name"]
        ra, dec, scale = p["display"]
        figure = [[v for lon, lat in seg for v in (ra360(lon), round(lat, 4))] for seg in lines.get(f["id"], [])]
        rows.append([f["id"], name, p["gen"], ra360(ra), round(dec, 4), scale, figure])
    rows.sort(key=lambda r: r[1])
    text = json.dumps({"source": "d3-celestial, Olaf Frohn, BSD-3-Clause", "rows": rows}, separators=(",", ":"))
    for d in COPIES:
        if d.exists():
            (d / "constellations.json").write_text(text)
            print(f"wrote {d / 'constellations.json'}")
    print(f"{len(rows)} constellations, {sum(len(r[6]) for r in rows)} figure lines, {len(text) // 1024} KB")


if __name__ == "__main__":
    main()
