# ñü.Føňt: the house typeface

**Decided 12 October 2026. First release built and published the same day; second release the same day with ñü.Føňt Mono, pulse mode, and Vietnamese, Greek and Cyrillic. Taken off the sites' display roles the same evening: Elliott found the first draw handwritten (the d floated; letters did not share a baseline), Dosis was tried for titles and dropped within the hour ("i don't like dosis in the actual site"), and the sites went back to Inter and JetBrains Mono. The redraw is section 6, item 1.** Shown as **ñü.Føňt** (o with stroke U+00F8, n with caron U+0148). Code, files and the page use `nu.font` (`/font` on khensu.nu, `tools/font/` in `khensu-site`); the font family name inside the files is `nu Font`, PostScript names `nuFont-<Style>`. Running text uses nu.font. Elliott typed the name both ways, ñũ.Føñt and ñü.Føňt, and closed with "this style is called ñü.Føňt", so that is the display form; the first form is listed here so the record shows the choice.

ñü.Føňt is meant to be the typeface for everything people see from khėnsu.ñü: the wordmark, headings, navigation, buttons and labels on every site, the apps when they reach it, and anything anyone else wants to set in it, because it is published free under the SIL Open Font License. Today it is on its own page, in the files, and on the link-preview cards; the sites wait for the redraw. It is also the home of the rule that letters can move: a wordmark is written into a page as paths, one per stroke, and any stroke can animate on its own. The dot on the ė, Elliott's E, is the first one that does.

## 1. What the first release is

| Item | Value |
| --- | --- |
| Glyphs | 567 in each family: ASCII, Latin-1, Latin Extended-A, the Vietnamese letters with stacked marks, monotonic Greek, Cyrillic for Russian, Ukrainian and Belarusian, the ligatures and letters the names need (æ œ ð ł ø ħ þ ß ŋ and capitals), currency and typographic symbols, and precomposed letters for every mark the names use: ė ċ ñ ũ ẽ ü ë î ê ŵ š ř ě ů å ț and their relatives |
| Families | **ñü.Føňt** (`nu Font`) and **ñü.Føňt Mono** (`nu Font Mono`), the same letters fitted to a 600-unit cell: wide skeletons are squeezed (arcs become ellipse arcs, the pen keeps its width), narrow ones centred. `post.isFixedPitch` and PANOSE monospaced are set so editors list it as a code font. Digits are tabular in both |
| Weights | Ultralight 100, Light 300, Medium 500, Bold 700, Heavy 800, Blackout 900 |
| Axes | `wght` 100 to 900; `slnt` 0 to −11, the italic |
| Masters | 12 per family: the six weights, upright and slanted |
| Files | `nuFont-Variable.ttf` (854 KB) and `.woff2` (188 KB); `nuFontMono-Variable.ttf` (834 KB) and `.woff2` (186 KB); twelve static TTFs per family of about 133 KB and WOFF2s of about 20 KB; `nufont.zip` (1.4 MB) with all of them; `nufont.json` with every measured figure |
| Metrics | 1000 units per em; cap height 700; x-height 350; descender −216 (350 ÷ φ); ascender 700 |
| Where | `khensu-site/tools/font/nufont.py` (the generator) and `glyphs_more.py` (symbols, Latin extras, Greek, Cyrillic, the composite tables), `tools/font/build.sh` (build, copy, zip), `sites/khensu-nu/public/fonts/nufont/` (the files people download), `src/data/nufont-marks.ts` (generated inline wordmarks), `src/components/khensu/NuMark.astro` (the component that inlines them), `sites/khensu-nu/src/pages/font.astro` (the page) |

Every figure above comes from the build; the page reads them from `nufont.json`, so nothing on it is typed by hand.

## 2. The shape rules

The font is parametric. Each glyph is a skeleton of centreline strokes (lines, circle and ellipse arcs, filleted polylines) and the weight is the width of the pen that strokes them. Because the skeletons are shared, every master has the same point structure and the whole family interpolates into one variable font.

