# nu.universes — nu.u: Google Earth for galaxies and the whole universe

**Status: built v1, 18 October 2026.** Part of nu.waves (`nu.khensu.waves`, waves.khensu.nu). Short name **nu.u**. This document is the design, the physics model, the data model and the shipped v1 scope. Where a figure is measured it says so; where it is a design target or an estimate it says so. Nothing here is held for a patent filing — it is published as it is built (see §13).

Related: `design/nu-waves-player.md`, `design/nu-audio.md`, `design/nu-spatial.md`, `design/nu-3d.md`, `design/nu-glass.md`, `PROTOCOL.md` 12.6 (archive), `WEBE.md` 7.1 (link previews are media).

| Item | Value |
| --- | --- |
| Shown | nu.universes in headings, buttons and labels; **nu.u** as the short name; part of ñü.ŵævẽš |
| Running text | `nu.universes`, `nu.u`, `nu.waves` (ASCII, per `AGENTS.md`) |
| Code | `nu.universes`, `Universes/` in the Waves target, `nu-u` in file names |
| Host | `iverse.khensu.nu` (header i.verse; `nu:iverse.khensu.nu`) with `universes.khensu.nu`, `rabbithole.khensu.nu` and `portal.khensu.nu` opening the same page. `inverse.khensu.nu` 301s to iverse (the easy autocorrect typo). One own cert `moqom-aura-iverse-khensu-nu-2` shared with aura (never the shared products pack). Apex `https://khensu.nu/universes` also opens it |
| App | Inside `nu.khensu.waves` (iPhone, iPad, Mac, iOS/iPadOS/macOS 26). No new bundle ID, no new App Store app. Native RealityKit + AR; the web page is the catalogue and the fallback viewer |
| Licence | Specs CC BY 4.0 (`khensu-specs`); app AGPL-3.0 (`khensu-apple`); core Apache-2.0 if a decoder lands in `khensu-core` |

---

## 1. What it is

nu.u is Google Earth / Google Maps for the sky, at every scale, in every wavelength, across all of time:

- **Scales.** Your room in AR → the night sky over your house → the Solar System → the Milky Way → the Local Group → **the Triangulum Galaxy (M33)** as the first fully mapped galaxy → the observable universe → the whole universe since the Big Bang, and forward to where real physics predicts it goes.
- **Time.** A single timeline from \(t = 0\) (13.8 Gyr ago) to \(t = +10\) Gyr from now. You scrub it. The universe expands, the cosmic microwave background (CMB) cools and redshifts, galaxies form, merge and fade — computed from cosmology, not keyframed by an artist.
- **Wavelength.** Music is only the audible band. nu.u renders the full electromagnetic spectrum plus the channels humans do not have: gamma ray, X-ray, ultraviolet, visible, infrared, microwave, radio, **and** the mantis-shrimp hyperspectral + polarisation mode (§6). A wavelength slider is the same gesture as tuning a radio or pitching a sound in nu.waves — that is why nu.universes lives inside nu.waves.
- **Real data, real physics.** Every star is a catalogue star with a measured position, distance, temperature and variability class. Stars do not twinkle because a shader says `sin(t)`; they vary because their physics varies (§5). The M33 background is the real Hubble mosaic, served as map tiles, refreshed from NASA and ESA archives (§4).
- **Graphics past Night Sky.** Night Sky, Stellarium Mobile and Sky Guide render a flat star chart beautifully. nu.u renders a *place*: volumetric nebulae as Gaussian splats, a 40-billion-star galaxy you can fly through, HDR spectral colour, 120 Hz ProMotion, and AR that locks the galaxy to your table or the real sky (§7–§8).

Non-goals for v1: no server-side rendering, no Siri / Private Cloud Compute / cloud model (fixed decision in `AGENTS.md`), no social feed inside nu.u, no invented stars. If a pixel is not catalogue data, a physics model, or a labelled artistic reconstruction, it is not drawn.

---

## 2. The model

### 2.1 One scene graph, seven scale layers

A single RealityKit scene holds seven nested layers. Crossing a boundary cross-fades LODs; there is never a loading screen between Earth and M33.

| Layer | Extent | Contents | Source |
| --- | --- | --- | --- |
| L0 Room (AR) | 0.1–10 m | Tabletop galaxy, sky dome locked to your walls | RealityKit AR world tracking |
| L1 Sky | 1 AU view | Night sky from your location and time, planets, Milky Way band | Gaia + Hipparcos, VSX variables, JPL ephemeris (on-device) |
| L2 Solar System | 100 AU | Sun, planets, major moons, spacecraft | JPL Horizons-class ephemeris, bundled + refreshed |
| L3 Milky Way | 200 kly | Gaia stars (subsampled on device), globulars, nebulae, Galactic centre | Gaia DR, Harris globular catalogue |
| L4 Local Group | 10 Mly | Milky Way, Andromeda (M31), **Triangulum (M33)**, dwarfs | NED / Local Group catalogues |
| L5 M33 Deep Map | 60 kly across | The Google-Maps layer for M33: Hubble tiles, 25 M resolved stars, NGC 604, star clusters, H II regions | ESA/Hubble PHATTER, PHAT-class surveys (§3–§4) |
| L6 Universe | 93 Gly (observable) | Galaxy surveys, CMB sphere, large-scale structure, cosmic timeline | Planck CMB, SDSS/DESI-class catalogues (subsampled), FLRW model (§2.3) |

Coordinates: everything is stored in **galactocentric Cartesian, parsecs, double precision on disk, float32 relative-to-camera on the GPU** (RealityKit entities are re-based to the camera every frame — the standard floating-origin fix, so 2.7 Mly and 0.1 m both work).

### 2.2 Time model — since the Big Bang, and forward

\[
a(t):\quad H^2(a) = H_0^2\left(\Omega_r a^{-4} + \Omega_m a^{-3} + \Omega_k a^{-2} + \Omega_\Lambda\right)
\]

with Planck-class parameters (\(H_0 \approx 67.4\ \mathrm{km\,s^{-1}\,Mpc^{-1}}\), \(\Omega_m \approx 0.315\), \(\Omega_\Lambda \approx 0.685\); pinned values ship in `UniverseModels.swift` and are versioned). The timeline integrates \(a(t)\) on device (RK4, cached table) and derives:

