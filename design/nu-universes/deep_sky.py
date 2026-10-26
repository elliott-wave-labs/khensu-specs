"""Build the nu.universes deep-sky data: nebulae, clusters, star systems, pulsars, black holes, quasars, and M33.

    python3 deep_sky.py OUT_DIR

Writes, beside catalog.py's files:

  objects.json  [[name, kind, group, ra deg, dec deg, distance pc, size pc, motion, note], ...]
                A curated list. Coordinates come from SIMBAD (CDS) by identifier, so they are exact. Distances
                and sizes are the commonly cited published values. Quasar distances are comoving distances for
                flat ΛCDM, H0 = 67.7 km/s/Mpc, Ωm = 0.31 (Planck 2018). `motion` says how the map animates it:
                {"orbit": {...}} a companion on its published or circular orbit; {"pulse": {...}} a variable
                star's period and range; {"spin": seconds} a pulsar; {"flicker": days} a quasar.
  pulsars.bin   every pulsar in the ATNF Pulsar Catalogue with a distance: float32 ra, dec (deg), distance (pc),
                spin period (s), binary period (days, 0 if single). Manchester et al. 2005, AJ 129, 1993.
  m33.json      the Triangulum Galaxy's catalogued contents, as sky positions the map places onto its disc:
                cepheids  [ra, dec, period d, V, V amplitude]   Pellerin & Macri 2011 (J/ApJS/193/26)
                clusters  [ra, dec, V, log age, log mass]        Sarajedini & Mancone 2007 (J/AJ/134/447)
                hii       [ra, dec, radius pc]                   Relaño et al. 2013 (J/A+A/552/A140)
                snr       [ra, dec, diameter pc]                 Long et al. 2010 (J/ApJS/187/495)
  m33-stars.bin the brightest resolved stars, float32 ra, dec, V, B−V: Massey et al. 2006 Local Group Galaxy
                Survey (J/AJ/131/2478), V < 20.5 within 0.6° of the centre.
"""

import json
import math
import struct
import sys
import urllib.parse
import urllib.request
from pathlib import Path

VIZ = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv?-out.max=unlimited&-source="
M33 = "01 33 50.9 +30 39 36"
C_KMS = 299_792.458


def get(url):
    return urllib.request.urlopen(url, timeout=180).read().decode()


def comoving_pc(z, h0=67.7, om=0.31):
    n, s = 20000, 0.0
    for k in range(n):
        zz = (k + 0.5) * z / n
        s += 1 / math.sqrt(om * (1 + zz) ** 3 + (1 - om))
    return C_KMS / h0 * s * z / n * 1e6


def orbit(period_days, a_au, e=0.0, i=None, node=0.0, peri=0.0, tp=2451545.0, q=1.0, colour=None):
    """A companion's orbit. i, node and peri are on the sky (deg) when published; i=None means unknown,
    drawn edge-on for eclipsing pairs and 60° otherwise. q is the companion's share of the motion."""
    return {"orbit": {"P": period_days, "a": a_au, "e": e, "i": i, "node": node, "peri": peri, "tp": tp, "q": q, "colour": colour}}


def year_jd(y):
    return 2451545.0 + (y - 2000.0) * 365.25


