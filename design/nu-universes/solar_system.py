"""Build the nu.universes Solar System data from NASA/JPL: moons, spacecraft, small bodies, belts.

    python3 solar_system.py OUT_DIR

Writes, beside catalog.py's files:

  moons.json    {"epochs": [JD, ...], "moons": [[name, parent, diameter km, note, Horizons id], ...]}
  moons.bin     float32 osculating elements of each moon about its planet, every 10 days over the window:
                [moon][epoch] -> a (au), e, i, node, peri, M (deg), ecliptic J2000. The map propagates
                from the nearest epoch, so no moon is ever more than 5 days of two-body motion from JPL.
  craft.json    {"craft": [[name, note, first JD, count], ...], "step": 1} with positions in craft.bin
  craft.bin     float32 heliocentric ecliptic J2000 positions (au), one per day, per spacecraft
  bodies.json   {"made": JD, "bodies": [[name, kind, group, q au, e, i, node, peri, tp JD, note], ...]}
                named dwarf planets, asteroids and comets; every comet within 3 au of the Sun this year
                or next; asteroids passing within 0.05 au of Earth in the next 60 days; interstellar visitors.
                Elements use perihelion time so hyperbolic orbits work.
  belt.bin      float32 a, e, i, node, peri, M at belt_epoch, class (0 main belt, 1 Trojan, 2 Kuiper belt)

The window runs from 30 days before the build to 400 days after, so rebuild at least yearly.
Sources: JPL Horizons API, SBDB API, SBDB Query API, Close-Approach Data API (ssd.jpl.nasa.gov), public domain.
"""

import json
import struct
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

K = 0.985_607_668_6  # Gaussian mean motion, deg/day for a = 1 au
BELT_EPOCH = 2461200.5

MOONS = [
    ("Moon", "Earth", 301, 399, 3474.8, "Visited by 12 people, 1969–1972. Artemis is going back."),
    ("Phobos", "Mars", 401, 499, 22.5, "Spirals slowly inward; in about 50 million years it breaks up into a ring."),
    ("Deimos", "Mars", 402, 499, 12.4, "The smaller, outer moon of Mars."),
    ("Metis", "Jupiter", 516, 599, 43, "Innermost moon of Jupiter, inside its main ring."),
    ("Amalthea", "Jupiter", 505, 599, 167, "A red, potato-shaped inner moon; redder than anything else in the Solar System."),
    ("Thebe", "Jupiter", 514, 599, 98, "Inner moon whose dust feeds Jupiter's faint gossamer ring."),
    ("Io", "Jupiter", 501, 599, 3643, "The most volcanic world known."),
    ("Europa", "Jupiter", 502, 599, 3122, "An ocean under the ice. Europa Clipper arrives in 2030."),
    ("Ganymede", "Jupiter", 503, 599, 5268, "The largest moon in the Solar System, bigger than Mercury."),
    ("Callisto", "Jupiter", 504, 599, 4821, "The most cratered surface known."),
    ("Himalia", "Jupiter", 506, 599, 140, "The largest of Jupiter's distant, captured moons."),
    ("Pan", "Saturn", 618, 699, 28, "Walnut-shaped; it keeps the Encke Gap in Saturn's rings open."),
    ("Janus", "Saturn", 610, 699, 179, "Shares an orbit with Epimetheus; the two swap places every four years."),
    ("Epimetheus", "Saturn", 611, 699, 116, "Shares an orbit with Janus; the two swap places every four years."),
    ("Mimas", "Saturn", 601, 699, 396, "One giant crater, Herschel, makes it look like the Death Star."),
    ("Enceladus", "Saturn", 602, 699, 504, "Geysers of ocean water from its south pole feed Saturn's E ring."),
    ("Tethys", "Saturn", 603, 699, 1062, "Almost pure water ice."),
    ("Dione", "Saturn", 604, 699, 1123, "Bright ice cliffs on its trailing side."),
    ("Rhea", "Saturn", 605, 699, 1527, "Saturn's second-largest moon."),
    ("Titan", "Saturn", 606, 699, 5150, "Thick air and methane lakes. Huygens landed in 2005; Dragonfly follows."),
    ("Hyperion", "Saturn", 607, 699, 270, "Looks like a sponge and tumbles chaotically."),
    ("Iapetus", "Saturn", 608, 699, 1469, "One side as dark as coal, the other as bright as snow."),
    ("Phoebe", "Saturn", 609, 699, 213, "Orbits backwards: a captured body, source of Saturn's huge Phoebe ring."),
    ("Puck", "Uranus", 715, 799, 162, "The largest of Uranus's small inner moons, found by Voyager 2."),
    ("Miranda", "Uranus", 705, 799, 472, "Cliffs up to 20 km high."),
    ("Ariel", "Uranus", 701, 799, 1158, "The brightest of Uranus's moons."),
    ("Umbriel", "Uranus", 702, 799, 1169, "The darkest of Uranus's large moons."),
    ("Titania", "Uranus", 703, 799, 1577, "The largest moon of Uranus."),
    ("Oberon", "Uranus", 704, 799, 1523, "The outermost large moon of Uranus."),
    ("Proteus", "Neptune", 808, 899, 420, "About as big as a body can be without being pulled round by its own gravity."),
    ("Triton", "Neptune", 801, 899, 2707, "Orbits backwards: a captured Kuiper belt world, with nitrogen geysers."),
    ("Nereid", "Neptune", 802, 899, 357, "One of the most eccentric moon orbits known."),
    ("Charon", "Pluto", 901, 999, 1212, "Half Pluto's size; the two orbit a point between them."),
    ("Nix", "Pluto", 902, 999, 50, "A small moon that tumbles as Pluto and Charon pull on it."),
    ("Hydra", "Pluto", 903, 999, 51, "Pluto's outermost moon, coated in nearly pure water ice."),
]

