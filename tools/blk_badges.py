#!/usr/bin/env python3
"""
BLK.SYSTEM - contact badges.

Links cannot live inside a README image, so the contact channels become
whole cards wrapped in <a> tags - the entire badge is the link. Three keys,
one row, same hand as everything else.

Usage    python tools/blk_badges.py
Outputs  assets/sections/badge-{linkedin,email,site}-{light,dark}.svg
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 416, 118
RADIUS = 18
STROKE = 3
EDGE_INSET = 6
MARGIN_BOTTOM = 14

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

THEMES = {
    "light": {"paper": "#f4f2ee", "ink": "#101010", "sub": "#57534c",
              "border": "#1c1a17"},
    "dark": {"paper": "#0a0a0a", "ink": "#ece8e0", "sub": "#8d887f",
             "border": "#cfc9c0"},
}

# (slug, seed, title, detail)
BADGES = [
    ("linkedin", 301, "LINKEDIN", "/in/juandalvit"),
    ("email", 307, "EMAIL", "eng3.flexibase@gmail.com"),
    ("site", 311, "SITE", "dalvit.dev"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size, fill, weight=900, spacing=0, family=FONT,
         opacity=1.0):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" '
            'font-weight="%d" letter-spacing="%s" fill="%s" opacity="%s">'
            "%s</text>") % (x, y, family, size, weight, spacing, fill,
                            opacity, esc(s))


def build(slug, seed, title, detail, theme):
    t = THEMES[theme]
    out = []

    out.append(blk_style.anim_css())
    out.append(blk_style.draw_card(W, H, RADIUS, seed, t["paper"],
                                   t["border"]))

    out.append(text(36, 56, title, 26, t["ink"], 900, 3))
    out.append(text(37, 88, detail, 14, t["sub"], 400, 0.5, MONO, 0.9))
    out.append('<text class="bcu" x="%.1f" y="88" font-family="%s" '
               'font-size="14" font-weight="700" fill="%s">_</text>'
               % (37 + len(detail) * 7.9 + 4, MONO, t["ink"]))

    total_h = H + MARGIN_BOTTOM
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="%s">%s</svg>'
            % (W, total_h, W, total_h,
               esc("%s - %s" % (title, detail)), "".join(out)))


def main():
    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)
    for slug, seed, title, detail in BADGES:
        for theme in THEMES:
            markup = build(slug, seed, title, detail, theme)
            name = "badge-%s-%s.svg" % (slug, theme)
            with open(os.path.join(out_dir, name), "w",
                      encoding="utf-8") as fh:
                fh.write(markup)
            print("assets/sections/%-28s %6.1f KB" % (name,
                                                      len(markup) / 1024))


if __name__ == "__main__":
    main()