- **CMB temperature** \(T = T_0(1+z)\), \(T_0 = 2.725\ \mathrm{K}\): at recombination (\(z \approx 1100\), \(t \approx 380{,}000\) yr) the L6 shell glows orange at ~3,000 K and cools to today's invisible 2.7 K microwaves. You *watch* it redshift as you scrub forward.
- **Lookback is literal.** When you look at M33 you see it as it was 2.73 Myr ago, because its light left 2.73 Myr ago. nu.u labels every object with *emitted* time and *observed* time and never pretends "realtime" means instantaneous (§4.3).
- **Future is prediction, labelled as prediction.** Proper motions (Gaia), radial velocities and N-body-lite integration carry stars and galaxies forward: M33's approach, the Andromeda–Milky Way encounter in ~4 Gyr, M33's uncertain fate (§3). Predicted frames carry a `predicted` flag in the data model and a different timeline tint in the UI. Physics in, prediction out — never presented as observation.

Epochs on the slider: Big Bang → recombination (380 kyr) → first stars (~200 Myr) → reionisation (~1 Gyr) → peak star formation (~10 Gyr ago) → today → +4 Gyr (Milkomeda encounter) → +10 Gyr.

### 2.3 Rendering model — a spectral cube, not an RGB texture

Every renderable body carries a **19-channel spectral signature** (§6), not an RGB colour. The renderer projects the cube to the display through the selected observer (human, mantis, instrument band, sonification). This is the one architectural decision everything else follows from: change the observer and the same data re-renders in gamma rays or in mantis colours without re-downloading anything.

Per frame, per star (Metal compute, instanced point sprites in RealityKit via a custom `SurfaceShader`):

1. Fetch catalogue record (position, \(T_\text{eff}\), radius, variability, spectrum class).
2. Evaluate the spectral cube for the current cosmic time (blackbody + emission/absorption features per band, redshifted by \(1+z\)).
3. Apply variability physics (§5) to get instantaneous flux per channel.
4. Project cube → display RGB (or → audio, §6.4) through the observer matrix.
5. Size/soften the sprite by distance, magnitude and the selected band's PSF; add diffraction spikes only for saturated stars, from the band PSF, never as decoration.

Nebulae and galaxy discs are **Gaussian splats** (`.nu` splat tracks, `design/nu-3d.md` 3.8) whose splat colours are likewise spectral means per channel, plus a Hubble-tile underlay at L5 so the flown-through galaxy and the photographed galaxy are the same galaxy.

---

## 3. M33 — the Triangulum Galaxy, the first deep map

M33 is the hero and the default background because it is close, face-on, star-forming, and the best-photographed galaxy beyond our own. The facts below are the v1 catalogue constants; each is cited and each ships in `M33Catalog.swift`.