CRAFT = [
    (-31, "Voyager 1", "Voyager 1", "Launched 1977. Left the heliosphere in 2012: the farthest object people have made."),
    (-32, "Voyager 2", "Voyager 2", "Launched 1977. The only spacecraft to visit Uranus and Neptune; in interstellar space since 2018."),
    (-23, "Pioneer 10", "Pioneer 10", "Launched 1972; silent since 2003, still coasting outward. Position predicted."),
    (-24, "Pioneer 11", "Pioneer 11", "Launched 1973; silent since 1995, still coasting outward. Position predicted."),
    (-98, "New Horizons", "New Horizons", "Flew past Pluto in 2015 and Arrokoth in 2019; now crossing the Kuiper belt."),
    (-96, "Parker Solar Probe", "Parker Solar Probe", "Flies through the Sun's corona; the fastest spacecraft ever, 191.7 km/s."),
    (-144, "Solar Orbiter", "Solar Orbiter", "ESA's Sun-watcher, tilting its orbit to see the Sun's poles."),
    (-170, "James Webb Space Telescope", "JWST", "Infrared telescope near Sun–Earth L2, 1.5 million km from Earth."),
    (-121, "BepiColombo", "BepiColombo", "ESA–JAXA mission to Mercury."),
    (-255, "Psyche", "Psyche", "On its way to the metal-rich asteroid Psyche; arrives 2029."),
    (-49, "Lucy", "Lucy", "Touring Jupiter's Trojan asteroids, 2027–2033."),
    (-159, "Europa Clipper", "Europa Clipper", "On its way to Jupiter's moon Europa; arrives 2030."),
    (-28, "JUICE", "JUICE", "ESA's Jupiter Icy Moons Explorer; arrives at Jupiter in 2031."),
    (-61, "Juno", "Juno", "Orbiting Jupiter since 2016."),
    (-64, "OSIRIS-APEX", "OSIRIS", "Heading for Apophis, to meet it after its close pass of Earth in April 2029."),
]

