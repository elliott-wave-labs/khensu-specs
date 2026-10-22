#!/usr/bin/env python3
# SPDX-License-Identifier: CC-BY-4.0
"""nu.eyes — the ÑÜ lens print tile.

One 512 px seamless tile, white marks on transparent: a staggered grid of the ÑÜ wordmark and a
four-point star. The web viewer, the app and the Blender renders all use this one file as the
mask of the mirror coating, so the print reads the same everywhere (design/nu-eyes.md §4).

  python3 print_tile.py --font inter-latin-800-normal.woff --out nu-print.png
"""
import argparse
import math

from PIL import Image, ImageDraw, ImageFont

SIZE = 512


def star(draw, cx, cy, r, inner=0.28):
    pts = []
    for i in range(8):
        a = math.pi / 2 + i * math.pi / 4
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy - rr * math.sin(a)))
    draw.polygon(pts, fill=(255, 255, 255, 255))


def mark(draw, font, cx, cy):
    box = draw.textbbox((0, 0), "ÑÜ", font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    draw.text((cx - w / 2 - box[0], cy - h / 2 - box[1]), "ÑÜ", font=font, fill=(255, 255, 255, 255))


def tile(font_path):
    # Draw at 2x on a 3x3 canvas so marks that cross an edge wrap seamlessly.
    s = SIZE * 2
    big = Image.new("RGBA", (s * 3, s * 3), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    font = ImageFont.truetype(font_path, int(s * 0.25))
    for ox in range(3):
        for oy in range(3):
            bx, by = ox * s, oy * s
            mark(d, font, bx + s * 0.25, by + s * 0.25)
            mark(d, font, bx + s * 0.75, by + s * 0.75)
            star(d, bx + s * 0.75, by + s * 0.25, s * 0.085)
            star(d, bx + s * 0.25, by + s * 0.75, s * 0.085)
    return big.crop((s, s, 2 * s, 2 * s)).resize((SIZE, SIZE), Image.LANCZOS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", required=True)
    ap.add_argument("--out", default="nu-print.png")
    a = ap.parse_args()
    tile(a.font).save(a.out, optimize=True)
    print(a.out)
