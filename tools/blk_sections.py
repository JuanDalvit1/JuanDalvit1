#!/usr/bin/env python3
"""
BLK.SYSTEM - section headers.

One pattern, repeated for every section of the profile - a softly rounded
card that holds everything it needs:

    .------------------------------------------------------------------.
    |  [index]  [FLAT TITLE]                                   [crown]  |
    |  [lowercase mono subtitle]                                        |
    `------------------------------------------------------------------'

Nothing floats outside the card. Order in the typography, the entity's mark
closing the line, the whole thing sitting on the page like a key you could
press.

The crown is the drawing itself, embedded as a data URI - a README image is
served through GitHub's proxy, so a relative <image href> inside the SVG would
never resolve. Run tools/blk_images.py first to produce it.

Usage    python tools/blk_sections.py
Outputs  assets/sections/<slug>-{light,dark}.svg
"""

import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEMES = {
    "light": {"paper": "#f4f2ee", "ink": "#101010",
              "sub": "#57534c", "border": "#1c1a17"},
    "dark": {"paper": "#0a0a0a", "ink": "#ece8e0",
             "sub": "#8d887f", "border": "#cfc9c0"},
}

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

W, H = 1280, 150
RADIUS = 24          # ~16px once GitHub scales the card to column width
STROKE = 3
EDGE_INSET = 6       # room for the wobble to swing without clipping
CROWN_H = 46

def card(theme, seed):
    """The hand-drawn card: organic silhouette filled, then traced in ink."""
    t = THEMES[theme]
    passes = blk_style.sketch(W - EDGE_INSET * 2, H - EDGE_INSET * 2,
                              RADIUS, seed, passes=3)
    shifted = [[(x + EDGE_INSET, y + EDGE_INSET) for x, y in p]
               for p in passes]

    out = ['<path d="%s" fill="%s"/>'
           % (blk_style.svg_path(shifted[0]), t["paper"])]
    for i, pts in enumerate(shifted):
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                   'stroke-linejoin="round" stroke-linecap="round" '
                   'opacity="%.2f"/>'
                   % (blk_style.svg_path(pts), t["border"],
                      max(1, STROKE - i), 0.98 - 0.26 * i))
    return "".join(out)


SECTIONS = [
    ("01", "WHAT I BUILD",
     "ai systems, automation, and the platforms that keep them running",
     "manifesto"),
    ("02", "TECH STACK",
     "languages, ai, backend, data, frontend, infrastructure",
     "stack"),
    ("03", "GITHUB STATS",
     "the numbers, unedited",
     "signals"),
    ("04", "CONTRIBUTION GRAPH",
     "the void devours every commit / rebuilt every 12h",
     "serpent"),
    ("05", "GET IN TOUCH",
     "open channels",
     "contact"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def crown_uri(theme):
    path = os.path.join(ROOT, "assets", "blk", "crown-%s.png" % theme)
    if not os.path.exists(path):
        sys.exit("missing %s - run tools/blk_images.py first"
                 % os.path.relpath(path, ROOT))
    with open(path, "rb") as fh:
        return ("data:image/png;base64,"
                + base64.b64encode(fh.read()).decode("ascii"))


def text(x, y, s, size, fill, weight=900, spacing=0, family=FONT, opacity=1.0):
    return ('<text x="%d" y="%d" font-family="%s" font-size="%d" '
            'font-weight="%d" letter-spacing="%s" fill="%s" opacity="%s">'
            "%s</text>") % (x, y, family, size, weight, spacing, fill,
                            opacity, esc(s))


def build(index, title, subtitle, theme, crown_data, crown_w, seed):
    t = THEMES[theme]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 %(w)d %(h)d" width="%(w)d" height="%(h)d" role="img" '
        'aria-label="%(alt)s">'
        "%(card)s%(index)s%(title)s%(subtitle)s"
        '<image x="%(crown_x)d" y="%(crown_y)d" width="%(crown_w)d" '
        'height="%(crown_h)d" xlink:href="%(crown)s"/>'
        "</svg>"
    ) % {
        "w": W, "h": H,
        "alt": "%s %s - %s" % (index, title, subtitle),
        "card": card(theme, seed),
        "index": text(48, 74, index, 32, t["sub"], 900, 2, MONO, 0.5),
        "title": text(118, 76, title, 38, t["ink"], 900, 5),
        "subtitle": text(120, 114, subtitle, 16, t["sub"], 400, 1, MONO, 0.85),
        "crown_x": W - 50 - crown_w,
        "crown_y": (H - CROWN_H) // 2,
        "crown_w": crown_w, "crown_h": CROWN_H,
        "crown": crown_data,
    }


def main():
    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)

    for theme in THEMES:
        data = crown_uri(theme)
        # crown-*.png is written at a fixed height by blk_images.py;
        # read its real aspect so the mark is never stretched
        from PIL import Image
        with Image.open(os.path.join(ROOT, "assets", "blk",
                                     "crown-%s.png" % theme)) as im:
            crown_w = round(im.width * CROWN_H / im.height)

        for seed, (index, title, subtitle, slug) in enumerate(SECTIONS):
            markup = build(index, title, subtitle, theme, data, crown_w,
                           seed=101 + seed * 7)
            name = "%s-%s.svg" % (slug, theme)
            with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
                fh.write(markup)
            print("assets/sections/%-26s %6.1f KB"
                  % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