# (SBDB search string, display name, kind, group, note)
NAMED = [
    ("1", "Ceres", "Dwarf planet", "Asteroid belt", "The largest body in the asteroid belt. Visited by Dawn, 2015–2018."),
    ("4", "Vesta", "Asteroid", "Asteroid belt", "Second-largest in the belt. Visited by Dawn, 2011–2012."),
    ("2", "Pallas", "Asteroid", "Asteroid belt", "Third-largest in the belt, on a steeply tilted orbit."),
    ("10", "Hygiea", "Asteroid", "Asteroid belt", "Fourth-largest in the belt; nearly round."),
    ("3", "Juno", "Asteroid", "Asteroid belt", "One of the first four asteroids found, 1804."),
    ("16", "Psyche", "Asteroid", "Asteroid belt", "A metal-rich asteroid. NASA's Psyche arrives in 2029."),
    ("433", "Eros", "Asteroid", "Near-Earth asteroids", "First asteroid orbited and landed on, by NEAR Shoemaker, 2001."),
    ("101955", "Bennu", "Asteroid", "Near-Earth asteroids", "OSIRIS-REx brought its rocks to Earth in 2023."),
    ("162173", "Ryugu", "Asteroid", "Near-Earth asteroids", "Hayabusa2 brought samples home in 2020."),
    ("25143", "Itokawa", "Asteroid", "Near-Earth asteroids", "Hayabusa's target; first asteroid sample, 2010."),
    ("99942", "Apophis", "Asteroid", "Near-Earth asteroids", "Passes 32,000 km from Earth on 13 April 2029, inside the orbits of some satellites."),
    ("65803", "Didymos", "Asteroid", "Near-Earth asteroids", "DART struck its moon Dimorphos in 2022 and shortened its orbit."),
    ("624", "Hektor", "Trojan asteroid", "Asteroid belt", "The largest of Jupiter's Trojans, 60° ahead of Jupiter."),
    ("134340", "Pluto", "Dwarf planet", "Kuiper belt", "Visited by New Horizons in 2015."),
    ("136199", "Eris", "Dwarf planet", "Kuiper belt", "About as massive as Pluto; its discovery led to the definition of a planet."),
    ("136108", "Haumea", "Dwarf planet", "Kuiper belt", "Spins every four hours into an egg shape, and has a ring."),
    ("136472", "Makemake", "Dwarf planet", "Kuiper belt", "Bright, red, icy world beyond Pluto."),
    ("225088", "Gonggong", "Dwarf planet", "Kuiper belt", "One of the largest bodies beyond Neptune."),
    ("50000", "Quaoar", "Kuiper belt object", "Kuiper belt", "Has a ring far outside where rings should hold."),
    ("90482", "Orcus", "Kuiper belt object", "Kuiper belt", "Pluto's opposite: same orbit period, opposite side."),
    ("90377", "Sedna", "Detached object", "Kuiper belt", "Never comes closer than 76 au; one orbit takes about 11,000 years."),
    ("486958", "Arrokoth", "Kuiper belt object", "Kuiper belt", "The most distant world visited, by New Horizons in 2019."),
    ("1P", "Halley's Comet", "Comet", "Comets", "Returns every 76 years; next in 2061."),
    ("2P", "Comet Encke", "Comet", "Comets", "The shortest known period of a bright comet: 3.3 years."),
    ("9P", "Comet Tempel 1", "Comet", "Comets", "Deep Impact struck it in 2005."),
    ("19P", "Comet Borrelly", "Comet", "Comets", "Deep Space 1 flew past in 2001."),
    ("67P", "Comet 67P/Churyumov–Gerasimenko", "Comet", "Comets", "Rosetta orbited it and Philae landed, 2014–2016."),
    ("81P", "Comet Wild 2", "Comet", "Comets", "Stardust brought its dust to Earth in 2006."),
    ("103P", "Comet Hartley 2", "Comet", "Comets", "EPOXI flew past in 2010."),
    ("109P", "Comet Swift–Tuttle", "Comet", "Comets", "Parent of the Perseid meteors. Back in 2126."),
    ("55P", "Comet Tempel–Tuttle", "Comet", "Comets", "Parent of the Leonid meteors."),
    ("12P", "Comet Pons–Brooks", "Comet", "Comets", "The 'devil comet' of 2024. Back in 2095."),
    ("C/1995 O1", "Comet Hale–Bopp", "Comet", "Comets", "The great comet of 1997. Back in about 2,400 years."),
    ("1I", "1I/ʻOumuamua", "Interstellar object", "Interstellar visitors", "The first object known from another star system, found in 2017. Leaving, never to return."),
    ("2I", "2I/Borisov", "Interstellar comet", "Interstellar visitors", "The first interstellar comet, found in 2019."),
    ("3I", "3I/ATLAS", "Interstellar comet", "Interstellar visitors", "The third interstellar object, found on 1 July 2025; passing through once."),
]

