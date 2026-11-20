#!/usr/bin/env python3
"""Build the GoodCISO favicon set from the original brand artwork.

The mark itself is `goodciso-shield.png`, cut from the original 1024x1024
artwork in ~/projects/good-ciso-logo. This script places that artwork on a
navy tile and emits the three files a browser actually asks for.

Why a tile: the artwork's counter (the G-shaped hole) is knocked out to
TRANSPARENCY, because the header renders it on the page background. On a
transparent favicon the counter would show whatever the browser tab
happens to be, so the G would read differently on a light tab and a dark
one. The tile restores a fixed backdrop and reproduces the structure of
the favicon the site shipped for months - navy square, teal shield.

Why PNG and not SVG: the artwork is a JPEG-derived raster. The vector
trace (trace_logo.py) loses the G counter, so the original pixels are
what ship. See docs/BRAND.md.

Run it manually after changing the artwork; the outputs are committed
because CI has no imaging library:

    python3.12 make_favicons.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

BRAND = Path(__file__).resolve().parent / "assets/brand"
SHIELD = BRAND / "goodciso-shield.png"

NAVY = (3, 7, 18)  # #030712 - GoodCISO's navy, the established brand colour

# The tile's corner radius, as a fraction of its side. Matches the AWARE
# favicon's rx="7" on a 32-unit box (7/32 = 0.219) so the two brands read
# as the same family of mark without sharing a colour.
RADIUS = 0.219

# The shield's height as a fraction of the tile's side. The old live
# favicon drew the shield 24 units tall in a 32-unit box (0.75), so the
# mark's optical weight on the tab is unchanged.
SHIELD_HEIGHT = 0.75

TILE = 512


def tile(size: int = TILE) -> Image.Image:
    """The navy rounded tile the mark sits on."""
    t = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    radius = int(round(size * RADIUS))
    # Draw the rounded rect on its own layer so it can be alpha-composited
    # without the shield's own antialiased edges bleeding into it.
    plate = Image.new("RGBA", (size, size), NAVY + (255,))
    mask = Image.new("L", (size, size), 0)
    from PIL import ImageDraw

    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    t.paste(plate, (0, 0), mask)
    return t


def compose(size: int = TILE) -> Image.Image:
    """The navy tile with the original shield artwork centred on it."""
    out = tile(size)
    shield = Image.open(SHIELD).convert("RGBA")
    h = int(round(size * SHIELD_HEIGHT))
    w = int(round(shield.width * h / shield.height))
    shield = shield.resize((w, h), Image.LANCZOS)
    out.alpha_composite(shield, ((size - w) // 2, (size - h) // 2))
    return out


def main() -> None:
    master = compose()
    png = BRAND / "favicon-goodciso.png"
    master.save(png, optimize=True)
    print(f"  {png.name}: {master.size[0]}x{master.size[1]}  {png.stat().st_size} bytes")

    ico = BRAND / "favicon-goodciso.ico"
    master.save(ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"  {ico.name}: {ico.stat().st_size} bytes")

    # iOS composites transparency as black, so the apple-touch icon is
    # flattened onto its own opaque tile rather than left transparent.
    apple = Image.new("RGB", (180, 180), NAVY)
    icon = compose(180)
    apple.paste(icon, (0, 0), icon)
    apple_path = BRAND / "apple-touch-icon.png"
    apple.save(apple_path, optimize=True)
    print(f"  {apple_path.name}: 180x180  {apple_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
