# nueu — nu.e.u

**Status: web v1, 25 October 2026.** A chart cast in the browser. Shown as **nu.e.u** in headings, buttons, labels and the footer. Header nav: **e.u**. Code, files and the storage key stay `nueu`. Running text uses **nueu**.

The mark is the esoteric 9: the enneagram, point 9 at the top, the triangle 9–3–6 and the hexad 1–4–2–8–5–7.

| Item | Value |
| --- | --- |
| Shown | nu.e.u |
| Running text | nueu |
| Code | `nueu` |
| Host | `nueu.khensu.nu` (`nu:nueu.khensu.nu`) |
| Also opens it | `u.khensu.nu`, `neue.khensu.nu`, `new.khensu.nu`, `nu.khensu.nu` — 301 to the host above, once each name resolves and the own cert is active |
| Apex | `https://khensu.nu/nueu`, and `/u`, `/neue`, `/new`, `/nu` on the apex |
| App | Web first. A native app is a later build. No bundle id yet |
| Short name nu.u | Stays with nu.universes. The host `u.khensu.nu` belongs to nueu |

Related: `design/nu-waves-player.md` (the spacetime bubble), `design/nu-universes.md` (drag to turn, scrub time), `design/nu-glass.md` (the light).

---

## 1. What it is

nueu is a personal chart in the sense of [Co–Star](https://www.costarastrology.com/) and [The Pattern](https://www.thepattern.com/), with the working instruments of [Time Nomad](https://timenomad.app/):

- Natal chart
- Transits for now, and for any moment
- Synastry between two charts kept on the device
- Secondary progressions (a day after birth for a year of life)
- Solar return, the Sun back on its natal tropical degree
- Planetary hours from sunrise and sunset at the birth place
- nu.natal, the tab after the hours: the birth chart written out, each point, house and aspect, and what it means
- Fifteen fixed stars, a conjunction within 1.5°
- Opens on nu.skies: the thirteen constellations the ecliptic crosses, Ophiuchus included, each at the real IAU width
- Twelve-sign chart still available: tropical, or sidereal Lahiri (Spica at 180°)
- Whole sign, equal, or Placidus houses

The reading is composed from the chart: sign, the tightest transit, the phase of the Moon, void of course when the Moon perfects no further major aspect before it changes sign. It is a language for the sky. It is not a diagnosis.

Birth data stays in `localStorage` under `nueu.v1`. Nothing is posted. A city is matched against a list shipped in the page. Latitude and longitude can be typed. “Use this device’s place” uses the browser’s geolocation and keeps the result. With nothing saved, the chart opens on nube: 20 April 1969, 8:08 in the evening, Toronto. A chart already saved in the browser stays. A saved zodiac is kept only after it was chosen. Otherwise the chart opens on nu.skies.

## 2. The picture

- **Light motes** in the stage, the same quiet dust as the memory page: a few dozen points, additive, in the aura colours.
- **The wheel**, ascendant at the left. It opens on nu.skies: thirteen unequal constellations, with the Ophiuchus symbol between Scorpius and Sagittarius. The twelve equal signs are the other setting. House cusps stay twelve, at their longitudes. A second chart sits on the outer ring for transits and bonds. Rest, click or tap a body, an aspect line, a house number or a sign. A second point reads the relation between them. The tight aspects pulse. A selected point pulses faster. The same readings are written out on nu.natal, the last tab, after the planetary hours.
- **The sample**, `#nube-compare`. nube, 20 April 1969, 8:08 in the evening, Toronto, whole sign, drawn four times from the same cast: twelve tropical signs at rest, that wheel with the tight aspects pulsing, then nu.skies the same way. Ophiuchus is on the nu.skies ring at its real width. The link preview is that comparison: `/og/nueu.jpg` is the still, `/og/nueu.mp4` is the landscape H.264, `/og/nueu-square.mp4` is the square HEVC.
- **The sky**, a spacetime bubble. The ecliptic is a ring. Bodies are lights on it. Drag to turn, arrow keys to turn, a moment control to move the sky the way nu.universes moves time.

The relay network still sits behind the hero, like every other page.

## 3. The calculation

Geocentric ecliptic longitude of date comes from `astronomy-engine` 2.1.19 (Sun, Moon, Mercury through Pluto). The mean lunar node is Meeus. The Part of Fortune is ascendant + Moon − Sun by day, the reverse by night. Day is the Sun in houses 7–12.

Ascendant and midheaven use Greenwich apparent sidereal time, the birth longitude, and the mean obliquity of date. Placidus intermediate cusps iterate the semi-arc (one third and two thirds, day and night). Above 66° latitude, or if that division fails, the houses fall back to whole sign and the page says so.

Checked against a known library for 4 August 1961, 19:24, Honolulu (21.3069° N, 157.8583° W), as 5 August 1961 05:24 UTC: Sun 132.548°, ascendant 318.05°, midheaven 238.89°, Placidus cusps within about 0.02° of that library. This is not JPL DE-430. It is the theory in the page, and it is enough for a sign, a degree, and an aspect.

Lahiri here is the tropical longitude of Spica, precessed from J2000, minus 180°. Fixed-star longitudes use the same precession in longitude. That is accurate to a few arcminutes over the decades the chart is for, not to a star catalogue of record.

nu.skies does not divide the ecliptic by 30°, and it does not invent a thirteenth equal sign. The ring is the thirteen IAU constellations the ecliptic actually crosses. The boundary longitudes are David Asher’s intersections of those boundaries with the J2000 ecliptic, precessed to the chart date with the same longitude precession as the stars. Ophiuchus sits between Scorpius and Sagittarius. Scorpius is the short one, about 6.6°. The symbol on the wheel is ⛎. Houses stay a twelve-fold division. The chart opens on nu.skies. The twelve-sign natal chart remains the other setting. A section on the page, `#thirteen-section`, treats thirteen as a number for life: thirteen moons in a year of the Sun, the Fibonacci step, and the power left outside the twelve-month Mesopotamian grid.

Aspects: conjunction and opposition 8°, square and trine 6°, sextile 4°, plus 2° when the Sun or Moon is involved.

Planetary hours follow the Chaldean order from the weekday of sunrise. The twelve day hours split sunrise to sunset. The twelve night hours split sunset to the next sunrise.

## 4. Hosts

Do not put these names on the shared products certificate.

The header, the footer and the canonical are `https://nueu.khensu.nu`. The apex `https://khensu.nu/nueu` still opens the same page. It is not the nav href.

`nueu.khensu.nu`, `u.khensu.nu`, `neue.khensu.nu`, `new.khensu.nu` and `nu.khensu.nu` each need `dig A` → `34.107.228.246` before a certificate is created. One own cert can cover all five. `nueu.khensu.nu` serves the page. The other four 301 to it. A missing A record is a Hover record. It is not a reason to point the nav at `https://khensu.nu/nueu`.

The project SSL certificate quota was 100 on 25 October 2026, with 10 in use. A new cert still waits on DNS. An unanswered name must not be attached to the proxy.

## 5. Patent

The math is classical. The page is a defensive publication. See `PATENTS.md`. The page does not say patent pending.