| Rule | How it is drawn |
| --- | --- |
| Golden ratio throughout | Cap height 700, x-height 350 (capitals are twice the bowl of a b), descender 350 ÷ φ, H and its family 700 ÷ φ wide, the A crossbar at 700 ÷ φ² |
| No sharp edges, not fully round | Every stroke ends in a superellipse with exponent 2.6: a capsule that is rounder than a square and squarer than a circle. Dots and the period are the same shape. Corners of v, w, z, A, M and the marks are filleted arcs, never points |
| No stems where a letter can live without one | n is an upside-down horseshoe, u a horseshoe, m two horseshoes with equal legs; r is a tall quarter-ellipse rising from the baseline and bending a bit past the top ("a bit more than half a curve"); o, c, e, s, v, w, x and z have no stem |
| h squiggles back | The stem comes down from the ascender to the x-height, half the letter's height, and bends into the shoulder, which bends down into the right leg. The left side never touches the baseline. This is Elliott's sketch of 12 October, with the corners rounded |
| b and d float | A short stem from the ascender to halfway down the bowl; the bubble sits 8 % of the x-height above the baseline, so neither the stem nor the bubble is on the baseline |
| Stems stop at half height | Where a stem is cut, it ends at 50 % of the glyph's height, never lower on one side |
| Heavy weights widen | From Bold up, bowls and arches grow sideways so counters stay open; Blackout keeps a counter 50 units tall |
| Capitals look like capitals | I has its top and bottom bars; H is an H; every capital with a stem keeps it in this release |
| Marks stack | A composite names its base and one or more marks. Each mark sits a gap above the ink below it (the base, or the previous mark); marks below (dot below, cedilla, comma, ogonek) hang from the baseline and don't push the ones above. Side marks (ogonek, horn) attach at the right edge. Greek tonos is the acute; dialytika the dieresis |
| Other scripts, same hand | Greek and Cyrillic are drawn from the same horseshoes, bowls and capsule ends; Cyrillic capitals take the Latin capital proportions (700 ÷ φ wide), and Greek descenders the Latin descender |

### 2.1 Glyphs that still have a stem

Listed for Elliott's decision; the generator prints the same list with `python nufont.py stems`, and the page shows it under Stems.

| Glyph | Stem in this release |
| --- | --- |
| h | the top half only, from the ascender to the x-height, then the squiggle into the shoulder |
| b, d | a short stem from the ascender to half the x-height; the bubble floats |
| a | single-storey: a right stroke from the x-height to the baseline |
| i, dotless i, j | a short stem of x-height; j continues into the descender and hooks left |
| k | a full stem; both arms meet it at 42 % of the x-height |
| l, l with stroke | a full stem that curls right at the baseline |
| f, t | a stem through the crossbar; f hooks at the top, t curls at the baseline |
| p, q, g, y | a stem or arm into the descender; g and y hook left |
| B D E F H I K L M N P R T, Lslash | capitals keep their stems |
| 1, 4 | digits with a vertical |

Everything else, n m u r o c e s v w x z, the round capitals C G O Q S U, A V W X Y Z and the remaining digits, has no stem.

## 3. Letters that move

The rule: **every letter and every mark can join the ñü.aura colour shift, or act on its own — fade, pulse, drift, burst — and the choice is made in CSS, not with images or crossfaded text.**

How it works in this release:

1. `nufont.py marks` writes each wordmark as SVG with one `<path>` per stroke. Diacritics carry a class: `mark dot`, `mark dieresis`, `mark tilde`, `mark caron`, `mark circumflex`, `mark ring`, `mark comma`, `mark cedilla`, and the new `macron`, `breve`, `doubleacute`, `hookabove`, `dotbelow`, `ogonek`, `horn`. Every path also carries `data-g` (glyph name) and `data-i` (letter index), so any letter can be addressed.
2. `NuMark.astro` inlines the SVG, adds the visually hidden text for readers and search, and, when asked, fills the letters with the house gradient (a `<linearGradient>` that repeats and slides over 9 s, the same period as `--aura-flow-dur`).
3. CSS does the motion. `.nf-word .mark.dot` scales 1 → 1.28 → 1 over 2.8 s with a soft glow, and its fill phases green → blue → purple over 9 s. Nothing else moves: the tilde on ñ and the dieresis on ü keep the fill of the letters. `prefers-reduced-motion` holds the dot still in the accent colour.
4. The ė is lowercase only. Ė exists in the font but has no animation.

