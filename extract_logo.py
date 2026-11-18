#!/usr/bin/env python3
"""Cut the GoodCISO brand assets out of the original artwork.

The original mark lives in ~/projects/good-ciso-logo/good-ciso-logo.png —
a 1024x1024 JPEG despite the .png extension. It contains the stacked logo:
the teal shield with its amber centre dot, and the "Good CISO" wordmark
below it in dark navy.

Two assets are produced from it, both cropped from the original pixels so
the mark on the site is the original mark rather than a redrawing of it:

  goodciso-logo.png    the whole stacked logo, shield and wordmark
  goodciso-shield.png  the shield alone, for the header and favicon

The white background is knocked out to transparency, and both are
palette-quantised, because they render at 26-32px and a full-colour
version of a 1024px source would be an unreasonable weight for a header.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = Path("/Users/alfie/projects/good-ciso-logo/good-ciso-logo.png")
DEST = Path("/Users/alfie/projects/goodciso-web/assets/brand")

# Regions of the source artwork, in source pixels.
#   logo:   the shield plus the wordmark beneath it
#   shield: the shield alone
LOGO_BOX = (320, 610, 260, 730)
SHIELD_BOX = (320, 510, 430, 600)

WHITE_CUT = 238


def masks(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    teal = (g > r + 18) & (b > r + 18)
    amber = (r > 150) & (g > 90) & (b < 120) & (r > b + 55)
    return teal, amber


def cut(im: Image.Image, a: np.ndarray, box: tuple[int, int, int, int], name: str) -> Image.Image:
    y0, y1, x0, x1 = box
    region = np.zeros(a.shape[:2], bool)
    region[y0:y1, x0:x1] = True
    teal, amber = masks(a)
    ink = (teal | amber) & region
    # The wordmark is navy, not teal, so it is found by darkness.
    dark = a.sum(axis=2) < 620
    ink = ink | (dark & region)

    ys, xs = np.nonzero(ink)
    crop = im.crop(
        (
            int(xs.min()) - 3,
            int(ys.min()) - 3,
            int(xs.max()) + 4,
            int(ys.max()) + 4,
        )
    )
    ca = np.asarray(crop).astype(int)
    white = (ca[:, :, 0] > WHITE_CUT) & (ca[:, :, 1] > WHITE_CUT) & (ca[:, :, 2] > WHITE_CUT)
    out = np.dstack([np.asarray(crop), np.where(white, 0, 255).astype(np.uint8)])
    rgba = Image.fromarray(out, "RGBA")
    print(f"  {name}: source region {crop.size}")
    return rgba


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(int)

    logo = cut(im, a, LOGO_BOX, "stacked logo")
    shield = cut(im, a, SHIELD_BOX, "shield")

    # The header renders the shield at 30px tall; the stacked logo is used
    # for the social/OG image. Both are cut at a size that stays crisp at
    # 2x.
    for src, name, width in (
        (logo, "goodciso-logo.png", 160),
        (shield, "goodciso-shield.png", 64),
    ):
        out = src.resize((width, int(width * src.size[1] / src.size[0])), Image.LANCZOS)
        out = out.quantize(colors=32, method=Image.FASTOCTREE)
        path = DEST / name
        out.save(path, optimize=True)
        print(f"  {name}: {out.size[0]}x{out.size[1]}  {os.path.getsize(path)} bytes")


if __name__ == "__main__":
    main()
