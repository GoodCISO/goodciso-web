#!/usr/bin/env python3
"""Generate the brand assets that the sites reference but that do not exist.

Every one of these was a live 404 on 2026-11-20, checked against production:

    /favicon.ico          404
    /apple-touch-icon.png 404
    /og.png                404   (no og:image at all in the markup)

A browser tab falls back to a default globe, an iOS home screen falls back
to a screenshot of the page, and a shared link renders with no card at all.
Those are not subtle defects: they are the three surfaces where a brand is
recognised before a word is read.

The assets are generated from the SAME source as the rest of the brand —
the original GoodCISO artwork for the corporate site, the AWARE shield SVG
for the product sites — so they cannot drift from the mark that already
ships.

Two brands, so two sets:

    corporate   the ORIGINAL GoodCISO mark: teal shield with a G-shaped
                counter and an amber dot, cut from
                ~/projects/good-ciso-logo/good-ciso-logo.png
    aware       the AWARE shield-and-checkmark, from
                assets/brand/favicon-aware.svg

The AWARE SVG is rasterised with headless Chrome because it is vector
art: the SVG must become a real multi-resolution .ico and a 180px PNG, and
no pure-Python rasteriser is available in CI (which installs no packages).

    python3.12 make_brand_assets.py

Requires: Pillow. Headless Chrome is required only for the AWARE set.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent.resolve()
BRAND_DIR = ROOT / "assets/brand"

# The brand palette. GoodCISO's colours come from the original artwork's
# README and the artwork itself; AWARE's are its own.
GOODCISO_NAVY = (3, 7, 18)        # #030712
GOODCISO_TEAL = (0, 168, 150)     # #00A896
GOODCISO_AMBER = (245, 166, 35)   # #F5A623
AWARE_MIDNIGHT = (11, 18, 32)     # #0B1220
AWARE_GREEN = (34, 197, 94)       # #22C55E

# The Inter variable font the sites load. Fetched once and cached beside
# the script so the build does not need the network on every run.
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"
FONT_PATH = BRAND_DIR / "Inter.ttf"


def chrome_binary() -> str | None:
    for p in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        shutil.which("chromium") or "",
        shutil.which("google-chrome") or "",
    ):
        if p and Path(p).exists():
            return p
    return None


def rasterise_svg(svg: Path, size: int) -> Image.Image:
    """Rasterise an SVG at an exact size using headless Chrome."""
    chrome = chrome_binary()
    if not chrome:
        raise SystemExit(
            "[brand] headless Chrome is required to rasterise the AWARE mark. "
            "Install Google Chrome, or render the SVG by hand."
        )
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        page = td / "page.html"
        page.write_text(
            "<!doctype html><html><head><style>"
            "html,body{margin:0;padding:0;background:transparent}"
            f"img{{display:block;width:{size}px;height:{size}px}}"
            "</style></head><body>"
            f'<img src="{svg.resolve().as_uri()}">'
            "</body></html>",
            encoding="utf-8",
        )
        out = td / "shot.png"
        subprocess.run(
            [
                chrome, "--headless", "--disable-gpu", "--no-sandbox",
                "--hide-scrollbars", "--default-background-color=00000000",
                f"--screenshot={out}", f"--window-size={size},{size}",
                page.resolve().as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        return Image.open(out).convert("RGBA")


def load_font(size: int, weight: int = 500) -> ImageFont.FreeTypeFont:
    """Load Inter at a weight, from the cached file or by fetching it once.

    Inter ships as a VARIABLE font. PIL ignores the weight unless the
    variation axes are set explicitly, so a "bold" wordmark silently
    renders at Regular — which is how the wordmark lost the weight
    difference between "Good" and "CISO" on the first pass.
    """
    if not FONT_PATH.exists():
        import urllib.request

        print(f"[brand] fetching {FONT_PATH.name} ...")
        with urllib.request.urlopen(FONT_URL, timeout=120) as r:
            FONT_PATH.write_bytes(r.read())
    font = ImageFont.truetype(FONT_PATH, size)
    try:
        font.set_variation_by_axes([32, weight])
    except Exception:
        # A static fallback font has no axes; the name still applies.
        pass
    return font


def corporate_mark(size: int) -> Image.Image:
    """The corporate mark on the corporate background, square, at `size`.

    The original artwork is a teal shield with a G-shaped counter and an
    amber dot on white. iOS and .ico both need an opaque square, so the
    white is replaced with the brand navy rather than left transparent:
    a transparent favicon on a light browser chrome is nearly invisible.
    """
    shield = Image.open(BRAND_DIR / "goodciso-shield.png").convert("RGBA")
    canvas = Image.new("RGBA", (size, size), GOODCISO_NAVY + (255,))
    # Fit the shield into the square with a margin, preserving its aspect.
    margin = int(size * 0.14)
    inner = size - margin * 2
    scale = inner / max(shield.size)
    w, h = max(1, int(shield.size[0] * scale)), max(1, int(shield.size[1] * scale))
    resized = shield.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(resized, ((size - w) // 2, (size - h) // 2))
    return canvas


def aware_mark(size: int) -> Image.Image:
    """The AWARE mark, rasterised from its own SVG."""
    return rasterise_svg(BRAND_DIR / "favicon-aware.svg", size)


def write_ico(image: Image.Image, path: Path) -> None:
    """Write a real multi-resolution .ico (16/32/48).

    PIL's ICO writer takes ONE source image and resizes it itself — the
    `append_images` argument is silently ignored, which produced an .ico
    containing only the 16px frame. A 16px-only .ico is what a browser
    falls back to when it cannot find an SVG, so it is the size that
    matters most and the one most often missing.
    """
    image.save(path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])


def apple_touch(image: Image.Image, path: Path) -> None:
    """Write the 180x180 apple-touch-icon.

    iOS does NOT round the corners or mask transparency — it draws the
    icon as a square and applies its own mask. So the icon must already
    be a full-bleed square with an opaque background.
    """
    image.resize((180, 180), Image.LANCZOS).save(path, format="PNG")


def social_card(
    mark: Image.Image,
    wordmark: str,
    tagline: str,
    domain: str,
    path: Path,
    bg: tuple[int, int, int],
    fg: tuple[int, int, int],
    accent: tuple[int, int, int],
) -> None:
    """A 1200x630 Open Graph card.

    The mark is the brand's own, the wordmark is set in the brand's type,
    and the tagline is the site's own line. The card is a brand surface,
    so it is generated from the same palette as the site rather than
    being a screenshot of one.
    """
    W, H = 1200, 630
    card = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(card)

    # A quiet brand wash down the right-hand side, using the accent at
    # low opacity so the card has depth without a second colour.
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wash)
    wd.ellipse((W - 460, -260, W + 260, 460), fill=accent + (26,))
    card = Image.alpha_composite(card.convert("RGBA"), wash).convert("RGB")
    d = ImageDraw.Draw(card)

    margin = 84

    # The mark, top-left, on its own brand background.
    mark_size = 108
    badge = Image.new("RGBA", (mark_size, mark_size), bg + (255,))
    m = mark.resize((mark_size, mark_size), Image.LANCZOS)
    badge.alpha_composite(m)
    card.paste(badge.convert("RGB"), (margin, margin), badge)
    d = ImageDraw.Draw(card)

    # The wordmark, set large. "Good" heavier, "CISO" in caps, matching
    # the artwork and the header lockup: the header renders "Good" at
    # weight 700 and "CISO" at 600.
    if wordmark == "Good CISO":
        good_font = load_font(82, weight=700)
        ciso_font = load_font(82, weight=600)
        w_good = d.textlength("Good", font=good_font)
        y = margin + 172
        d.text((margin, y), "Good", font=good_font, fill=fg)
        d.text((margin + w_good + 20, y), "CISO", font=ciso_font, fill=fg)
    else:
        big = load_font(82, weight=600)
        d.text((margin, margin + 172), wordmark, font=big, fill=fg)

    # The tagline, in the muted tone of the same family.
    small = load_font(34, weight=400)
    d.text((margin, margin + 292), tagline, font=small, fill=fg)

    # The domain, small and quiet, bottom-left.
    tiny = load_font(26, weight=400)
    d.text((margin, H - margin - 34), domain, font=tiny, fill=fg)

    card.save(path, format="PNG")


def main() -> int:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    out = BRAND_DIR / "generated"
    out.mkdir(exist_ok=True)

    corp = corporate_mark(512)
    corp.save(out / "corporate-mark-512.png")
    write_ico(corp, out / "favicon.ico")
    apple_touch(corp, out / "apple-touch-icon.png")
    social_card(
        corporate_mark(512),
        "Good CISO",
        "Enterprise cybersecurity and AI governance.",
        "goodciso.org",
        out / "og-corporate.png",
        GOODCISO_NAVY,
        (255, 255, 255),
        GOODCISO_TEAL,
    )

    aware = aware_mark(512)
    aware.save(out / "aware-mark-512.png")
    write_ico(aware, out / "favicon-aware.ico")
    apple_touch(aware, out / "apple-touch-icon-aware.png")
    social_card(
        aware,
        "AWARE",
        "The security control plane for autonomous AI agents.",
        "aware.goodciso.org",
        out / "og-aware.png",
        AWARE_MIDNIGHT,
        (226, 232, 240),
        AWARE_GREEN,
    )

    for f in sorted(out.iterdir()):
        print(f"[brand] {f.relative_to(ROOT)}  {f.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