The wordmarks in use: the hero title, the header brand and the footer brand on khensu.nu; the webË heading on /webe; the header brand on dev.khensu.nu; the hero on elliottwave.studio/khensu, which is generated from the khensu.nu homepage; and `khensu-full` (kħėñšü.ñü), `shield-full` (šûñüłîñk.šħîēłð) and `webe` for the marketing cards.

### 3.1 Pulse mode

Asked for on 12 October: "these Ë diacritics should pulse and use nu.aura … the mode will pulse inside the diacritic too and sort of have a light that circles inside and gets a hard cut off from the internal edge of the character. The pulse light should cross fade out and into another location at the same time, like the pulses do on the spacetime bubble."

**How it is done.** For every stroke tagged `mark`, `svg_runs` emits, right after the mark's `<path>`, a `<clipPath>` holding the same outline and a `<g class="nf-lights" clip-path="url(#…)">` with two `<circle class="nf-light a|b">`. Each circle is centred on the mark, has a radius of 0.42 × the mark's larger dimension, and carries inline CSS variables: `--nf-blur` (0.3 × radius) and four resting places `--lx0..3`, `--ly0..3` at ±0.42 of the mark's width and height, the two lights offset by 180° so they are never in the same place. Everything is in glyph units; CSS transforms on SVG elements use the user coordinate system, so the same numbers work at any rendered size. The id placeholder `@ID@` is replaced by `NuMark.astro` with an id unique to the page, or the whole lights block is stripped when the mark isn't in pulse mode, so ordinary wordmarks carry no extra bytes.

`global.css` then animates:

- `.nf-word.pulse .mark`: fill phases through the aura (`nf-dot-aura`, `--aura-flow-dur`, 9 s);
- `.nf-word.pulse .nf-light`: `filter: blur(var(--nf-blur))`, opacity 0 → `--nf-light-opacity` → 0 over `--nf-light-dur` (3.6 s, `nf-light-fade`), and a `step-end` move through the four places over 4 × `--nf-light-dur` (`nf-light-move`), so a light only ever jumps while it is dark;
- `.nf-light.b` runs both animations half a period behind, so one light fades in as the other fades out;
- the clip gives the hard edge: the glow is soft inside the shape and stops dead at the outline;
- `prefers-reduced-motion` hides the lights and holds the marks in the accent colour.

**How to set colours and speed** (on the `.nf-word`, or on any ancestor):

| Variable | Default | What it does |
| --- | --- | --- |
| `--nf-light` | `#fff` | the light's colour; any colour, including `var(--aura-blue)` |
| `--nf-light-opacity` | `0.85` | peak brightness |
| `--nf-light-dur` | `3.6s` | one fade in and out; the light moves every period, and tours its four places in four |
| `--aura-flow-dur` | `9s` | one pass through green, blue and purple for the marks' fill |
| `--aura-green`, `--aura-blue`, `--aura-purple` | the site's | the three aura colours |

Turn it on with `<NuMark name="webe" aura pulse />`. It is on for the webË heading on /webe and the khėnsu.ñü hero title; the header and footer brands stay quiet.

## 4. Where the font is used

| Role | Today (since the evening of 12 October 2026) | When the redraw is signed off |
| --- | --- | --- |
| Headings h1–h3, the wordmark, header navigation, buttons, pills, chips, the product bar name, StatStrip figures | Inter: `--font-display` is `var(--font-sans)`. The name is text through `Name.astro`, which draws the pulsing dot in CSS over Inter's e (`--edot-top` 0.11em, `--edot-size` 0.125em, from Inter 600's dot accent) | ñü.Føňt, through `--font-display`; the wordmarks back to `NuMark` paths |
| Running text, forms, tables | Inter | Inter until ñü.Føňt has kerning and hinting. One line switches it: set `--font-sans` |
| Code, `~` commands, the node terminal, figures and small labels | JetBrains Mono, through `--font-mono` | ñü.Føňt Mono, through `--font-mono`, with JetBrains Mono as the fallback |
| The nu.font page, the downloadable files, and the hyper link-preview mode (`OgCard` `mode="hyper"`, `MODE=hyper` for og tools); shipped cards use Inter | ñü.Føňt | ñü.Føňt |

