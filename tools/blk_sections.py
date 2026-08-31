#!/usr/bin/env python3
"""
BLK.SYSTEM - section headers.

One pattern, repeated for every section of the profile:

    [index]  [FLAT TITLE]                                          [crown]
    ------------------------------------------------------------------------
    [lowercase mono subtitle]

Order in the typography, the entity's mark at the end of the rule. The crown
is the drawing itself, embedded as a data URI - a README image is served
through GitHub's proxy, so a relative <image href> inside the SVG would never
resolve. Run tools/blk_images.py first to produce it.

Usage    python tools/blk_sections.py
Outputs  assets/sections/<slug>-{light,dark}.svg
"""

import base64
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEMES = {
    "light": {"paper": "#f4f2ee", "ink": "#101010",
              "sub": "#57534c", "rule": "#cfcabf"},
    "dark": {"paper": "#0a0a0a", "ink": "#ece8e0",
             "sub": "#8d887f", "rule": "#2b2b2b"},
}

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

W, H = 1280, 132
CROWN_H = 46

SECTIONS = [
    ("01", "MANIFESTO", "how i work, and what i refuse to ship", "manifesto"),
    ("02", "STACK", "what i actually reach for", "stack"),
    ("03", "SIGNALS", "the numbers, unedited", "signals"),
    ("04", "THE SERPENT", "the void devours every commit", "serpent"),
    ("05", "CONTACT", "open channels", "contact"),
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


def build(index, title, subtitle, theme, crown_data, crown_w):
    t = THEMES[theme]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 %(w)d %(h)d" width="%(w)d" height="%(h)d" role="img" '
        'aria-label="%(alt)s">'
        '<rect width="%(w)d" height="%(h)d" fill="%(paper)s"/>'
        "%(index)s%(title)s"
        '<image x="%(cx)d" y="18" width="%(cw)d" height="%(ch)d" '
        'xlink:href="%(crown)s"/>'
        '<path d="M40 84H%(rule_end)d" stroke="%(rule)s" stroke-width="2"/>'
        "%(subtitle)s"
        "</svg>"
    ) % {
        "w": W, "h": H,
        "alt": "%s %s" % (index, title),
        "paper": t["paper"],
        "rule": t["rule"],
        "rule_end": W - 40,
        "index": text(40, 62, index, 34, t["sub"], 900, 2, MONO, 0.5),
        "title": text(112, 62, title, 40, t["ink"], 900, 7),
        "subtitle": text(42, 116, subtitle, 17, t["sub"], 400, 1, MONO, 0.9),
        "cx": W - 40 - crown_w,
        "cw": crown_w,
        "ch": CROWN_H,
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

        for index, title, subtitle, slug in SECTIONS:
            markup = build(index, title, subtitle, theme, data, crown_w)
            name = "%s-%s.svg" % (slug, theme)
            with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
                fh.write(markup)
            print("assets/sections/%-26s %6.1f KB"
                  % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