BELT = [("MBA", 0, 10000), ("TJN", 1, 1500), ("TNO", 2, 2000)]


def get(url, tries=4):
    for k in range(tries):
        try:
            return urllib.request.urlopen(url, timeout=120).read().decode()
        except Exception as e:  # network hiccups and rate limits: back off and retry
            if k == tries - 1:
                raise
            print("retry", url[:90], e, file=sys.stderr)
            time.sleep(3 * (k + 1))


def horizons(params):
    base = {"format": "text", "OBJ_DATA": "NO", "MAKE_EPHEM": "YES", "REF_PLANE": "ECLIPTIC", "REF_SYSTEM": "J2000",
            "OUT_UNITS": "AU-D", "CSV_FORMAT": "YES"}
    base.update(params)
    q = "&".join(f"{k}='{v}'" if k not in ("format",) else f"{k}={v}" for k, v in base.items())
    text = get("https://ssd.jpl.nasa.gov/api/horizons.api?" + urllib.parse.quote(q, safe="=&'@"))
    name = next((l.split(":", 1)[1].strip() for l in text.splitlines() if l.startswith("Target body name")), "")
    if "$$SOE" not in text:
        return name, []
    rows = text.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines()
    return name, [[c.strip() for c in r.split(",")] for r in rows if r.strip()]


