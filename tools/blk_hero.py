#!/usr/bin/env python3
"""
BLK.SYSTEM - the living hero.

The banner joins the system it started: the PNG is now a flat printing
plate, and this wrapper puts the same living card around it that every
other section has - the scribbled border undulating through its three
layers - plus the glitch, applied to the plate itself: twice a cycle the
whole print slips, two ink ghosts split off and snap back. A press
misregistration on the artwork, monochrome by nature.

The plate is embedded once and referenced three times with <use>, so the
ghosts cost bytes only for their class names, not another copy of the
image.

Run tools/blk_images.py first - this consumes hero-{theme}.png.

Usage    python tools/blk_hero.py
Outputs  assets/blk/hero-{light,dark}.svg
"""

import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLK = os.path.join(ROOT, "assets", "blk")

W, H = 1500, 500
RADIUS = 26
STROKE = 4

# The plate sits this far inside the card. The border's drift swings about
# 15px from the edge at its widest; 20 keeps the scribble from ever being
# covered by the plate, and the paper margin reads as a mat around a print.
PLATE_INSET = 20
PLATE_RADIUS = 16

THEMES = {
    "light": {"paper": "#f4f2ee", "border": "#1c1a17"},
    "dark": {"paper": "#0a0a0a", "border": "#cfc9c0"},
}


def build(theme):
    t = THEMES[theme]
    png = os.path.join(BLK, "hero-%s.png" % theme)
    if not os.path.exists(png):
        sys.exit("missing %s - run tools/blk_images.py first"
                 % os.path.relpath(png, ROOT))
    with open(png, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")

    pw = W - PLATE_INSET * 2
    ph = H - PLATE_INSET * 2

    out = [
        blk_style.anim_css(),
        blk_style.draw_card(W, H, RADIUS, 17, t["paper"], t["border"],
                            stroke=STROKE, inset=8),
        ('<defs>'
         '<clipPath id="plate"><rect x="%d" y="%d" width="%d" height="%d" '
         'rx="%d" ry="%d"/></clipPath>'
         '<image id="himg" x="%d" y="%d" width="%d" height="%d" '
         'preserveAspectRatio="xMidYMid slice" clip-path="url(#plate)" '
         'href="data:image/png;base64,%s"/>'
         '</defs>'
         % (PLATE_INSET, PLATE_INSET, pw, ph, PLATE_RADIUS, PLATE_RADIUS,
            PLATE_INSET, PLATE_INSET, pw, ph, data)),
        '<use href="#himg" class="bgh1" style="animation-delay:-1.3s" '
        'opacity="0"/>',
        '<use href="#himg" class="bgh2" style="animation-delay:-1.3s" '
        'opacity="0"/>',
        '<use href="#himg" class="bglt" style="animation-delay:-1.3s"/>',
    ]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="Juan Dalvit - '
            'Engineering Manager. AI, Systems and Automation. Founder at '
            'Flexibase-Projects.">%s</svg>'
            % (W, H, W, H, "".join(out)))


def main():
    for theme in THEMES:
        markup = build(theme)
        name = "hero-%s.svg" % theme
        with open(os.path.join(BLK, name), "w", encoding="utf-8") as fh:
            fh.write(markup)
        print("assets/blk/%-18s %6.1f KB" % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