Dosis itself was tried for titles for part of that evening (`--font-title`) and removed the same day, files included. The studio takes the same `global.css` (with its own accent) and the same components through `tools/sync-studio.sh`, which also copies the variable WOFF2s into the studio's `public/fonts/nufont/`.

## 5. Installing it

Published free under the SIL Open Font License 1.1 so it installs anywhere and ships inside any app. Mac: Font Book. Windows: right-click, Install. Linux: `~/.local/share/fonts` and `fc-cache -f`. iPhone and iPad: a font-installer app, or the TTF in an app bundle under `UIAppFonts`. Android: `res/font`. Web: one `@font-face` with `font-weight: 100 900` and `font-style: oblique 0deg 11deg`. khensu-apple bundles the variable TTF when it adopts the face.

## 6. Open, in order

1. **The redraw.** Elliott's brief, 12 October: "we don't want this handwritten feel… we want modern and clean"; "the d looks like it's floating. everything should have same baseline like any font"; "good job on h and r"; "use the dosis style but don't actually use that font… a font that is dosis but with our stem rule". So: Dosis-like proportions on the same skeleton engine (measured from Dosis at 1000 UPM: x-height 472, cap 731, ascender 763, descender −232, o ink about 380 wide, H 421, round terminals, stadium bowls, double-storey a, single-storey g, hooked f and j, straight y tail, dotted zero), with every letter on the baseline, no floating b or d, and the stem rule kept where it was approved: h and r, and with them n, m and u as arches. Expected to change beyond h and r: b, d, p, q back onto the baseline with stems; the a double-storey; g, t, f, l and the capitals on the new heights; the mono refitted. Planned metrics CAP 730, XH 470, ASC 760, DESC −230, overshoot 8; weights 26/50/84/120/142/164 for the six masters. Not started; needs Elliott's go-ahead, then the font files first ("i wanna see the font files once you add our styling for stem rule for h").
2. **Kerning.** No pair spacing yet; the sites used tight letter-spacing on headings. First pairs: every name on the sites, `.ñ`, `ñü`, `kh`, `Fî`, `Bî`, digits.
3. **Hinting or a size-tuned master.** Then running text can switch.
4. **Written styles.** A hand-drawn italic and a sharpie style that stays close to the typed forms, as new masters on a `styl` axis or as sibling families.
5. **Mylar balloons.** Text as floating ñü.3d balloon shells (`design/nu-3d.md`), each glyph inflated from its skeleton with creases and highlights; part of the Templify emulation Elliott is recording.
6. **Emoji and animated emoji** in the same strokes and capsule ends, including Telegram-style animated emoji.
7. **Capsule renderer.** Glyphs drawn from their strokes at run time with a built-in alpha mask, tuned for the Neural Engine and TPUs, so the rounding "fades away" at any size without outline files.
8. **Per-letter presets.** Named cues (fade, pulse, drift, burst) chosen in CSS for any letter or mark, with the choreography of a whole wordmark in one data attribute.
9. **More scripts.** Arabic, Hebrew, Devanagari and CJK; and the language-specific forms Inter carries (`locl` for Bulgarian, Serbian, Dutch ĳ), which need OpenType features rather than more glyphs.
10. **Mark attachment in the font.** Marks are precomposed per letter today. GPOS mark-to-base anchors would let any base take any mark and make the composite table unnecessary.
11. **Mono fit.** Squeezing fits every glyph in the cell, but m, w, M, W and @ get narrow at the heavy weights; a drawn mono master for those would read better.

## 7. Patent assessment

Row in `PATENTS.md`. Candidates: the stroke-skeleton family that shares point structure across weights and slant and emits per-stroke SVG for addressable animation; the monospaced twin made by squeezing skeletons rather than redrawing; pulse mode (a mark's own outline clipping lights whose places the font tool emits as CSS variables); the per-letter animation rule as a web and app rendering pipeline; the capsule renderer with built-in alpha mask (not built). Prior art to compare: Metafont and MetaPost (Knuth), parametric type systems (Prototypo, Spiro, Glyphs' smart components, Font Bureau's variable workflows), variable fonts (OpenType 1.8), COLRv1 and animated colour fonts, Lottie and Rive text animation, SVG-in-OpenType. Not filed. The page does not say patent pending.
