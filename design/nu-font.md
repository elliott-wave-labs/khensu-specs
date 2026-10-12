# ñü.Føňt: the house typeface

**Decided 12 October 2026. First release built and published the same day.** Shown as **ñü.Føňt** (o with stroke U+00F8, n with caron U+0148). Code, files and the page use `nu.font` (`/font` on khensu.nu, `tools/font/` in `khensu-site`); the font family name inside the files is `nu Font`, PostScript names `nuFont-<Style>`. Running text uses nu.font. Elliott typed the name both ways, ñũ.Føñt and ñü.Føňt, and closed with "this style is called ñü.Føňt", so that is the display form; the first form is listed here so the record shows the choice.

ñü.Føňt is the typeface for everything people see from khėnsu.ñü: the wordmark, headings, navigation, buttons and labels on every site, the apps when they reach it, and anything anyone else wants to set in it, because it is published free under the SIL Open Font License. It is also the home of the rule that letters can move: a wordmark is written into a page as paths, one per stroke, and any stroke can animate on its own. The dot on the ė, Elliott's E, is the first one that does.

## 1. What the first release is

| Item | Value |
| --- | --- |
| Glyphs | 160: basic Latin, digits, punctuation, the ligatures and letters the names need (æ œ ð ł ø and capitals), and precomposed letters for every mark the names use: ė ċ ñ ũ ẽ ü ë î ê ŵ š ř ě ů å ț and their relatives |
| Weights | Ultralight 100, Light 300, Medium 500, Bold 700, Heavy 800, Blackout 900 |
| Axes | `wght` 100 to 900; `slnt` 0 to −11, the italic |
| Masters | 12: the six weights, upright and slanted |
| Files | `nuFont-Variable.ttf` (220 KB) and `.woff2` (70 KB); twelve static TTFs of about 35 KB and WOFF2s of about 8 KB; `nufont.zip` with all of them; `nufont.json` with every measured figure |
| Metrics | 1000 units per em; cap height 700; x-height 350; descender −216 (350 ÷ φ); ascender 700 |
| Where | `khensu-site/tools/font/nufont.py` (the generator), `tools/font/build.sh` (build, copy, zip), `sites/khensu-nu/public/fonts/nufont/` (the files people download), `src/data/nufont-marks.ts` (generated inline wordmarks), `src/components/khensu/NuMark.astro` (the component that inlines them), `sites/khensu-nu/src/pages/font.astro` (the page) |

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

1. `nufont.py marks` writes each wordmark as SVG with one `<path>` per stroke. Diacritics carry a class: `mark dot`, `mark dieresis`, `mark tilde`, `mark caron`, `mark circumflex`, `mark ring`, `mark comma`, `mark cedilla`. Every path also carries `data-g` (glyph name) and `data-i` (letter index), so any letter can be addressed.
2. `NuMark.astro` inlines the SVG, adds the visually hidden text for readers and search, and, when asked, fills the letters with the house gradient (a `<linearGradient>` that repeats and slides over 9 s, the same period as `--aura-flow-dur`).
3. CSS does the motion. `.nf-word .mark.dot` scales 1 → 1.28 → 1 over 2.8 s with a soft glow, and its fill phases green → blue → purple over 9 s. Nothing else moves: the tilde on ñ and the dieresis on ü keep the fill of the letters. `prefers-reduced-motion` holds the dot still in the accent colour.
4. The ė is lowercase only. Ė exists in the font but has no animation.

The wordmarks in use: the hero title, the header brand and the footer brand on khensu.nu; the header brand on dev.khensu.nu; the hero on elliottwave.studio/khensu, which is generated from the khensu.nu homepage.

## 4. Where the font is used

| Role | Font |
| --- | --- |
| Headings h1–h3, the wordmark, header navigation, buttons, pills, chips, the product bar name, StatStrip figures | ñü.Føňt, through `--font-display` |
| Running text, forms, tables | Inter until ñü.Føňt has kerning and hinting (section 6). One line switches it: set `--font-sans` |
| Code | JetBrains Mono, unchanged |

The studio takes the same `global.css` (with its own accent) and the same components through `tools/sync-studio.sh`, which also copies the variable WOFF2 into the studio's `public/fonts/nufont/`.

## 5. Installing it

Published free under the SIL Open Font License 1.1 so it installs anywhere and ships inside any app. Mac: Font Book. Windows: right-click, Install. Linux: `~/.local/share/fonts` and `fc-cache -f`. iPhone and iPad: a font-installer app, or the TTF in an app bundle under `UIAppFonts`. Android: `res/font`. Web: one `@font-face` with `font-weight: 100 900` and `font-style: oblique 0deg 11deg`. khensu-apple bundles the variable TTF when it adopts the face.

## 6. Open, in order

1. **Kerning.** No pair spacing yet; the sites use tight letter-spacing on headings. First pairs: every name on the sites, `.ñ`, `ñü`, `kh`, `Fî`, `Bî`, digits.
2. **Hinting or a size-tuned master.** Then running text can switch.
3. **Written styles.** A hand-drawn italic and a sharpie style that stays close to the typed forms, as new masters on a `styl` axis or as sibling families.
4. **Mylar balloons.** Text as floating ñü.3d balloon shells (`design/nu-3d.md`), each glyph inflated from its skeleton with creases and highlights; part of the Templify emulation Elliott is recording.
5. **Emoji and animated emoji** in the same strokes and capsule ends, including Telegram-style animated emoji.
6. **Capsule renderer.** Glyphs drawn from their strokes at run time with a built-in alpha mask, tuned for the Neural Engine and TPUs, so the rounding "fades away" at any size without outline files.
7. **Per-letter presets.** Named cues (fade, pulse, drift, burst) chosen in CSS for any letter or mark, with the choreography of a whole wordmark in one data attribute.
8. **More scripts.** Greek and Cyrillic first; the fallback stack covers the rest meanwhile.

## 7. Patent assessment

Row in `PATENTS.md`. Candidates: the stroke-skeleton family that shares point structure across weights and slant and emits per-stroke SVG for addressable animation; the per-letter animation rule as a web and app rendering pipeline; the capsule renderer with built-in alpha mask (not built). Prior art to compare: Metafont and MetaPost (Knuth), parametric type systems (Prototypo, Spiro, Glyphs' smart components, Font Bureau's variable workflows), variable fonts (OpenType 1.8), COLRv1 and animated colour fonts, Lottie and Rive text animation, SVG-in-OpenType. Not filed. The page does not say patent pending.
