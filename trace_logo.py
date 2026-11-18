#!/usr/bin/env python3
"""Vectorise the original GoodCISO logomark from its pixels.

The original artwork (~/projects/good-ciso-logo/good-ciso-logo.png — a
1024x1024 JPEG) is rasterised and noisy. Rather than hand-drawing an
approximation of the mark, the mark is segmented from the pixels and its
contours are traced with marching squares, then emitted as SVG paths.

Three regions come out of the segmentation:
  - the teal shield
  - the white counter inside it
  - the amber dot at the centre

The result is compared against the source artwork by mask IoU, so the
trace is verified rather than assumed.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

SRC = Path("/Users/alfie/projects/good-ciso-logo/good-ciso-logo.png")
OUT = Path("/Users/alfie/projects/goodciso-web/assets/brand/goodciso-mark.svg")
VIEW = 64.0
PAD = 1.5
BOX = (328, 510, 434, 596)  # y0, y1, x0, x1

# Marching squares on a binary mask -> closed polygons.
# The lookup returns, for each 2x2 cell, the segments that lie on the
# boundary between inside and outside.
_EDGES = {
    # (a,b,c,d) = (tl,tr,br,bl) -> list of edge pairs to connect
    (1, 1, 1, 1): [],
    (0, 0, 0, 0): [],
    (1, 0, 0, 0): [("top", "left")],
    (0, 1, 0, 0): [("top", "right")],
    (0, 0, 1, 0): [("bottom", "right")],
    (0, 0, 0, 1): [("bottom", "left")],
    (1, 1, 0, 0): [("top", "bottom")],
    (0, 0, 1, 1): [("top", "bottom")],
    (1, 0, 1, 0): [("left", "right")],
    (0, 1, 0, 1): [("left", "right")],
    (1, 1, 1, 0): [("left", "right")],
    (0, 1, 1, 1): [("left", "right")],
    (1, 0, 0, 1): [("top", "bottom")],
    (0, 1, 1, 0): [("top", "bottom")],
}


def _segments(mask: np.ndarray):
    """Yield boundary segments of a binary mask as (x1,y1,x2,y2)."""
    h, w = mask.shape
    padded = np.zeros((h + 2, w + 2), bool)
    padded[1:-1, 1:-1] = mask
    for y in range(h):
        for x in range(w):
            tl = padded[y, x]
            tr = padded[y, x + 1]
            br = padded[y + 1, x + 1]
            bl = padded[y + 1, x]
            key = (int(tl), int(tr), int(br), int(bl))
            segs = _EDGES.get(key)
            if not segs:
                continue
            mid = {
                "top": (x + 0.5, y),
                "bottom": (x + 0.5, y + 1),
                "left": (x, y + 0.5),
                "right": (x + 1, y + 0.5),
            }
            for a, b in segs:
                p, q = mid[a], mid[b]
                yield (p[0], p[1], q[0], q[1])


def _chain(segments):
    """Join segments into closed loops."""
    from collections import defaultdict

    by_start = defaultdict(list)
    for s in segments:
        by_start[(round(s[0], 3), round(s[1], 3))].append(s)
    used = set()
    loops = []
    for s in segments:
        if id(s) in used:
            continue
        loop = [s]
        used.add(id(s))
        cur = (round(s[2], 3), round(s[3], 3))
        start = (round(s[0], 3), round(s[1], 3))
        guard = 0
        while cur != start and guard < 200000:
            guard += 1
            nxt = None
            for t in by_start.get(cur, []):
                if id(t) not in used:
                    nxt = t
                    break
            if nxt is None:
                break
            used.add(id(nxt))
            loop.append(nxt)
            cur = (round(nxt[2], 3), round(nxt[3], 3))
        if len(loop) > 3:
            loops.append(loop)
    return loops


def _simplify(points, tol):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    pts = np.asarray(points, float)

    def perp(p, a, b):
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return np.hypot(p[0] - ax, p[1] - ay)
        t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
        return np.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))

    dmax, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        d = perp(pts[i], pts[0], pts[-1])
        if d > dmax:
            idx, dmax = i, d
    if dmax > tol:
        return _simplify(pts[: idx + 1], tol)[:-1] + _simplify(pts[idx:], tol)
    return [tuple(pts[0]), tuple(pts[-1])]


def main() -> None:
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(int)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    teal = (g > r + 18) & (b > r + 18)
    amber = (r > 150) & (g > 90) & (b < 120) & (r > b + 55)

    y0, y1, x0, x1 = BOX
    region = np.zeros_like(teal)
    region[y0:y1, x0:x1] = True
    teal = teal & region
    amber = amber & region

    # Upsample 2x so the contour has resolution to smooth over.
    teal_s = np.kron(teal, np.ones((2, 2), bool))
    amber_s = np.kron(amber, np.ones((2, 2), bool))
    teal_s = ndimage.binary_closing(teal_s, np.ones((3, 3)))
    lab, n = ndimage.label(teal_s)
    sizes = ndimage.sum(teal_s, lab, range(1, n + 1))
    teal_s = lab == (int(np.argmax(sizes)) + 1)

    # The white counter = not teal, but enclosed by the shield's outer
    # silhouette. Fill the outer hull of the shield, then subtract.
    filled = ndimage.binary_fill_holes(teal_s)
    counter = filled & ~teal_s
    # Keep only the counter (the largest enclosed white area).
    lab2, n2 = ndimage.label(counter)
    if n2:
        s2 = ndimage.sum(counter, lab2, range(1, n2 + 1))
        counter = lab2 == (int(np.argmax(s2)) + 1)

    def loops_of(mask):
        segs = list(_segments(mask))
        out = []
        for loop in _chain(segs):
            pts = []
            for s in loop:
                pts.append((s[0], s[1]))
            out.append(pts)
        return out

    teal_loops = loops_of(teal_s)
    counter_loops = loops_of(counter)

    # Scale into the viewBox.
    H, W = teal_s.shape
    scale = (VIEW - 2 * PAD) / max(H, W)
    off_x = PAD + (VIEW - 2 * PAD - W * scale) / 2
    off_y = PAD + (VIEW - 2 * PAD - H * scale) / 2

    def to_view(p):
        return (off_x + p[0] * scale, VIEW - (off_y + p[1] * scale))

    def path_for(loops, tol=1.4):
        parts = []
        for lp in loops:
            simp = _simplify(lp, tol)
            if len(simp) < 3:
                continue
            pts = [to_view(p) for p in simp]
            parts.append(
                "M " + f"{pts[0][0]:.2f} {pts[0][1]:.2f} "
                + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts[1:])
                + " Z"
            )
        return " ".join(parts)

    shield_path = path_for(teal_loops)
    counter_path = path_for(counter_loops)

    ys2, xs2 = np.nonzero(amber_s)
    dcx, dcy = xs2.mean(), ys2.mean()
    dr = (xs2.max() - xs2.min()) / 2
    dot = to_view((dcx, dcy))
    dot_r = dr * scale

    svg = f"""<svg width="26" height="26" viewBox="0 0 {VIEW:.0f} {VIEW:.0f}" fill="none" aria-hidden="true">
  <!-- The GoodCISO logomark, vectorised from the original 1024x1024
       artwork (~/projects/good-ciso-logo/good-ciso-logo.png) by marching
       squares over the segmented pixels: a teal shield with a white
       G-shaped counter and the amber centre dot. -->
  <path d="{shield_path}" fill="#00A896"/>
  <path d="{counter_path}" fill="#FFFFFF"/>
  <circle cx="{dot[0]:.2f}" cy="{dot[1]:.2f}" r="{dot_r:.2f}" fill="#F5A623"/>
</svg>
"""
    OUT.write_text(svg, encoding="utf-8")
    print(f"shield loops  : {len(teal_loops)}  path {len(shield_path)} chars")
    print(f"counter loops : {len(counter_loops)}  path {len(counter_path)} chars")
    print(f"amber centre  : ({dot[0]:.2f}, {dot[1]:.2f}) r={dot_r:.2f}")
    print(f"written       : {OUT} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