# (SIMBAD id, name, kind, group, distance pc, size pc, motion, note)
OBJECTS = [
    ("M 42", "Orion Nebula", "Emission nebula", "Nebulae", 412, 7.4, None, "The nearest big star nursery, 1,344 light-years away; visible to the naked eye in Orion's sword."),
    ("M 8", "Lagoon Nebula", "Emission nebula", "Nebulae", 1250, 33, None, "A giant star nursery in Sagittarius, wider than the full Moon in our sky."),
    ("M 16", "Eagle Nebula", "Emission nebula", "Nebulae", 1740, 21, None, "Home of the Pillars of Creation, columns of gas light-years tall."),
    ("NGC 3372", "Carina Nebula", "Emission nebula", "Nebulae", 2300, 140, None, "One of the biggest star-forming regions in our galaxy, home of Eta Carinae."),
    ("NGC 2237", "Rosette Nebula", "Emission nebula", "Nebulae", 1600, 40, None, "A rose of glowing hydrogen around the young cluster NGC 2244."),
    ("NGC 7000", "North America Nebula", "Emission nebula", "Nebulae", 795, 30, None, "Shaped like the continent, in Cygnus."),
    ("NGC 2070", "Tarantula Nebula", "Emission nebula", "Nebulae", 49_590, 200, None, "The most active star nursery in the Local Group, in the Large Magellanic Cloud."),
    ("M 57", "Ring Nebula", "Planetary nebula", "Nebulae", 787, 0.4, None, "The shell a dying Sun-like star threw off; Webb imaged it in 2023."),
    ("NGC 7293", "Helix Nebula", "Planetary nebula", "Nebulae", 200, 0.8, None, "One of the nearest planetary nebulae: 'the Eye of God'."),
    ("NGC 6543", "Cat's Eye Nebula", "Planetary nebula", "Nebulae", 1000, 0.2, None, "Nested shells thrown off every 1,500 years or so."),
    ("M 27", "Dumbbell Nebula", "Planetary nebula", "Nebulae", 417, 0.44, None, "The first planetary nebula found, by Charles Messier in 1764."),
    ("M 1", "Crab Nebula", "Supernova remnant", "Nebulae", 2000, 3.4, None, "What is left of a star seen exploding in 1054, with a pulsar at its heart."),
    ("NAME Cassiopeia A", "Cassiopeia A", "Supernova remnant", "Nebulae", 3400, 3, None, "The youngest known remnant in our galaxy: its light reached Earth around 1680."),
    ("NAME Cygnus Loop", "Veil Nebula", "Supernova remnant", "Nebulae", 735, 34, None, "Filaments of a star that exploded 10,000 to 20,000 years ago."),
    ("SN 1987A", "SN 1987A", "Supernova remnant", "Nebulae", 51_400, 0.4, None, "The nearest supernova seen since 1604, in February 1987, in the Large Magellanic Cloud."),
    ("NAME Vela SNR", "Vela Supernova Remnant", "Supernova remnant", "Nebulae", 290, 40, None, "One of the nearest remnants; the Vela Pulsar spins at its centre."),
    ("M 45", "Pleiades", "Open cluster", "Star clusters", 136, 4, None, "The Seven Sisters: about 1,000 young stars in a veil of dust."),
    ("Cl Melotte 25", "Hyades", "Open cluster", "Star clusters", 47, 6, None, "The nearest open cluster: the V of Taurus."),
    ("NGC 5139", "Omega Centauri", "Globular cluster", "Star clusters", 5430, 46, None, "Our galaxy's biggest globular cluster, about 10 million stars, with a middle-weight black hole found in 2024."),
    ("M 13", "Hercules Cluster", "Globular cluster", "Star clusters", 6800, 44, None, "Target of the 1974 Arecibo message."),
    ("NGC 104", "47 Tucanae", "Globular cluster", "Star clusters", 4450, 37, None, "The second-brightest globular cluster, rich in millisecond pulsars."),
    ("alf CMa", "Sirius B", "White dwarf · binary", "Star systems", 2.64, 0, orbit(50.128 * 365.25, 19.8, 0.5923, 136.336, 44.578, 147.27, year_jd(1994.5715), 2.063 / 3.081, [0.8, 0.88, 1]),
     "A white dwarf the size of Earth orbiting Sirius every 50.1 years. Orbit: Bond et al. 2017."),
    ("alf Cen A", "Alpha Centauri B", "Star · binary", "Star systems", 1.34, 0, orbit(79.91 * 365.25, 23.5, 0.5208, 79.32, 205.06, 232.3, year_jd(1955.56), 1.1 / 2.0, [1, 0.8, 0.55]),
     "Alpha Centauri A and B orbit each other every 79.9 years. Orbit: Kervella et al. 2016."),
    ("bet Per", "Algol", "Eclipsing binary", "Star systems", 28.5, 0, {**orbit(2.867, 0.062, colour=[1, 0.75, 0.5]), "pulse": {"P": 2.867, "shape": "eclipse", "range": [2.1, 3.4]}},
     "The Demon Star: dims for 10 hours every 2.87 days as its dimmer partner passes in front."),
    ("alf Vir", "Spica", "Binary", "Star systems", 77, 0, orbit(4.0145, 0.12, colour=[0.7, 0.8, 1]), "Two hot blue stars so close they pull each other into eggs; one orbit every 4 days."),
    ("bet Lyr", "Beta Lyrae", "Eclipsing binary", "Star systems", 294, 0, {**orbit(12.94, 0.28, colour=[0.75, 0.85, 1]), "pulse": {"P": 12.94, "shape": "eclipse", "range": [3.3, 4.4]}},
     "A pair so close that gas streams from one star to the other."),
    ("alf Gem", "Castor", "Multiple star", "Star systems", 15.6, 0, None, "Six stars in three pairs that orbit each other."),
    ("zet UMa", "Mizar and Alcor", "Multiple star", "Star systems", 25, 0, None, "Six stars: the famous eye test in the handle of the Big Dipper."),
    ("eta Car", "Eta Carinae", "Binary · luminous blue variable", "Star systems", 2300, 0, orbit(5.54 * 365.25, 15.4, 0.9, colour=[1, 0.85, 0.7]),
     "A giant pair, the larger star about 100 Suns; it erupted in the 1840s and briefly became the second-brightest star in the sky."),
    ("del Cep", "Delta Cephei", "Cepheid variable", "Star systems", 272, 0, {"pulse": {"P": 5.366, "shape": "cepheid", "range": [3.48, 4.37]}},
     "The star that named the Cepheids, whose period gives their true brightness: the first rung of the cosmic distance ladder."),
    ("omi Cet", "Mira", "Long-period variable", "Star systems", 92, 0, {"pulse": {"P": 332, "shape": "mira", "range": [2.0, 10.1]}}, "The 'wonderful' star: brightens up to a thousandfold over 11 months."),
    ("RR Lyr", "RR Lyrae", "Pulsating variable", "Star systems", 262, 0, {"pulse": {"P": 0.5669, "shape": "cepheid", "range": [7.06, 8.12]}}, "Prototype of the old pulsating stars used to measure distances to globular clusters."),
    ("PSR B0531+21", "Crab Pulsar", "Pulsar", "Pulsars and magnetars", 2000, 0, {"spin": 0.0334}, "A neutron star born in 1054, spinning 30 times a second."),
    ("PSR B0833-45", "Vela Pulsar", "Pulsar", "Pulsars and magnetars", 287, 0, {"spin": 0.0893}, "Spins 11 times a second; known for sudden spin-ups called glitches."),
    ("PSR B1919+21", "PSR B1919+21", "Pulsar", "Pulsars and magnetars", 1000, 0, {"spin": 1.3373}, "The first pulsar, found by Jocelyn Bell Burnell in 1967. Its pulses are the cover of Joy Division's Unknown Pleasures."),
    ("PSR J0437-4715", "PSR J0437−4715", "Millisecond pulsar", "Pulsars and magnetars", 156.3, 0, {"spin": 0.005757}, "The nearest millisecond pulsar: a neutron star spinning 174 times a second."),
    ("PSR B1913+16", "Hulse–Taylor Pulsar", "Binary pulsar", "Pulsars and magnetars", 4167, 0, {"spin": 0.05903, **orbit(0.323, 0.013, 0.617, colour=[0.8, 0.9, 1])},
     "Two neutron stars; their orbit shrinks exactly as gravitational waves predict (Nobel Prize 1993)."),
    ("PSR J0737-3039A", "Double Pulsar", "Binary pulsar", "Pulsars and magnetars", 735, 0, {"spin": 0.022699, **orbit(0.1023, 0.0059, 0.088, colour=[0.8, 0.9, 1])},
     "The only known pair of pulsars, orbiting every 2.45 hours."),
    ("PSR J0633+1746", "Geminga", "Pulsar", "Pulsars and magnetars", 250, 0, {"spin": 0.2371}, "A nearby pulsar seen in gamma rays but almost silent in radio."),
    ("PSR J1748-2446ad", "PSR J1748−2446ad", "Millisecond pulsar", "Pulsars and magnetars", 5900, 0, {"spin": 0.001396}, "The fastest-spinning known pulsar: 716 turns a second, in the cluster Terzan 5."),
    ("SGR 1806-20", "SGR 1806−20", "Magnetar", "Pulsars and magnetars", 8700, 0, {"spin": 7.55}, "A magnetar: in December 2004 its giant flare briefly ionised Earth's upper atmosphere."),
    ("Cyg X-1", "Cygnus X-1", "Black hole binary", "Black holes", 2220, 0, orbit(5.6, 0.2, colour=[0.7, 0.8, 1]), "A 21-Sun black hole feeding on a blue supergiant: the first black hole widely accepted, 1972."),
    ("Gaia DR3 4373465352415301632", "Gaia BH1", "Black hole binary", "Black holes", 480, 0, orbit(185.6, 1.4, 0.45, colour=[1, 0.95, 0.85]), "The nearest known black hole, found in 2022 from the wobble of its Sun-like companion."),
    ("V404 Cyg", "V404 Cygni", "Black hole binary", "Black holes", 2390, 0, orbit(6.47, 0.15, colour=[1, 0.8, 0.6]), "A black hole that flares every few decades, last in 2015."),
    ("M 87", "M87*", "Supermassive black hole", "Black holes", 16_400_000, 0, None, "The first black hole ever imaged (Event Horizon Telescope, 2019): 6.5 billion Suns, with a jet 5,000 light-years long."),
    ("3C 273", "3C 273", "Quasar", "Quasars", None, 0, {"flicker": 100, "z": 0.158}, "The first quasar identified, 1963: a black hole feeding so fast it outshines its galaxy."),
    ("TON 618", "TON 618", "Quasar", "Quasars", None, 0, {"flicker": 300, "z": 2.219}, "One of the most massive black holes known, about 40 billion Suns."),
    ("QSO B0957+561", "Twin Quasar", "Lensed quasar", "Quasars", None, 0, {"flicker": 200, "z": 1.413}, "The first gravitational lens found, 1979: one quasar seen twice through a galaxy."),
    ("3C 48", "3C 48", "Quasar", "Quasars", None, 0, {"flicker": 150, "z": 0.367}, "The first quasar found, though its distance was worked out second."),
]


