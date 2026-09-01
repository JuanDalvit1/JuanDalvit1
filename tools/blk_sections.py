#!/usr/bin/env python3
"""
BLK.SYSTEM - standalone section headers.

Most sections are now a single card holding their own header and content
(blk_manifesto, blk_work, blk_stack). Two sections keep a standalone header
because their content cannot live inside our SVG: the contribution snake is
an external image rebuilt by CI, and the contact badges must each be their
own anchor to be clickable.

Usage    python tools/blk_sections.py
Outputs  assets/sections/<slug>-{light,dark}.svg
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEMES = {
    "light": {"paper": "#f4f2ee", "ink": "#101010",
              "sub": "#57534c", "border": "#1c1a17", "hair": "#e2ddd2"},
    "dark": {"paper": "#0a0a0a", "ink": "#ece8e0",
             "sub": "#8d887f", "border": "#cfc9c0", "hair": "#242424"},
}

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

W, H = 1280, 150
MARGIN_BOTTOM = 22
RADIUS = 24

SECTIONS = [
    ("04", "CONTRIBUTION GRAPH",
     "the serpent eats every commit / rebuilt every 12h",
     "serpent", 122),
    ("05", "GET IN TOUCH",
     "open channels",
     "contact", 129),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(index, title, subtitle, theme, seed):
    t = THEMES[theme]
    th = H + MARGIN_BOTTOM
    out = [
        blk_style.anim_css(),
        blk_style.draw_card(W, H, RADIUS, seed, t["paper"], t["border"]),
        ('<text x="48" y="74" font-family="%s" font-size="32" '
         'font-weight="900" letter-spacing="2" fill="%s" opacity="0.45">'
         "%s</text>") % (MONO, t["sub"], esc(index)),
        ('<text class="bboil" x="118" y="76" font-family="%s" '
         'font-size="38" font-weight="900" letter-spacing="5" '
         'fill="%s">%s</text>') % (FONT, t["ink"], esc(title)),
        ('<text x="120" y="114" font-family="%s" font-size="16" '
         'font-weight="400" letter-spacing="1" fill="%s" opacity="0.85">'
         "%s</text>") % (MONO, t["sub"], esc(subtitle)),
        blk_style.crown_image(ROOT, theme, W - 50, 52, 46),
    ]
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="%s">%s</svg>'
            % (W, th, W, th, esc("%s %s - %s" % (index, title, subtitle)),
               "".join(out)))


def main():
    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)
    for index, title, subtitle, slug, seed in SECTIONS:
        for theme in THEMES:
            markup = build(index, title, subtitle, theme, seed)
            name = "%s-%s.svg" % (slug, theme)
            with open(os.path.join(out_dir, name), "w",
                      encoding="utf-8") as fh:
                fh.write(markup)
            print("assets/sections/%-26s %6.1f KB" % (name,
                                                      len(markup) / 1024))


if __name__ == "__main__":
    main()
