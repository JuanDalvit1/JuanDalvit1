#!/usr/bin/env python3
"""
BLK.SYSTEM - the manifesto body.

The whole 01 section as one card: header on top, the manifesto beneath it.
The one place the profile speaks in full sentences - and even here, nothing
floats loose on the page. Height follows the text.

Usage    python tools/blk_manifesto.py
Outputs  assets/sections/what-i-build-{light,dark}.svg
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W = 1280
RADIUS = 24
STROKE = 3
EDGE_INSET = 6
MARGIN_BOTTOM = 22       # transparent breathing room baked into the file

LEFT = 56
CHAR_W = 8.7             # mono advance at 16px
WRAP = int((W - LEFT * 2) / CHAR_W)   # ~134 chars
LINE_H = 27

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

THEMES = {
    "light": {"paper": "#f4f2ee", "ink": "#101010", "sub": "#57534c",
              "border": "#1c1a17", "hair": "#e2ddd2"},
    "dark": {"paper": "#0a0a0a", "ink": "#ece8e0", "sub": "#8d887f",
             "border": "#cfc9c0", "hair": "#242424"},
}

INTRO = [
    "Engineering Manager working at the seam where AI, systems and "
    "automation meet the parts of a business that actually have to keep "
    "running.",
    "I care about the unglamorous half of engineering: clear contracts, "
    "honest error paths, observability that answers questions at 3am, and "
    "documentation that stays true after the third refactor. I would rather "
    "ship one boring system that holds than five clever ones that need a "
    "keeper.",
]

# (lead set in ink, rest set in sub)
PRINCIPLES = [
    ("CONTRACTS BEFORE CODE",
     "an API without a validated schema and a defined failure mode is a "
     "rumour, not an interface."),
    ("DOCS ARE PART OF DONE",
     "if the architecture changed and the doc did not, the work is "
     "unfinished."),
    ("AUTOMATE THE SECOND TIME",
     "the first time is research; the second is a pipeline."),
    ("ACCESSIBILITY IS NOT A PHASE",
     "every state - loading, empty, error, disabled, keyboard - ships or "
     "the component does not."),
    ("NO DASHBOARDS WITHOUT DATA",
     "everything on this page is drawn from real, verifiable numbers."),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(s, width):
    lines, line = [], ""
    for word in s.split():
        cand = (line + " " + word).strip()
        if len(cand) > width and line:
            lines.append(line)
            line = word
        else:
            line = cand
    if line:
        lines.append(line)
    return lines


def text(x, y, s, size, fill, weight=900, spacing=0, family=FONT,
         opacity=1.0):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" '
            'font-weight="%d" letter-spacing="%s" fill="%s" opacity="%s">'
            "%s</text>") % (x, y, family, size, weight, spacing, fill,
                            opacity, esc(s))


def tick(rng, x, y, ink):
    """A short hand-drawn dash - the bullet, in the border's own hand."""
    out = []
    for p in range(2):
        pts = [(x + i * 7 + rng.gauss(0, 1.0),
                y + rng.gauss(0, 1.3) + p * 0.8) for i in range(4)]
        d = "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % q for q in pts[1:])
        out.append('<path d="%s" fill="none" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round" '
                   'opacity="%.2f"/>'
                   % (d, ink, 2.2 - p * 0.7, 0.9 - p * 0.3))
    return out


def build(theme):
    t = THEMES[theme]
    rng = random.Random(97 if theme == "light" else 98)

    # measure pass: lay the text out first, then draw the card around it
    blocks = []          # (kind, payload)
    for para in INTRO:
        blocks.append(("para", wrap(para, WRAP)))
    blocks.append(("hair", None))
    for lead, rest in PRINCIPLES:
        blocks.append(("principle", wrap("%s - %s" % (lead, rest), WRAP - 4)))

    y = 186.0
    body = []
    for kind, lines in blocks:
        if kind == "hair":
            body.append('<path d="M%d %.1fH%d" stroke="%s" '
                        'stroke-width="1.5"/>'
                        % (LEFT, y - 12, W - LEFT, t["hair"]))
            y += 16
            continue
        if kind == "para":
            for line in lines:
                body.append(text(LEFT, y, line, 16, t["sub"], 400, 0.5,
                                 MONO, 0.95))
                y += LINE_H
            y += 10
        else:
            for i, line in enumerate(lines):
                x = LEFT + 34
                if i == 0:
                    body += tick(rng, LEFT, y - 5, t["ink"])
                    lead = line.split(" - ")[0]
                    # SVG collapses a leading space, so hand the rest over
                    # already stripped and give it its own start position
                    rest = line[len(lead):].lstrip()
                    body.append(text(x, y, lead, 16, t["ink"], 700, 0.5,
                                     MONO, 0.98))
                    body.append(text(x + (len(lead) + 1) * CHAR_W + 4, y, rest,
                                     16, t["sub"], 400, 0.5, MONO, 0.95))
                else:
                    body.append(text(x, y, line, 16, t["sub"], 400, 0.5,
                                     MONO, 0.95))
                y += LINE_H
            y += 7

    card_h = int(y + 18)

    out = [
        blk_style.anim_css(),
        blk_style.draw_card(W, card_h, RADIUS, 131, t["paper"],
                            t["border"]),
        blk_style.header(ROOT, theme, t, "01", "WHAT I BUILD",
                         "ai systems, automation, and the platforms that "
                         "keep them running", W, FONT, MONO),
    ]
    out += body

    total_h = card_h + MARGIN_BOTTOM
    alt = ("01 What I Build. " + " ".join(INTRO) + " "
           + " ".join("%s: %s" % p for p in PRINCIPLES))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="%s">%s</svg>'
            % (W, total_h, W, total_h, esc(alt), "".join(out)))


def main():
    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)
    for theme in THEMES:
        markup = build(theme)
        name = "what-i-build-%s.svg" % theme
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(markup)
        print("assets/sections/%-28s %6.1f KB" % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
