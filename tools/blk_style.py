#!/usr/bin/env python3
"""
BLK.SYSTEM - the shared edge.

Every surface in the profile is the same card, and its border is drawn, not
computed: a rounded rectangle that wobbles like a hand traced it around a
ruler. One implementation feeds both output formats - the PNG banners
(Pillow) and the section cards (SVG) - so the edge cannot drift between them.

Two ideas make it read as hand-drawn rather than as noise:

  * the wobble is LOW frequency. Independent jitter per point gives a fuzzy,
    digital-looking line; a smooth offset resampled every few dozen pixels
    gives the slow drift of a hand that cannot hold a straight line.
  * it is drawn more than once. A physical pen never lands twice in the same
    place, so each pass gets its own offsets and a slightly lower opacity.

The outline is also the card's silhouette, not just a stroke on top of a
geometric shape - so the corners themselves are organic.
"""

import math
import random


def rounded_rect(w, h, radius, step=7.0):
    """Evenly-spaced perimeter points of a rounded rectangle, clockwise."""
    r = min(radius, w / 2, h / 2)
    pts = []

    def line(x0, y0, x1, y1):
        dist = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(dist / step))
        for i in range(n):
            f = i / n
            pts.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))

    def arc(cx, cy, a0, a1):
        n = max(2, int(abs(a1 - a0) * r / step))
        for i in range(n):
            a = a0 + (a1 - a0) * i / n
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))

    line(r, 0, w - r, 0)
    arc(w - r, r, -math.pi / 2, 0)
    line(w, r, w, h - r)
    arc(w - r, h - r, 0, math.pi / 2)
    line(w - r, h, r, h)
    arc(r, h - r, math.pi / 2, math.pi)
    line(0, h - r, 0, r)
    arc(r, r, math.pi, math.pi * 1.5)
    return pts


def _drift(n, rng, amplitude, wavelength):
    """
    A smooth, seamless offset series around a closed loop.

    Control points every `wavelength` samples, cosine-interpolated between
    them, and the loop closes on itself so the start and end of the border
    meet without a seam.
    """
    count = max(3, int(round(n / wavelength)))
    knots = [rng.gauss(0, amplitude) for _ in range(count)]
    out = []
    for i in range(n):
        pos = i * count / n
        a, f = int(pos), pos - int(pos)
        b = (a + 1) % count
        smooth = (1 - math.cos(f * math.pi)) / 2
        out.append(knots[a] * (1 - smooth) + knots[b] * smooth)
    return out


def _normals(pts):
    out = []
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy) or 1.0
        out.append((dy / length, -dx / length))
    return out


def sketch(w, h, radius, seed, passes=3, amplitude=3.4, wavelength=26.0,
           step=7.0):
    """
    Hand-drawn outline of a rounded rectangle.

    Returns one point list per pass, each closed. Pass 0 is the cleanest and
    doubles as the card's silhouette; later passes drift further and are meant
    to be stroked more faintly on top.
    """
    base = rounded_rect(w, h, radius, step)
    norms = _normals(base)
    n = len(base)
    rng = random.Random(seed)

    out = []
    for p in range(passes):
        amp = amplitude * (1.0 + 0.35 * p)
        offsets = _drift(n, rng, amp, wavelength)
        grit = amplitude * 0.16
        pts = [(x + nx * offsets[i] + rng.gauss(0, grit),
                y + ny * offsets[i] + rng.gauss(0, grit))
               for i, ((x, y), (nx, ny)) in enumerate(zip(base, norms))]
        pts.append(pts[0])
        out.append(pts)
    return out


def svg_path(pts, precision=1):
    fmt = "%." + str(precision) + "f"
    head = "M" + fmt % pts[0][0] + " " + fmt % pts[0][1]
    body = "".join("L" + fmt % x + " " + fmt % y for x, y in pts[1:])
    return head + body + "Z"
