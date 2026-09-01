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

# --------------------------------------------------------------------------- #
# shared card chrome
# --------------------------------------------------------------------------- #

def anim_css():
    """
    The living layer, two behaviours:

      * the border UNDULATES - a continuous SMIL morph between the three
        sketch passes of the same line, slow and eased, so the edge moves
        the way something organic moves instead of snapping frames;
      * the titles GLITCH - long stillness, then a fraction of a second of
        print misregistration: two ink ghosts split off and snap back.
        Monochrome glitch, like a press that slipped, never an RGB effect.

    Plus the crown bob. All of it survives GitHub's image proxy (CSS and
    SMIL both run inside <img>), and prefers-reduced-motion stills the
    type and hides the ghosts. The SMIL morph does not consult the media
    query, so reduced-motion readers keep only the slow border drift -
    the gentlest motion on the page.
    """
    return (
        "<style>"
        "@keyframes blkBob{0%,100%{transform:translateY(0)}"
        "50%{transform:translateY(-5px)}}"
        "@keyframes blkGlM{0%,88%,93%,100%{transform:translate(0,0)}"
        "89%{transform:translate(2px,0)}91%{transform:translate(-2px,0)}}"
        "@keyframes blkGh1{0%,88%,93%,100%{opacity:0}"
        "89%{opacity:.5;transform:translate(6px,0)}"
        "91%{opacity:.35;transform:translate(-5px,1px)}}"
        "@keyframes blkGh2{0%,88%,93%,100%{opacity:0}"
        "89%{opacity:.4;transform:translate(-6px,0)}"
        "91%{opacity:.3;transform:translate(5px,-1px)}}"
        ".bcrown{animation:blkBob 4.2s ease-in-out infinite}"
        ".bglt,.bgh1,.bgh2{transform-box:fill-box;transform-origin:center}"
        ".bglt{animation:blkGlM 4.6s steps(1,end) infinite}"
        ".bgh1{animation:blkGh1 4.6s steps(1,end) infinite}"
        ".bgh2{animation:blkGh2 4.6s steps(1,end) infinite}"
        "@media (prefers-reduced-motion:reduce)"
        "{.bcrown,.bglt,.bgh1,.bgh2{animation:none}}"
        "</style>"
    )


def draw_card(w, h, radius, seed, paper, border, stroke=3, inset=6,
              dur=7.0):
    """
    The card, alive: one path carries both the paper fill and the ink
    edge, and its geometry morphs continuously between the three sketch
    passes of the same line - eased splines, no snapping. Fill and stroke
    live on one element so they can never drift apart. A second, fainter
    stroke runs the same cycle a phase ahead, the sketchy double line.
    """
    passes = sketch(w - inset * 2, h - inset * 2, radius, seed, passes=3)
    d = [svg_path([(x + inset, y + inset) for x, y in p]) for p in passes]

    def morph(values):
        n = len(values) - 1
        return ('<animate attributeName="d" dur="%.1fs" '
                'repeatCount="indefinite" calcMode="spline" '
                'keyTimes="%s" keySplines="%s" values="%s"/>'
                % (dur,
                   ";".join("%.3f" % (i / n) for i in range(n + 1)),
                   ";".join([".42 0 .58 1"] * n),
                   ";".join(values)))

    return (
        '<path fill="%s" stroke="%s" stroke-width="%.1f" '
        'stroke-linejoin="round" stroke-linecap="round" opacity="0.97" '
        'd="%s">%s</path>'
        '<path fill="none" stroke="%s" stroke-width="%.1f" '
        'stroke-linejoin="round" stroke-linecap="round" opacity="0.20" '
        'd="%s">%s</path>'
        % (paper, border, stroke * 0.9, d[0],
           morph([d[0], d[1], d[2], d[0]]),
           border, stroke * 0.55, d[1],
           morph([d[1], d[2], d[0], d[1]])))


def glitch(markup, delay=0.0):
    """
    Wrap one <text> element in the misregistration treatment: two ink
    ghosts that exist only during the burst, then the element itself.
    Ghosts rest at opacity 0, so reduced motion never sees them.
    """
    import re

    ghost = re.sub(r'opacity="[^"]*"', 'opacity="0"', markup, count=1)
    if 'opacity="0"' not in ghost:
        ghost = ghost.replace("<text ", '<text opacity="0" ', 1)
    style = 'style="animation-delay:-%.2fs" ' % delay
    return (ghost.replace("<text ", '<text class="bgh1" ' + style, 1)
            + ghost.replace("<text ", '<text class="bgh2" ' + style, 1)
            + markup.replace("<text ", '<text class="bglt" ' + style, 1))


def dust_anim(rng, n, bbox, ink):
    """
    Living graphite: faint particles that drift and flicker. Each one gets
    its own duration and a negative delay, so the field never moves in step
    - dust does not march.
    """
    x0, y0, x1, y1 = bbox
    out = []
    for _ in range(n):
        dur = rng.uniform(6.0, 13.0)
        out.append('<circle class="bdust" cx="%.1f" cy="%.1f" r="%.2f" '
                   'fill="%s" style="animation-duration:%.1fs;'
                   'animation-delay:-%.1fs"/>'
                   % (rng.uniform(x0, x1), rng.uniform(y0, y1),
                      rng.uniform(0.8, 2.0), ink, dur,
                      rng.uniform(0, dur)))
    return "".join(out)


def crown_image(root, theme, right_x, y, height, cls="bcrown"):
    """The drawn crown as a floating <image>, anchored by its right edge."""
    import base64
    import os

    from PIL import Image

    path = os.path.join(root, "assets", "blk", "crown-%s.png" % theme)
    with Image.open(path) as im:
        width = round(im.width * height / im.height)
    with open(path, "rb") as fh:
        data = base64.b64encode(fh.read()).decode("ascii")
    return ('<image class="%s" x="%d" y="%d" width="%d" height="%d" '
            'href="data:image/png;base64,%s"/>'
            % (cls, right_x - width, y, width, height, data))


def header(root, theme, tokens, index, title, subtitle, w,
           font, mono, crown_h=46):
    """
    The section header, now the top of its own content card rather than a
    card of its own: index, flat title, mono subtitle, floating crown.
    """
    def esc(s):
        return (s.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))

    out = [
        ('<text x="48" y="78" font-family="%s" font-size="32" '
         'font-weight="900" letter-spacing="2" fill="%s" opacity="0.45">'
         "%s</text>") % (mono, tokens["sub"], esc(index)),
        glitch(('<text x="118" y="80" font-family="%s" font-size="38" '
                 'font-weight="900" letter-spacing="5" fill="%s">'
                 "%s</text>") % (font, tokens["ink"], esc(title)),
               delay=(sum(map(ord, title)) % 37) / 10.0),
        ('<text x="120" y="116" font-family="%s" font-size="16" '
         'font-weight="400" letter-spacing="1" fill="%s" opacity="0.9">'
         "%s</text>") % (mono, tokens["sub"], esc(subtitle)),
        crown_image(root, theme, w - 50, 30, crown_h),
        ('<path d="M48 142H%d" stroke="%s" stroke-width="1.5"/>'
         % (w - 48, tokens.get("hair", tokens["sub"]))),
    ]
    return "".join(out)