def jd_date(jd):
    return time.strftime("%Y-%m-%d", time.gmtime((jd - 2440587.5) * 86400))


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    now = round(time.time() / 86400 + 2440587.5 - 0.5) + 0.5
    start, end = now - 30, now + 400

    # Moons: elements about the planet every 10 days.
    epochs = [start + 10 * k for k in range(int((end - start) / 10) + 1)]
    meta, data = [], bytearray()
    for name, parent, mid, centre, diam, note in MOONS:
        target, rows = horizons({"COMMAND": str(mid), "EPHEM_TYPE": "ELEMENTS", "CENTER": f"500@{centre}",
                                 "START_TIME": f"JD{epochs[0]}", "STOP_TIME": f"JD{epochs[-1]}", "STEP_SIZE": "10d"})
        if len(rows) != len(epochs) or name.split()[0].lower() not in target.lower():
            print("skip moon", name, target, len(rows), file=sys.stderr)
            continue
        for r in rows:
            e, inc, node, peri, ma, a = (float(r[i]) for i in (2, 4, 5, 6, 9, 11))
            data += struct.pack("<6f", a, e, inc, node, peri, ma)
        meta.append([name, parent, diam, note, mid])
        print("moon", name, file=sys.stderr)
    (out / "moons.json").write_text(json.dumps({"epochs": epochs, "moons": meta}, ensure_ascii=False, separators=(",", ":")))
    (out / "moons.bin").write_bytes(bytes(data))

    # Spacecraft: daily heliocentric positions.
    craft, data = [], bytearray()
    for cid, name, expect, note in CRAFT:
        rows = []
        for a, b in ((start, end), (start, now + 30), (start, now)):
            target, rows = horizons({"COMMAND": str(cid), "EPHEM_TYPE": "VECTORS", "VEC_TABLE": "1", "CENTER": "500@10",
                                     "START_TIME": f"JD{a}", "STOP_TIME": f"JD{b}", "STEP_SIZE": "1d"})
            if rows and expect.lower() in target.lower():
                break
            rows = []
        if not rows:
            print("skip craft", name, file=sys.stderr)
            continue
        for r in rows:
            data += struct.pack("<3f", float(r[2]), float(r[3]), float(r[4]))
        craft.append([name, note, float(rows[0][0]), len(rows)])
        print("craft", name, len(rows), file=sys.stderr)
    (out / "craft.json").write_text(json.dumps({"step": 1, "craft": craft}, ensure_ascii=False, separators=(",", ":")))
    (out / "craft.bin").write_bytes(bytes(data))

    # Named bodies, active comets, Earth passers, interstellar visitors.
    bodies, seen = [], set()

    def sbdb(sstr):
        d = json.loads(get("https://ssd-api.jpl.nasa.gov/sbdb.api?full-prec=1&sstr=" + urllib.parse.quote(sstr)))
        if "orbit" not in d:
            return None, None
        el = {e["name"]: float(e["value"]) for e in d["orbit"]["elements"] if e["value"] is not None}
        if "tp" not in el:
            n = K / el["a"] ** 1.5
            el["tp"] = float(d["orbit"]["epoch"]) - el["ma"] / n
        return d["object"]["fullname"].strip(), el

    def add(name, kind, group, el, note):
        if name in seen:
            return
        seen.add(name)
        bodies.append([name, kind, group, el["q"], el["e"], el["i"], el["om"], el["w"], el["tp"], note])

    for sstr, name, kind, group, note in NAMED:
        _, el = sbdb(sstr)
        if el:
            add(name, kind, group, el, note)
            print("body", name, file=sys.stderr)

    q = urllib.parse.urlencode({"fields": "full_name,pdes,q,e,i,om,w,tp", "sb-kind": "c",
                                "sb-cdata": json.dumps({"AND": ["q|LT|3", f"tp|RG|{now - 365}|{now + 365}"]}), "limit": 80})
    for full, pdes, *v in json.loads(get("https://ssd-api.jpl.nasa.gov/sbdb_query.api?" + q))["data"]:
        try:
            qq, e, inc, om, w, tp = map(float, v)
        except (TypeError, ValueError):
            continue
        add(full.strip(), "Comet", "Comets", {"q": qq, "e": e, "i": inc, "om": om, "w": w, "tp": tp},
            f"Closest to the Sun on {jd_date(tp)}, {qq:.2f} au out.")
    print("comets", len(bodies), file=sys.stderr)

    cad = json.loads(get("https://ssd-api.jpl.nasa.gov/cad.api?date-min=now&date-max=%2B60&dist-max=0.05&sort=dist"))
    for des, _, _, cd, dist, *_rest in cad["data"][:30]:
        v_rel = float(_rest[2])
        full, el = sbdb(des)
        if el:
            ld = float(dist) * 149_597_870.7 / 384_400
            add(full or des, "Asteroid", "Passing Earth", el,
                f"Passes Earth on {cd[:11]} at {ld:.1f} times the Moon's distance, {v_rel:.1f} km/s.")
    print("bodies", len(bodies), file=sys.stderr)
    (out / "bodies.json").write_text(json.dumps({"made": now, "bodies": bodies}, ensure_ascii=False, separators=(",", ":")))

    # The belts: a real sample, all propagated to one epoch.
    data = bytearray()
    for cls, code, limit in BELT:
        rows = json.loads(get(f"https://ssd-api.jpl.nasa.gov/sbdb_query.api?fields=a,e,i,om,w,ma,epoch&sb-class={cls}&limit={limit}"))["data"]
        for row in rows:
            try:
                a, e, i, om, w, ma, epoch = map(float, row)
            except (TypeError, ValueError):
                continue
            if e >= 1:
                continue
            data += struct.pack("<7f", a, e, i, om, w, (ma + K / a ** 1.5 * (BELT_EPOCH - epoch)) % 360, code)
        print(cls, len(rows), file=sys.stderr)
    (out / "belt.bin").write_bytes(bytes(data))
    (out / "belt.json").write_text(json.dumps({"epoch": BELT_EPOCH}))


if __name__ == "__main__":
    main()
