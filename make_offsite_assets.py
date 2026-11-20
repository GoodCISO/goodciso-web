#!/usr/bin/env python3
"""Generate the brand assets for the OFF-REPO brand surfaces.

The website's brand surfaces live in `assets/brand/` and are guarded in CI
(`qa.py`). The surfaces below are NOT in the repository and CI cannot see
them, so they drift — and did: on 2026-11-20 the LinkedIn company avatar was
an unsaturated greyscale photo and the cover was ChangTech's sunset stock
image, served from a CDN file literally named `changtech_consultants_cover`.

They are generated here from the SAME committed sources the website uses,
so an off-repo surface cannot drift from the mark that ships:

    corporate mark  assets/brand/goodciso-shield.png (cut from the original
                    artwork by extract_logo.py) on the corporate navy tile
                    (BRAND.md §4 rule 3)
    corporate type  assets/brand/Inter.ttf
    wordmark        the site's own lockup: "Good" at weight 700, "CISO" in
                    caps at weight 600 (build.py, GOODCISO_WORDMARK)

Outputs, in assets/brand/generated/:

    linkedin-avatar-goodciso.png   800x800    LinkedIn company logo
    linkedin-cover-goodciso.png   1584x396    LinkedIn company banner

    python3.12 make_offsite_assets.py

Requires: Pillow. Nothing here touches a website — these are files an
operator uploads by hand to a third-party surface. The script only makes
sure the file they upload is the brand's own mark, cut from the same source
the site ships, rather than a screenshot or a redrawing.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

# The shared brand helpers live with the website's own generator, so the
# mark, the type and the tile are defined in exactly one place.
from make_brand_assets import (  # noqa: E402
    GOODCISO_NAVY,
    GOODCISO_TEAL,
    load_font,
)

ROOT = Path(__file__).parent.resolve()
BRAND = ROOT / "assets/brand"
OUT = BRAND / "generated"

WHITE = (255, 255, 255)
SLATE = (148, 163, 184)  # #94A3B8

# The corporate promise, the home page's own h1 (apps/other.py).
TAGLINE = "Securing the enterprise in the age of autonomous AI."


def shield_rgba() -> Image.Image:
    """The corporate mark, cut from the original artwork."""
    return Image.open(BRAND / "goodciso-shield.png").convert("RGBA")


def corporate_tile(size: int, margin_ratio: float = 0.14) -> Image.Image:
    """The corporate mark on the corporate navy tile (BRAND.md rule 3).

    The artwork's counter is knocked out to transparency for the header, so
    a transparent avatar would show the G against whatever the platform
    paints behind it. The navy tile fixes the backdrop.
    """
    shield = shield_rgba()
    canvas = Image.new("RGBA", (size, size), GOODCISO_NAVY + (255,))
    margin = int(size * margin_ratio)
    inner = size - margin * 2
    scale = inner / max(shield.size)
    w, h = max(1, int(shield.size[0] * scale)), max(1, int(shield.size[1] * scale))
    canvas.alpha_composite(
        shield.resize((w, h), Image.LANCZOS), ((size - w) // 2, (size - h) // 2)
    )
    return canvas


def wordmark(draw: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    """The corporate wordmark: "Good" bold, "CISO" in caps.

    This is the site's own lockup (build.py GOODCISO_WORDMARK): "Good" at
    weight 700 and "CISO" at 600, both caps-preserving. It is NOT "GOOD
    CISO" and it does NOT carry a period dot — the amber dot belongs to
    the shield, and putting it after the wordmark invents a mark that does
    not exist.
    """
    good = load_font(size, 700)
    ciso = load_font(size, 600)
    w_good = draw.textlength("Good", font=good)
    draw.text((x, y), "Good", font=good, fill=WHITE + (255,))
    draw.text((x + w_good + int(size * 0.28), y), "CISO", font=ciso, fill=WHITE + (255,))


def build_avatar() -> Path:
    out = OUT / "linkedin-avatar-goodciso.png"
    corporate_tile(800).convert("RGB").save(out, "PNG")
    return out


def build_cover() -> Path:
    W, H = 1584, 396
    card = Image.new("RGB", (W, H), GOODCISO_NAVY)
    d = ImageDraw.Draw(card)

    # A quiet teal wash on the right, so the banner has depth without
    # introducing a second colour.
    wash = Image.new("RGB", (520, H), (6, 26, 34))
    mask = Image.new("L", (520, H))
    md = ImageDraw.Draw(mask)
    for i in range(520):
        md.line((i, 0, i, H), fill=int(150 * (i / 520)))
    card.paste(wash, (W - 520, 0), mask)

    # The mark, on the corporate navy ground, at the left third.
    shield = shield_rgba()
    s = 132
    sc = s / max(shield.size)
    sw, sh = int(shield.size[0] * sc), int(shield.size[1] * sc)
    shield_r = shield.resize((sw, sh), Image.LANCZOS)
    card.paste(shield_r, (96, (H - sh) // 2), shield_r)

    x = 96 + sw + 48
    wordmark(d, x, 132, 56)
    d.text((x, 212), TAGLINE, font=load_font(24, 400), fill=SLATE + (255,))

    out = OUT / "linkedin-cover-goodciso.png"
    card.save(out, "PNG")
    return out


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for p in (build_avatar(), build_cover()):
        print("wrote", p, Image.open(p).size)
    # The palette is imported from the shared brand module so a change to
    # the corporate colours cannot silently miss this generator.
    assert GOODCISO_TEAL == (0, 168, 150), GOODCISO_TEAL