def simbad(ids):
    """Resolve identifiers through CDS Sesame, SIMBAD first."""
    found = {}
    for x in ids:
        text = get("https://cds.unistra.fr/cgi-bin/nph-sesame/-oI/S?" + urllib.parse.quote(x))
        for line in text.splitlines():
            if line.startswith("%J "):
                ra, dec = line.split()[1:3]
                found[x] = (float(ra), float(dec))
                break
    return found


def hms(s):
    h, m, x = (float(v) for v in s.split())
    return 15 * (h + m / 60 + x / 3600)


def dms(s):
    sign = -1 if s.strip().startswith("-") else 1
    d, m, x = (abs(float(v)) for v in s.split())
    return sign * (d + m / 60 + x / 3600)


def tsv(source, cols, extra=""):
    text = get(VIZ + source + "&-out=" + ",".join(cols) + extra)
    rows = []
    for line in text.splitlines():
        if not line or line.startswith("#") or line.startswith("-") or line.split("\t")[0] in cols:
            continue
        parts = line.split("\t")
        if len(parts) >= len(cols) and not parts[0].strip().startswith(("deg", '"h')):
            rows.append([p.strip() for p in parts[: len(cols)]])
    return rows


def num(v):
    try:
        return float(v)
    except ValueError:
        return None


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    pos = simbad([o[0] for o in OBJECTS])
    objects = []
    for sid, name, kind, group, dist, size, motion, note in OBJECTS:
        if sid not in pos:
            print("SIMBAD has no", sid, file=sys.stderr)
            continue
        ra, dec = pos[sid]
        if dist is None:
            dist = comoving_pc(motion["z"])
            note = f"{note} Redshift {motion['z']}: its light left {lookback_gyr(motion['z']):.1f} billion years ago."
        objects.append([name, kind, group, round(ra, 6), round(dec, 6), round(dist, 3), size, motion, note])
    (out / "objects.json").write_text(json.dumps(objects, ensure_ascii=False, separators=(",", ":")))
    print("objects", len(objects), file=sys.stderr)

    atnf = get("https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=2.6.1&JName=JName&RaJD=RaJD&DecJD=DecJD&P0=P0&PB=PB&Dist=Dist"
               "&startUserDefined=true&c1_val=&c2_val=&c3_val=&c4_val=&sort_attr=jname&sort_order=asc&condition=&pulsar_names=&ephemeris=short"
               "&coords_unit=raj%2Fdecj&radius=&coords_1=&coords_2=&style=Short+without+errors&no_value=*&fsize=3&x_axis=&x_scale=linear"
               "&y_axis=&y_scale=linear&state=query&table_bottom.x=40&table_bottom.y=20")
    data, n = bytearray(), 0
    for line in atnf.split("<pre>")[1].split("</pre>")[0].splitlines():
        parts = line.split()
        if len(parts) < 7 or not parts[0].isdigit():
            continue
        ra, dec, p0, pb, d = (num(x) for x in parts[2:7])
        if None in (ra, dec, p0, d) or d <= 0:
            continue
        data += struct.pack("<5f", ra, dec, d * 1000, p0, pb or 0)
        n += 1
    (out / "pulsars.bin").write_bytes(bytes(data))
    print("pulsars", n, file=sys.stderr)

    cone = "&-c=" + urllib.parse.quote(M33) + "&-c.rd=0.6"
    m33 = {"cepheids": [], "clusters": [], "hii": [], "snr": []}
    seen = set()
    for r in tsv("J/ApJS/193/26", ["RAJ2000", "DEJ2000", "Per", "Vmag", "Vamp"]):
        v = [num(x) for x in r]
        key = (round(v[0] or 0, 4), round(v[1] or 0, 4))
        if None not in v[:3] and key not in seen:
            seen.add(key)
            m33["cepheids"].append([round(v[0], 5), round(v[1], 5), v[2], v[3] or 22, v[4] or 0.3])
    for r in tsv("J/AJ/134/447", ["RAJ2000", "DEJ2000", "Vmag", "logAge", "logMass", "Class"]):
        if r[5] != "Cluster":
            continue
        m33["clusters"].append([round(hms(r[0]), 5), round(dms(r[1]), 5), num(r[2]), num(r[3]), num(r[4])])
    for r in tsv("J/A+A/552/A140", ["RAJ2000", "DEJ2000", "r"]):
        m33["hii"].append([round(hms(r[0]), 5), round(dms(r[1]), 5), num(r[2]) or 50])
    for r in tsv("J/ApJS/187/495", ["RAJ2000", "DEJ2000", "Diam"]):
        m33["snr"].append([round(hms(r[0]), 5), round(dms(r[1]), 5), num(r[2]) or 30])
    (out / "m33.json").write_text(json.dumps(m33, separators=(",", ":")))
    print({k: len(v) for k, v in m33.items()}, file=sys.stderr)

    data, n = bytearray(), 0
    for r in tsv("J/AJ/131/2478", ["RAJ2000", "DEJ2000", "Vmag", "B-V"], cone + "&Vmag=%3C20.5"):
        v, bv = num(r[2]), num(r[3])
        if v is None:
            continue
        data += struct.pack("<4f", hms(r[0]), dms(r[1]), v, bv if bv is not None else 0.3)
        n += 1
    (out / "m33-stars.bin").write_bytes(bytes(data))
    print("m33 stars", n, file=sys.stderr)


def lookback_gyr(z, h0=67.7, om=0.31):
    n, s = 20000, 0.0
    for k in range(n):
        zz = (k + 0.5) * z / n
        s += 1 / ((1 + zz) * math.sqrt(om * (1 + zz) ** 3 + (1 - om)))
    return 977.8 / h0 * s * z / n


if __name__ == "__main__":
    main()
