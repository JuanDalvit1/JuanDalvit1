#!/usr/bin/env python3
"""
BLK.SYSTEM - the living hero.

The banner itself is a raster drawing and cannot move. So the PNG gets
wrapped in an SVG that carries the living layer over it: graphite dust
drifting across the frame, and the terminal cursor blinking at the end of
the mono line. The atmosphere breathes; the entity holds still.

Run tools/blk_images.py first - this consumes hero-{theme}.png.

Usage    python tools/blk_hero.py
Outputs  assets/blk/hero-{light,dark}.svg
"""

import base64
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLK = os.path.join(ROOT, "assets", "blk")

W, H = 1500, 500
DUST_INK = {"light": "#57534c", "dark": "#8d887f"}


def build(theme):
    png = os.path.join(BLK, "hero-%s.png" % theme)
    if not os.path.exists(png):
        sys.exit("missing %s - run tools/blk_images.py first"
                 % os.path.relpath(png, ROOT))
    with open(png, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")

    rng = random.Random(41 if theme == "light" else 42)
    out = [
        blk_style.anim_css(),
        '<image x="0" y="0" width="%d" height="%d" '
        'href="data:image/png;base64,%s"/>' % (W, H, data),
        # drifting graphite, heavier around the figure, sparse over the type
        blk_style.dust_anim(rng, 26, (60, 40, 660, H - 40), DUST_INK[theme]),
        blk_style.dust_anim(rng, 8, (660, 40, W - 60, H - 60),
                            DUST_INK[theme]),
    ]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="Juan Dalvit - '
            'Engineering Manager. AI, Systems and Automation. Founder at '
            'Flexibase-Projects.">%s</svg>'
            % (W, H, W, H, "".join(out)))


def main():
    for theme in ("light", "dark"):
        markup = build(theme)
        name = "hero-%s.svg" % theme
        with open(os.path.join(BLK, name), "w", encoding="utf-8") as fh:
            fh.write(markup)
        print("assets/blk/%-18s %6.1f KB" % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