| Fact | Value | Source |
| --- | --- | --- |
| Distance | ~2.73 million light-years (NASA: "about 3 million") | [EarthSky](https://earthsky.org/clusters-nebulae-galaxies/triangulum-galaxy-m33-a-binocular-challenge/), [ESA/Hubble heic1901](https://esahubble.org/news/heic1901/), [NASA M33](https://science.nasa.gov/mission/hubble/science/explore-the-night-sky/hubble-messier-catalog/messier-33/) |
| Diameter | ~60,000 light-years (~60% of the Milky Way; NASA: "half the size") | ESA/Hubble heic1901; [ESO](https://www.eso.org/public/belgium-de/images/b13/?lang) (50–60 kly) |
| Stars | ~40 billion | ESA/Hubble heic1901, EarthSky |
| Rank | 3rd-largest in the Local Group, after Andromeda and the Milky Way; 2nd-closest large spiral | ESA/Hubble heic1901, EarthSky |
| Apparent magnitude | 5.7 — among the most distant objects visible to the unaided eye under dark skies | NASA M33, ESO |
| Hubble mosaic | 665 million pixels; 54 separate Advanced Camera for Surveys pointings; resolves 10–15 M individual stars in frame, 25 M stars across a 14,000-ly-wide central region; second-largest image Hubble has released | ESA/Hubble heic1901, NASA M33 |
| NGC 604 | Giant H II star-forming region, ~1,500 ly across, ~40× the visible Orion Nebula, >200 hot massive young stars; among the largest known in the Local Group; second most luminous H II region in the Local Group | NASA M33, ESO, ESA/Hubble heic1901 |
| NGC 595 | Second of the four brightest H II regions in the survey | ESA/Hubble heic1901 |
| Star formation | ~1 solar mass every 2 years; rate ~10× Andromeda's average | ESA/Hubble heic1901, NASA M33 |
| Motion | Moving toward Andromeda; suspected gravitational companion of Andromeda; approaching the Milky Way system at ~100,000 km/h (ESO). Both M31 and M33 move toward us; M33 may join the Andromeda–Milky Way collision in >4 Gyr, be torn apart by Andromeda, collide with the Milky Way first, or be ejected — fate not known | EarthSky, ESO, NASA M33 |
| Discovery | Catalogued by Charles Messier on 25 August 1764 (M33); probably recorded by Hodierna before 1654; Edwin Hubble's 1920s Cepheids proved it lies outside the Milky Way | ESO, NASA M33 |
| Structure | Face-on spiral, no bright central bulge, no bar; abundant gas and dust; small satellite: the Pisces Dwarf Galaxy; a clumpy hydrogen stream links M33 and Andromeda (found 2004) | ESA/Hubble heic1901, EarthSky, ESO |

In nu.u, M33 is not a backdrop picture. It is a mapped place (§4) you can descend into until individual Hubble-resolved stars fill the screen, with NGC 604 and NGC 595 as named landmarks, a scale bar in light-years, and the same pinch / pan / rotate grammar as a map.

## 4. Like Google Maps, for a galaxy (live M33 background)

### 4.1 Tiles

The M33 background and the L5 deep map are one system: a **HiPS tile pyramid** (IVOA Hierarchical Progressive Survey, the standard behind ESA Sky, NASA SkyView and Aladin Lite) built from the Hubble M33 mosaic and the PHATTER survey:

- Zoom levels correspond to map scales, exactly like Google Maps: whole galaxy (60 kly) → spiral arm → NGC 604 (1,500 ly) → a single star cluster → resolved stars. Each level is labelled in ly/px and in light-travel time.
- Tiles carry **per-band layers** (§6): the same field in HST optical (F475W/F814W-class), GALEX UV, Spitzer/Herschel IR, Chandra X-ray, VLA radio and Fermi gamma upper-limit layers where surveys exist. Switching wavelength re-tiles the background — the galaxy visibly changes shape, because in UV it *is* a different shape (young stars), and in IR the dust lanes glow.
- The tile manifest is a versioned JSON (`nu-u-m33-manifest-v1`) with per-tile hash, band, epoch and archive URI. It is archived on the network like every release (`PROTOCOL.md` 12.6) and cached on device; tiles are fetched over HTTPS from the archive mirrors (ESA/NASA originals stay the canonical source; khensu mirrors carry the content-addressed copy).

### 4.2 "Realtime updates"

Honest physics, stated in the UI: light from M33 takes 2.73 Myr to reach us, so no app shows M33 "now". What *is* realtime in nu.u:

1. **Archive realtime.** A background task (BGAppRefresh, and on open) polls the manifest and the upstream archives — ESA/Hubble (esahubble.org / ESA Sky), NASA (SkyView, MAST, the Hubble M33 catalogue pages) and ESO — for new or reprocessed M33 data, new PHATTER-class releases and transient alerts (GCN / TNS: supernovae, novae in M33). New tiles land as a map update with a changelog ("M33 map updated · new HST epoch · source: ESA/Hubble").
2. **Sky realtime.** For L1, your local sky is computed for *this second*: scintillation from live conditions (§5.2), satellite and planet positions, and any transient alert overlaid at its real coordinates.
3. **Clock realtime.** The cosmic timeline can run at 1×: stars vary on their real periods (a Cepheid pulses over days, compressed only when you scrub time).

Every tile and catalogue row shows `observed`, `emitted`, `archive epoch` and `source`. If upstream is unreachable, the cached map remains and is labelled with its epoch — never silently stale.

### 4.3 Where the data comes from (v1 endpoints)

All public, no key required for the v1 read path; every fetch is GET, cached, and attributed on screen:

| Data | Upstream | Use in nu.u |
| --- | --- | --- |
| M33 Hubble mosaic, NGC 604/595 imagery | ESA/Hubble heic1901 + ESA Sky HiPS | L5 tiles, background |
| M33 facts, mosaic metadata | NASA Hubble Messier Catalog M33 | Catalogue constants, credits |
| M33 wide field | ESO/S. Brunier image (ESO b13) | Farthest-zoom context tile |
| Finding charts, visibility | EarthSky M33 guide | "See it tonight" card (mag 5.7, November best, binocular challenge) |
| Stars, parallaxes, variability | Gaia + VSX via CDS VizieR / SIMBAD | L1/L3/L5 stars, twinkle physics |
| Multi-wavelength fields | NASA SkyView (DSS, GALEX, WISE, ROSAT, Fermi), ESA Sky | Band layers |
| Transients | GCN / Transient Name Server notices | Live pins on the map |

## 5. Why stars twinkle — real physics, three twinkles

Stars do not twinkle in space. nu.u models the three real effects separately and labels which one you are seeing. There is no decorative `sin` flicker anywhere in the code (`TwinklePhysics.swift`).

### 5.1 Intrinsic variability (the star itself)

Per variability class from the catalogue: Cepheid pulsation (period–luminosity, radial pulsation changing \(T_\text{eff}\) and radius — the very stars Hubble used to measure M33's distance), RR Lyrae, eclipsing binaries (geometric flux dips), rotating spotted stars, Miras, and flare stars (stochastic UV/optical flares). Amplitude and period are catalogue values where known, class-typical where not, and the spectral cube is re-evaluated per phase, so a Cepheid does not just get brighter — it gets *bluer and redder* as it pulses, as the real star does.

### 5.2 Atmospheric scintillation (Earth's air — AR / tonight mode only)

When you look from Earth (L1, and AR sky mode), the image dances because turbulent air cells refract it (the same reason [EarthSky](https://earthsky.org/clusters-nebulae-galaxies/triangulum-galaxy-m33-a-binocular-challenge/) warns M33 looks like "a water spot on a window": low surface brightness smeared by air). Model: Kolmogorov turbulence, Fried parameter \(r_0\) (default 0.10 m at 500 nm, adjustable, weather-seeded), intensity variance

\[
\sigma_I^2 \propto \lambda^{-7/6}\,(\sec z)^{11/6}\,r_0^{-5/3}
\]

evaluated per star per frame with a frozen-flow phase screen. Consequences that fall out of the physics and that Night Sky-class apps do not show: bright stars twinkle less than faint ones near the horizon in relative terms but scintillate faster; planets (extended discs) barely twinkle; blue flickers more than red (chromatic scintillation — the star flashes colours, as Sirius really does). Turn the atmosphere off and the sky goes space-still: that toggle *is* the lesson.

### 5.3 Propagation effects (space between)

Interstellar scintillation for compact radio sources, gravitational microlensing brightening (rare, labelled when simulated), and photon shot noise at the detector limit: faint stars flicker because photons arrive one at a time (Poisson). At L5 zoom on a faint Hubble star, what you see is counting statistics, not atmosphere.

## 6. Wavelengths — music is only the audible band

### 6.1 The band system

One spectrum control spans **25 orders of magnitude**, logarithmic like pitch:

| Band | Range | What you see in M33 | v1 layer |
| --- | --- | --- | --- |
| Gamma ray | < 0.01 nm | Pulsars, cosmic-ray interactions; mostly upper limits at M33's distance | Fermi-LAT layer, labelled sparse |
| X-ray | 0.01–10 nm | X-ray binaries, hot gas, supernova remnants | Chandra/ROSAT-class layer |
| Ultraviolet | 10–400 nm | The youngest, hottest stars; M33's spiral arms sharpen | GALEX/HST UV layer |
| **Visible** | 400–700 nm | The Hubble mosaic; human trichromatic colour | HST F475W/F814W-class |
| Infrared | 700 nm–1 mm | Dust lanes glow, hidden star formation, cool stars | Spitzer/WISE/Herschel-class |
| Microwave | 1 mm–30 cm | CMB (at L6), cold gas | Planck-class (L6) |
| Radio | > 30 cm | Synchrotron, H I 21 cm — M33's gas disc extends past the stars | VLA-class H I layer |
| **Audible (sonified)** | 20 Hz–20 kHz | **Music is this band.** Any field above can be *mapped* into it (§6.4) | nu.waves engine |

The control is a continuous log-frequency slider (with band detents) plus direct band chips: Gamma · X · UV · Visible · IR · Microwave · Radio · Mantis · Sound. Moving it cross-fades tile layers and re-projects every star's cube. In nu.waves terms: wavelength is pitch for light.

### 6.2 Human observer

CIE-class trichromatic projection of the cube through cone fundamentals. This is the only mode whose colours are "true", and the UI says so; every other mode is labelled *false colour — mapped for your eyes*.

### 6.3 Mantis-shrimp observer (the 19-channel mode)

Mantis shrimps (stomatopods) are the extreme case in nature: **16 photoreceptor types** — 12 channels for colour (including ultraviolet), plus polarisation channels (linear and circular) — packed into a midband stripe they sweep across the scene. (Popular accounts round this to "16–20 cones"; the peer-reviewed count is 16 photoreceptor classes, 12 of them chromatic. nu.u's pipeline is built for **19 channels** — 12 spectral (UV→red), 4 linear-polarisation, 1 circular-polarisation, plus intensity and a scanning-midband channel — so the mantis observer uses the full cube and the count the user asked for is the renderer's channel count, with the biology stated honestly.)

Rendering: the 19-channel cube is *not* collapsed to RGB by averaging. nu.u shows what the information looks like to a visual system that keeps the channels separate:

- **Channel-strip view.** The scene rendered in 12 spectral strips + polarisation strips (a contact sheet you can scrub), each strip a real measurement band.
- **Opponent-projection view.** A learned-free, published-matrix projection of the 12 chromatic channels into human RGB that preserves *discriminability* (things the mantis can tell apart look different, even when a human would call both "red"). Two flowers — or two stars — metameric to us separate on screen.
- **Polarisation view.** Degree/angle of polarisation as hue/brightness: scattered light, nebula geometry and the H I field structure appear that no human eye has ever seen directly.
- **Midband scan.** An optional animation that sweeps the high-acuity stripe across the scene the way the animal sweeps its eyes, because mantis colour vision is a *scanning* sense, not a snapshot.

The mantis mode is the flagship demo of the spectral-cube architecture: no new data was downloaded; the same M33 re-rendered for a different animal.

### 6.4 Audible observer — sonification through nu.waves

Any band can be mapped into sound by the nu.waves engine (the reason nu.universes is part of nu.waves): log-frequency transposition of the spectrum into 20 Hz–20 kHz, brightness → loudness, polarisation angle → position in the spacetime bubble™. A gamma-ray field becomes audible; a chord *is* a spectrum. ñü.ÊQ (gain, reverb, echo) applies to sonified fields exactly as to music. This is an accessibility feature as much as a toy: the whole map is navigable by ear.

## 7. RealityKit + AR (native, `khensu-apple`)

Shipped in `Waves/Universes/` inside the `nu.khensu.waves` target (iOS/iPadOS/macOS 26, Swift 6, RealityKit):

| File | Role |
| --- | --- |
| `UniverseModels.swift` | Scale layers, cosmic-time integrator (FLRW), 19-channel cube, observer definitions, band table |
| `M33Catalog.swift` | The §3 constants, landmarks (NGC 604, NGC 595, centre, Pisces Dwarf), HiPS manifest client for NASA/ESA/ESO tiles, transient pin model |
| `TwinklePhysics.swift` | §5: variability classes, Kolmogorov scintillation, shot noise. No decorative flicker |
| `SpectralMapper.swift` | Cube → human RGB, cube → mantis strips/opponent/polarisation, cube → audio parameters |
| `Flight/FlightCatalog.swift` | The map in parsecs (equatorial J2000, Sun at the origin): JPL planet elements, the HYG, UNGC and 2MRS catalogues from `Universes/Data/`, the labelled Milky Way model, galaxy particle discs at catalogue size, inclination and position angle, and the places with their best viewing angle |
| `Flight/FlightShaders.metal` | `CustomMaterial` geometry modifier that turns four corners per source into a camera-facing sprite whose size and brightness follow from absolute magnitude and true distance; twinkle from §5.2 near Earth only; the mosaic surface shader that makes the Hubble sky transparent |
| `UniversesRealityView.swift` | `FlightRig` (target, distance, heading; the Google Earth hop between places) and `FlightScene` (one `LowLevelMesh` per layer, per-frame exposure and labels from `SceneEvents.Update`, the M33 mosaic plane at 23° / 54°, AR on a table) |
| `UniversesView.swift` | SwiftUI shell: fly-to menu and chips, focus card with distance readout, fullscreen, AR, cosmic timeline, the atmosphere toggle. The `-place NAME` launch argument opens a place (like `?place=` on the web) |

AR specifics:

- **Tabletop mode.** `RealityView` with world tracking places the M33 disc (or the L6 universe shell) on a detected plane; walk around NGC 604. Content is anchored, occluded by real objects where the device supports it, and lit by the room (RealityKit environment lighting) at low intensity so the galaxy stays the light source.
- **Sky mode.** Point the phone at the real sky: the catalogue sky (L1) registers to compass/gyro (and, where available, ARKit sky segmentation), scintillation turns on (§5.2), and tapping M33's real position — magnitude 5.7, a binocular challenge 15° from Andromeda past Mirach, per [EarthSky](https://earthsky.org/clusters-nebulae-galaxies/triangulum-galaxy-m33-a-binocular-challenge/) — descends into the deep map. What you could not see with your eyes, you now fly through.
- **visionOS-ready.** The scene is a `RealityView` volume by construction; no UIKit-only rendering. Full immersion space is a later target, not a rewrite.
- **Performance budget (design targets, to be benchmarked, §11).** 120 Hz on ProMotion at L1 (10⁵ stars), 60 Hz at L5 (10⁶ instanced sprites + splats) on A17 Pro-class; MetalFX upscaling optional; total resident catalogue < 250 MB with tile cache capped and evictable. Night Sky renders a chart; nu.u's budget is spent on spectral instancing and splats.

Waves integration: `WavesRootView` becomes a two-tab shell — **Listen** (the existing WKWebView over waves.khensu.nu, unchanged) and **Universes** (native `UniversesView`). The `waves` JS bridge gains `{type:"universes", band, cosmicTime}` so a sonified field can play through the web player's spacetime bubble, and the native view can hand a track to the player ("hear this nebula in nu.waves").

Camera usage: the Waves `Info.plist` camera string gains AR/sky wording ("…and to place galaxies in your room and over the real sky with AR. Frames stay on this device."). No frame ever leaves the device (fixed decision).

## 8. Beating Night Sky — where the graphics budget goes

| Night Sky-class apps (chart) | nu.u (place) |
| --- | --- |
| RGB star points, static sizes | 19-channel spectral sprites, PSF per band, HDR tone mapping |
| Flat Milky Way photo backdrop | Splat nebulae + catalogue stars in 3D depth; parallax on fly-through |
| Atmosphere as blur/glow | Kolmogorov scintillation physics (§5.2), planets steady, Sirius flashing colour |
| One epoch (tonight) | 13.8 Gyr scrub + labelled future prediction (§2.2) |
| Visible light only | Gamma→radio + mantis + sonified (§6) |
| Sky chart AR overlay | Registered sky AR *and* tabletop galaxy AR, one scene graph |
| Closed catalogue | Cited, versioned, archived open data (NASA/ESA/ESO/Gaia) with per-object provenance |
| Object view: a textured Moon with names | 25 photoreal globes turned to their real orientation and lit from the Sun's real direction at the map's time (phase, day and night, ring shadows); 943 IAU names, each with the story of the name; the same globe in the map and close up (§16.7) |

## 9. Blender pipeline (3D models)

Galaxy hero models (the tabletop M33 mesh/splat set, the L6 shell, marketing renders) are authored procedurally, not hand-modelled:

- `design/nu-universes/blender_m33.py` builds M33 in Blender from the §3 constants: logarithmic spiral arms (face-on, no bulge, no bar), 40,000 instanced star points weighted by the UV/optical/IR arm profiles, NGC 604/595 emission knots, dust-lane splats, and a Pisces Dwarf satellite — then exports USDZ (RealityKit/AR Quick Look) and glTF (web) and a `.nu` splat set (`design/nu-3d.md`). Run headless: `blender -b -P design/nu-universes/blender_m33.py -- --out ~/Desktop/nu-u-m33` or interactively via the Blender MCP (`execute_blender_code`) when Blender is running — v1 was authored with the MCP offline, so the script is the source of truth and the MCP is the live-preview path.
- The Blender model is the *reconstruction*; the Hubble tiles are the *data*. Both ship, labelled as such, and the RealityKit scene cross-fades between them by zoom (model far, tiles near), so marketing beauty never masquerades as measurement.

## 10. Web surface (published with v1)

`https://iverse.khensu.nu` (header button i.verse), with `universes`, `rabbithole` and `portal.khensu.nu` and the apex `khensu.nu/universes` opening the same page; `inverse.khensu.nu` 301s to iverse. The five hosts plus the typo redirect share one own certificate with aura. Its link preview is the flight itself, recorded from the page by `khensu-site` `tools/og-flight.sh` (Earth's orbit to M33, the card's words on top). The hero is the M33 Hubble mosaic, and `#map` is the same 3D flight as the app in three.js (`khensu-site` `src/scripts/universes/flight.ts`), drawn from the same files (`/universes/data/`, built by `design/nu-universes/catalog.py`) with a logarithmic depth buffer from 10⁻⁹ to 10⁹ pc. Search, chips and labels fly the camera; `?place=NAME` opens a place; fullscreen fills the window. A control + eye.slash button hides the search, directions, fullscreen, clock, chips and readout. Those same controls fade out while the camera is flying, including the rabbithole flash, and come back when the move ends. The place chips stay one line and scroll, so a changing distance readout cannot reflow them. The page also carries the wavelength bands, the cosmic timeline and the catalogue facts with their NASA/ESA/ESO/EarthSky credits. It is the catalogue entry for nu.universes inside nu.waves and the link target for `nu:universes.khensu.nu`. Present tense, as shipped, per the publishing skill; unmeasured figures are labelled estimates.

## 11. Benchmarks and gates (to be measured, replaces estimates)

- Frame rate / energy at L1/L5/L6 on the oldest iOS 26 device and on A17 Pro+ (MetricKit), vs. the §7 targets.
- Tile fetch: cold M33 (whole galaxy → NGC 604) time on Wi-Fi and 5G; cache hit rate.
- Spectral correctness: rendered star colours vs. catalogue \(T_\text{eff}\) blackbody + band layers, ΔE on a 100-star test set.
- Scintillation: simulated \(\sigma_I^2\) vs. the §5.2 formula across airmass; planet/star twinkle ratio.
- Mantis projection: metamer pairs (human-identical, mantis-distinct spectra) must separate by ΔE > 10 in opponent view.
- AR registration error in sky mode (degrees) against known bright stars.

## 12. Privacy, security, rights

- Nothing is processed on servers: rendering, sonification, AR and timeline integration are on-device. Network use is tile/catalogue GETs and transient alerts only; no location is uploaded (sky mode computes locally; the web page asks for no location).
- Imagery credits ride with every tile (ESA/Hubble: NASA, ESA; ESO: ESO/S. Brunier; NASA pages as cited). Hubble/ESA/ESO public imagery is used under its public-outreach terms with attribution on screen.
- 3D assets follow `design/nu-3d.md`: no code, no external references, USDZ exports pass `usdchecker --arkit`.

## 13. Patent assessment

Per `PATENTS.md` practice — assess, publish anyway, never hold the sites:

| Candidate | Prior art to search | Note |
| --- | --- | --- |
| 19-channel spectral-cube scene re-projected per observer (human / mantis / instrument / audio) from one archived dataset | Spectral rendering (Hero Wavelength Spectral Sampling), hyperspectral viewers, sonification (NASA) | The per-observer re-projection of a *mapped place* (not a single image) with polarisation + sonification in one gesture may be narrow but novel; search first |
| Map-tile (HiPS) galaxy with per-band layers and emitted/observed/predicted time labelling | ESA Sky, Aladin Lite, SkyView, Google Sky | Combination with cosmic-timeline prediction flagging; likely defensive publication |
| Kolmogorov scintillation + intrinsic variability + shot noise as separable, labelled layers | Scintillation simulators, planetarium software | Publish as spec |
| Mantis midband-scan rendering of astronomical fields | Stomatopod vision models | Publish as spec |
| Turn-by-turn directions through real space: milestones found by log-sampling the straight path against shells (planet orbits, belts, heliopause, Oort cloud, Local Bubble), the Milky Way's disc and galaxy extents, with times per travel mode | Google Maps directions, Celestia/SpaceEngine "go to", NASA Eyes | The milestone method is simple; the novelty, if any, is the Maps grammar applied to a real-distance universe. Defensive publication |
| Rabbitholes: a wormhole graph whose gates open by the real sky over the user (galaxy above the horizon now), by places the user has visited, or always; routing by least bubble distance through open gates, with reasons for closed ones | Game fast-travel unlocked by discovery, location-gated AR games | Gating teleports on the live sky at the user's location, computed on the device, may be narrow but novel; search first |
| Social presence without a feed: people met only by being at the same place in the same map at the same time, over the mixnet | Spatial chat, MMO zones, Snap Map | Combination with the no-scroll rule and mixnet presence; assess when built |
| Close-up globes that share the map's clock: IAU rotation elements and the Sun's real direction give the phase seen from Earth, a "Sunlit side" swing, and ring shadows computed both ways in the shader | Night Sky, SkySafari, NASA Eyes, Celestia | Each part is known; the combination with tappable name origins and one globe for map and close-up is likely defensive publication |
| Time travel by animating the map clock to a chosen moment (smoothstep over a duration that grows with log of the gap), with everything moving there visibly and pausing on arrival | Planetarium time controls, Stellarium | Defensive publication |
| Tap picking in screen space: labelled bodies within 16 px, else the nearest orbit segment within 10 px, with orbit and body lit together | GIS feature picking | Publish as spec |

## 14. Open questions

1. HiPS hosting: khensu archive mirrors vs. hot-linking ESA/NASA HiPS (bandwidth, terms) — v1 manifests point at upstream with khensu content-addressed fallback.
2. Gaia subsampling licence/attribution string at L3/L5 densities.
3. visionOS full-immersion target and shared AR sessions (two people around one tabletop M33) — SharePlay for galaxies, mirroring nu.waves SharePlay.
4. Fermi/Chandra layer depth at M33: how sparse is too sparse to draw honestly? v1 draws upper-limit layers with explicit "no detection" tiling.
5. Whether the mantis opponent matrix should be fitted to stomatopod photoreceptor sensitivities (Marshall & Oberwinkler-class data) in v1.1 — v1 uses published peak sensitivities.

## 15. Directions and rabbitholes — Google Maps grammar for space

Built 22 Oct 2026 on the web (`khensu-site` `src/scripts/universes/route.ts`, `directions.ts`) and in the app (`Waves/Universes/Flight/Directions.swift`, `DirectionsView.swift`), with the same rules in both.

### 15.1 Layout

Like a Maps directions panel, top to bottom:

1. **From**: where you are. That is the last place you arrived at (this visit, then any earlier visit), else Earth.
2. **To**: a search over every place, grouped. The Solar System comes first in order from the Sun, with each planet's major moons under it, Ceres and the big asteroids under the asteroid belt, Pluto (with Charon) and the other dwarf planets under the Kuiper belt, then near-Earth asteroids and comets. Stars follow, then the Milky Way and beyond, with NGC 604 and NGC 595 under M33.
3. **How you travel**, with a time on each:
   - Rabbitholes (instant jumps, with the spacetime bubble between them).
   - Bubble.
   - Light (299,792 km/s, the fastest real trip).
   - Spacecraft (Parker Solar Probe's record, 191.7 km/s on 24 December 2024, held the whole way).
4. **Duration**: one big number, with the distance and how the trip is made under it.
5. **Steps**: a numbered timeline. Cyan is travel, pink is a rabbithole jump and red is the destination. Each step shows distance from the start, the time to get there in the chosen mode, and a one-line fact. Tap a step to fly there; **Start** flies the whole route, step by step. Jumps are instant, with a flash. The route is drawn on the map.
6. **Fine print**, folded:
   - What each mode means.
   - The bubble speed, 1× to 1 trillion× light speed (default 1 billion×). Warp bubbles are allowed by general relativity on paper and have not been built.
   - Which rabbitholes are open to you and why, and your latitude and longitude.
   - Data sources.

### 15.2 Milestones

The straight path from A to B is sampled in log distance from both ends (about 1,200 samples), so a shell 1 AU across is still found on a megaparsec trip. A step is added wherever the path crosses one of these:

| Kind | Where |
| --- | --- |
| Planet orbits | Mercury to Neptune at their semi-major axes |
| Asteroid belt | Enter at 2.2 AU, leave at 3.3 AU |
| Kuiper belt | Enter crossing Neptune's orbit (30 AU), leave at 50 AU |
| Heliopause | 120 AU |
| Oort cloud | Enter at about 2,000 AU, leave at about 100,000 AU |
| Local Bubble | About 150 pc |
| Milky Way's disc | Radius 15 kpc, half-thickness 1 kpc, galactocentric with the Sun 8,178 pc out and 20.8 pc up |
| Galaxies | Entering or leaving any galaxy's catalogue radius; passing within three radii of one |

A shell is skipped when either end of the trip sits within 5% of it, so Earth to Mars doesn't announce that you are crossing Earth's orbit. The first step gives the heading in right ascension and declination and in galactic longitude and latitude.

### 15.3 Rabbitholes

Rabbitholes form a graph of gates at places, and a jump runs along a link. A gate opens in one of three ways:

- **Always:** Sol, Alpha Centauri and Sagittarius A\*.
- **Sky:** the galaxy is above your real horizon now (LMC, SMC, Andromeda, Triangulum). Altitude comes from your latitude and longitude, the time and the place's right ascension and declination, using Greenwich mean sidereal time. A closed sky gate says when it next rises.
- **Visited:** you have been to a given place, for example NGC 604 once you have reached M33, and the Centaurus A, M81, M101 and M51 groups once you have reached them.

The route minimises the distance travelled by bubble (from the start to the first gate, then from the last gate to the destination). Ties go to the fewest jumps. Closed gates on the ideal route are listed with the reason and when they open.

Your location and the places you have visited stay on the device:
- **Web:** `localStorage`. The site's Permissions-Policy blocks geolocation, so you type your latitude and longitude.
- **App:** UserDefaults, with an optional single Core Location fix rounded to about 1 km. The usage string says it never leaves the device.

Nothing is sent anywhere.

### 15.4 Bodies added for directions

- **Moons:** 22 major moons, at their measured orbit radius and period. Where each is along its orbit today is approximate, and the place card says so.
- **Named bodies:** 32 dwarf planets, asteroids and comets, from NASA/JPL's Small-Body Database (full-precision osculating elements, propagated with two-body mean motion). Each draws its orbit.
- **Belt sample:** a real sample of 4,000 main-belt asteroids, 800 Jupiter Trojans and 1,500 Kuiper-belt objects, drawn as faint points.

`design/nu-universes/small_bodies.py` writes `bodies.json` and `belt.bin`.

### 15.5 Social: no feed (spec, not built)

nu.universes becomes a place you share with people, not a feed:

- **No feed, no scroll.** No timeline and no endless list. You meet people by being in the same place at the same time: at NGC 604, at the Moon, at a rabbithole.
- **Moving and jumping.** You move through the space, or jump. Where you can jump depends on where you are, the time (the real sky) and where you have been, as in §15.3, just like real life.
- **AR, VR and flat.** The same presence works in AR (on your table or over the real sky), in VR or immersive space, and on a flat phone or Mac screen.
- **Presence over the mixnet.** Being somewhere is announced only to your contacts, through the mixnet, like messages. Nothing is processed on servers, and the place you are at is never published.

The UI shows no people until this exists; there are no placeholder avatars.

## 16. The live map (web)

Built 23 to 25 Oct 2026 in `khensu-site` `src/scripts/universes/` (`flight.ts`, `solar.ts`, `deep.ts`, `places.ts`, `trip.ts`, `earth.ts`, `body.ts`, `closeup.ts`). The app has not caught up yet: it still has the 22 Oct map.

### 16.1 Data

| Script (`design/nu-universes/`) | Writes | From |
| --- | --- | --- |
| `solar_system.py` | `moons.json`/`.bin` (osculating elements every 10 days), `craft.json`/`.bin` (daily positions), `bodies.json`, `belt.bin` | NASA JPL Horizons, Small-Body Database, Close-Approach Data |
| `deep_sky.py` | nebulae, star systems, pulsars, black holes, quasars, M33's catalogued contents | SIMBAD, ATNF, VizieR (Pellerin & Macri 2011, Sarajedini & Mancone 2007, Relaño et al. 2013, Long et al. 2010, Massey et al. 2006) |
| `constellations.py` | `constellations.json`: the 88 figures (Serpens merged) | d3-celestial (BSD-3, Olaf Frohn) |
| `surfaces.py` | `/universes/surfaces/`: 4K and 1K WebP maps and `surfaces.json` | See §16.7 |

### 16.2 Live time and time travel

The map's clock runs live by default; the time bar runs it from an hour to a year a second, forwards or back, between 1800 and 2050 (the range of JPL's planet elements). Tapping the date, or **Now** while live, opens a picker: a date and time, or a moment (Apollo 11, Voyager 1 at Jupiter, Halley, Hale–Bopp, New Horizons at Pluto, ʻOumuamua, Apophis). The clock then runs to that moment with a smoothstep over 1.4 s plus up to 2.6 s more for big gaps (0.7 × log₁₀ of the days), so everything visibly moves there, and pauses on arrival. **Now** goes back to live. Pulsing stars hold still during the trip, so nothing flashes faster than once a second.

### 16.3 Turning, tapping and searching

- **Turning:** one finger (or the left button) turns the view like a trackball. The camera's up turns with it, so there is no pole to get stuck at. It coasts after a flick, except with reduced motion.
- **Tapping:** in screen space. A photoreal globe under the finger, or a labelled body within 16 px, wins; a body with a map opens close up (§16.7). Otherwise the nearest orbit within 10 px is lit with its body: orbit at full opacity and whitened, a ring around the body that breathes every 2.4 s, and its label lit.
- **Go to:** search reaches every place, labelled or not: moons such as Io and Europa, about 1,600 objects in M33, and the constellations. Matches rank exact, then prefix, then word start, then anywhere.

### 16.4 Deep sky and M33

Nebulae, binaries, pulsars, black holes and quasars sit at their measured places. M33's Hubble mosaic has its sky level subtracted and fades out on an ellipse, so only the galaxy's light is added to space; the modelled M33 stars are thinned with the same mask, so the photo and the model never double up. M33's catalogued objects (Cepheids, clusters, H II regions, supernova remnants and the 400 brightest stars) are searchable by J2000 designation.

### 16.5 Constellations

The 88 figures are snapped to HYG stars brighter than magnitude 6.5 within 0.3° and drawn in 3D between the stars' real positions. They fade out beyond 60 to 400 pc from the Sun, since only from near the Sun do they look like their figures, and going to one puts the camera at the Sun facing it.

### 16.6 Earth directions and privacy

When a trip starts or ends on Earth, the "On Earth" box plans the ground part to the nearest spaceport (or a chosen one, or any address), by car, bike or foot, and a launch step. The card is drawn like the Per-Ankh sailing itinerary: a dot globe, a violet-to-teal route, white stops and a vehicle riding the route. Your location stays on the device. Road routes and address search use OpenStreetMap's open servers (`routing.openstreetmap.de`, `photon.komoot.io`) only after you turn them on, with a disclosure that they see the points sent; otherwise distances are as the crow flies.

### 16.7 Close-up globes

Tapping a planet, a big moon, the Sun, Ceres or Vesta (on the map, its name tag, or **Look closer** on its card) opens it big, while the map flies there underneath.

- **Bodies:** the Sun, the eight planets, the Moon, Io, Europa, Ganymede, Callisto, Titan, Enceladus, Tethys, Dione, Rhea, Iapetus, Triton, Pluto, Charon, Ceres and Vesta.
- **Orientation:** IAU WGCCRE rotation elements (pole and prime meridian, without the small periodic terms) on the map's clock, so Earth's day side, the Moon's face and Saturn's ring tilt are right for the moment shown. Jupiter, Saturn, Uranus, Neptune and Earth are flattened by their measured oblateness.
- **Light:** from the Sun's real direction. **From Earth** puts the eye on the line from Earth, so the phase is the one you would see (the Moon shows its phase name). **Sunlit side** swings round to the day side, turned 30° so the terminator shows. Airless ground uses Lommel–Seeliger blended with Lambert, so a full Moon looks flat as the real one does; cloud tops use a soft terminator and darker limbs; the Sun is limb-darkened. Earth has city lights on its night side and a cloud shell (a typical day, labelled not live). Saturn's rings shade the planet and the planet shades the rings, computed per pixel. Earth, Venus, Mars, Titan, the giants, Pluto and Triton have a thin sky at the limb.
- **Names:** the largest IAU features on the near side, more as you zoom in, never overlapping, plus famous small ones (Tycho, Olympus Mons, the Gale and Jezero rover craters, Pwyll, Pele, Kraken Mare, the tiger stripes, Occator, the Moon's landing sites). Tapping a name shows its type, size, place and the origin of the name. On Venus the names show with the Radar layer.
- **Facts:** diameter, length of day, distance from Earth with the light time, distance from the Sun, and the phase from Earth, refreshed as the clock runs. **Directions** sets the body as the destination.
- **Controls:** drag turns, pinch or scroll zooms, arrow keys and +/− work, Escape closes. On a phone the globe centres in the space above the facts sheet.
- **In the map:** the same globe is drawn at its real size once it is more than a pixel or so across, with the 1K maps, and switches to 4K when it fills the view. The Moon is no longer a dot.
- **Maps:** Solar System Scope (CC BY 4.0, from NASA data) for the Sun, planets, Moon and rings; USGS Astrogeology (public domain) for the Galilean moons; NASA/JPL via Wikimedia Commons (public domain) for the rest. Ceres uses Dawn's enhanced-colour mosaic shown in grey, since it fills the poles in false colour. Map centres were checked against IAU features (Xanadu and Menrva on Titan, Iapetus's dark side, Dione's wispy terrain, Tirawa on Rhea, Sputnik Planitia on Pluto, Occator on Ceres, Pele on Io). About 25 MB of maps, fetched only when a globe is shown.

## Changelog

- 25 Oct 2026: Close-up globes (§16.7). Tap a planet, moon, the Sun, Ceres or Vesta to open it as a big photoreal globe, turned and lit as it is at the map's time, with IAU names and their stories; the same globes now draw in the map. `surfaces.py` builds the maps and names. The breathing highlight ring now stays on its body (its scale animation was scaling its offset too). §16 records the live map built 23 to 25 Oct.
- 24 Oct 2026 (later): Time travel from **Now** and the date (§16.2); tapping an orbit lights it and its body; the trackball fixes the stuck one-finger turn; "Go to" searches every body, M33's catalogued objects and the 88 constellations; the M33 mosaic blends into space instead of showing its rectangle.

- 24 Oct 2026: On the web map, controls hide while the camera flies. A control + eye.slash button hides them the rest of the time. Place chips no longer wrap or jump when the distance line changes.

- 23 Oct 2026: `inverse.khensu.nu` 301s to `iverse.khensu.nu` (autocorrect typo). Same own cert as aura / iverse.

- 22 Oct 2026: Directions and rabbitholes (§15) on the web and in the app.
  - **Panel:** laid out like Google Maps. From is your last place, else Earth. To searches every place, grouped. Then four travel modes with times, the duration, the steps as a timeline, and fine print.
  - **Spacecraft mode:** Parker Solar Probe's record speed.
  - **New bodies:** 22 moons, 32 named small bodies from the JPL Small-Body Database, the asteroid belt and Kuiper belt as places, and a sample of 6,300 real belt, Trojan and Kuiper-belt objects (`small_bodies.py`).
  - **Milestones:** planet orbits, both belts and the inner Oort cloud.
  - **Title:** the page title is nu.i.verse.

- 21 Oct 2026 (later): The map is a 3D flight with real distances, on the web and in the app, replacing the picture viewer below. One map in parsecs: planets from NASA JPL's Keplerian elements; 42,246 HYG v4.1 stars (magnitude 8 or within 25 pc) coloured by B−V; 869 UNGC galaxies with measured distances (Karachentsev 2013); 43,415 2MRS galaxies placed by redshift (H0 = 70), which show the cosmic web; a labelled Milky Way model (Sun 8,178 pc from the centre, bar, four arms); particle discs for the bright galaxies at their catalogue size, inclination and position angle; and the M33 mosaic as a plane 14,000 ly wide at its real tilt, with NGC 604 and NGC 595 as places on it. `design/nu-universes/catalog.py` builds the four data files from VizieR and HYG. Each point is a sprite whose brightness is m = M + 5 log₁₀(d / 10 pc) against a limiting magnitude that rises as you zoom out, so the Sun washes out up close and galaxies appear from far away. Flying between places zooms out and back in like Google Earth, and lands at each galaxy's best angle (mostly face-on, tipped 35° toward the Sun). The app draws this with RealityKit `CustomMaterial` sprites (`Flight/`) and puts the current view 30 cm across on a table in AR. Web label and focus-card styles are global, because Astro's scoped styles never reached the script-made tags. `m33_stars.py` and the mosaic-star twinkle are removed.
- 21 Oct 2026: The map is the real mosaic in both surfaces. App: the heic1901a mosaic (4000 × 2251, bundled as `m33-hubble.jpg`) is the disc texture; an orbit camera (drag to pan, pinch to zoom, twist to rotate, double-tap to tilt) replaces RealityKit's default camera, which sat in the disc plane and saw it edge-on; landmark chips fly the camera to NGC 604, NGC 595 and the centre; fullscreen hides the deck, the navigation bar, the tab bar and the status bar; the AR button switches the camera to world tracking and puts the galaxy 30 cm across on a table. Twinkle stars are the mosaic's 320 brightest point sources at their real positions, found by `design/nu-universes/m33_stars.py`, with temperature estimated from colour (labelled an estimate); the demo spiral is no longer drawn. Web: images are served from `khensu.nu` (the CSP allows only same-origin images), and the map is a near-full-window pan and zoom viewer with fly-to chips and fullscreen. Per-band HiPS tiles and the deep zoom pyramid of the 665-megapixel original are still to come; other bands are labelled false-colour tints until then.
- 18 Oct 2026: v1 — spec, RealityKit+AR app in `nu.khensu.waves`, Blender M33 pipeline, web page at khensu.nu/universes. M33 deep map from ESA/Hubble heic1901 (54 pointings, 665 Mpx), NASA Messier 33, ESO b13, EarthSky guide.
