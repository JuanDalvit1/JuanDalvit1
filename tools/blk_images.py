#!/usr/bin/env python3
"""
BLK.SYSTEM - image pipeline.

Takes the two source drawings and derives every themed asset the README needs.

The whole pipeline rests on one idea: the source is ink on paper, so its
luminance IS the ink coverage. We read it as an alpha channel and re-ink it
per theme - nanquim on paper for light, chalk on charcoal for dark. Nothing
is ever pasted as an opaque rectangle, so the drawings sit on the page with
real transparency instead of a white box.

Inputs   assets/blk/src-bust.png     the bust with the floating crown
         assets/blk/src-arise.png    the figure reaching for the crown
Outputs  assets/blk/{hero,arise,crown}-{light,dark}.png

Usage    python tools/blk_images.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLK = os.path.join(ROOT, "assets", "blk")

SRC_BUST = os.path.join(BLK, "src-bust.png")
SRC_ARISE = os.path.join(BLK, "src-arise.png")

THEMES = {
    #        paper       ink (the stroke colour)
    "light": ("#f4f2ee", "#101010"),
    "dark": ("#0a0a0a", "#ece8e0"),
}

SUB = {"light": "#57534c", "dark": "#8d887f"}
RULE = {"light": "#c8c3b9", "dark": "#2b2b2b"}
BORDER = {"light": "#1c1a17", "dark": "#cfc9c0"}

# Every surface in the system is the same card: softly rounded, hand-drawn
# border, content held inside it. Nothing floats loose on the page.
RADIUS = 30          # ~17px once GitHub scales a 1500px banner to column width
STROKE = 5
EDGE_INSET = 9       # room for the wobble to swing without clipping

HERO = (1500, 500)
ARISE = (1500, 500)

# Flat, direct, no relief and no drop shadow - the geometric order that the
# scrawl is set against. Windows paths first, then the usual Linux/mac names,
# so the banner can be rebuilt off this machine.
BLACK = ("ariblk.ttf", "Arial Black.ttf", "DejaVuSans-Bold.ttf")
BOLD = ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf")
MONOB = ("consolab.ttf", "Menlo-Bold.ttf", "DejaVuSansMono-Bold.ttf")


# --------------------------------------------------------------------------- #
def font(candidates, size):
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    sys.exit("no usable font among %s - install one or edit the tuple"
             % (candidates,))


def tracked(draw, xy, s, fnt, fill, spacing=0):
    """
    Draw text with letter-spacing. Pillow has no tracking, and the BLK
    typography depends on it: wide, deliberate, machine-set.
    """
    x, y = xy
    colour = hexrgb(fill) if isinstance(fill, str) else fill
    for ch in s:
        draw.text((x, y), ch, font=fnt, fill=colour)
        x += draw.textlength(ch, font=fnt) + spacing
    return x


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_ink(path, white_point=246, black_point=28):
    """
    Read a drawing as an ink-coverage mask (L: 0 = bare paper, 255 = solid ink).

    white_point drops the paper's own off-white to zero so the sheet does not
    show up as a faint grey wash; black_point pushes the densest scribble to
    full so the entity stays as heavy as it is in the original.
    """
    img = Image.open(path).convert("L")
    ink = ImageOps.invert(img)
    lo, hi = 255 - white_point, 255 - black_point
    scale = 255.0 / max(1, hi - lo)
    return ink.point(lambda v: 0 if v <= lo else min(255, int((v - lo) * scale)))


def ink_layer(mask, ink_hex):
    """Colourise an ink mask into an RGBA layer - the mask becomes the alpha."""
    layer = Image.new("RGBA", mask.size, hexrgb(ink_hex) + (0,))
    layer.putalpha(mask)
    return layer


def trim(mask, threshold=14, pad=0):
    """Crop to the drawn area, ignoring paper noise below the threshold."""
    box = mask.point(lambda v: 255 if v > threshold else 0).getbbox()
    if box is None:
        return mask, (0, 0, mask.width, mask.height)
    x0, y0, x1, y1 = box
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(mask.width, x1 + pad), min(mask.height, y1 + pad)
    return mask.crop((x0, y0, x1, y1)), (x0, y0, x1, y1)


def fit_height(mask, height):
    w = max(1, round(mask.width * height / mask.height))
    return mask.resize((w, height), Image.LANCZOS)


def card(img, border_hex, seed, radius=RADIUS, stroke=STROKE):
    """
    Cut the card out along a hand-drawn edge and trace that same edge in ink.

    The wobbled outline is the silhouette, not a stroke laid over a geometric
    rectangle - so the corners themselves are organic and the page background
    shows through them instead of a matte painted in one theme's colour.
    """
    w = img.width - EDGE_INSET * 2
    h = img.height - EDGE_INSET * 2
    passes = blk_style.sketch(w, h, radius, seed, passes=3)
    shifted = [[(x + EDGE_INSET, y + EDGE_INSET) for x, y in p]
               for p in passes]

    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(shifted[0], fill=255)

    out = img.convert("RGBA")
    out.putalpha(mask)

    draw = ImageDraw.Draw(out)
    for i, pts in enumerate(shifted):
        alpha = int(255 * (0.98 - 0.26 * i))
        draw.line(pts, fill=hexrgb(border_hex) + (alpha,),
                  width=max(1, stroke - i), joint="curve")
    return out


def compose(size, paper_hex, layers):
    """Flatten themed layers onto the paper. Layers are (rgba, (x, y))."""
    canvas = Image.new("RGBA", size, hexrgb(paper_hex) + (255,))
    for layer, pos in layers:
        canvas.alpha_composite(layer, pos)
    return canvas


def grain(size, seed=11, strength=9):
    """Paper tooth - a faint monochrome noise wash, never a texture photo."""
    noise = Image.effect_noise((size[0] // 2, size[1] // 2), 26).convert("L")
    noise = noise.resize(size, Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.4))
    return noise.point(lambda v: 128 + (v - 128) * strength // 100)


def paper_grain(img, seed=11):
    base = img.convert("RGB")
    g = grain(img.size, seed).convert("RGB")
    return ImageChops.overlay(base, g).convert("RGBA")


def save(img, name):
    path = os.path.join(BLK, name)
    img.convert("RGBA").save(path, optimize=True)
    print("%-34s %5d x %-4d  %6.1f KB"
          % (name, img.width, img.height, os.path.getsize(path) / 1024))


# --------------------------------------------------------------------------- #
def build_hero(bust_mask):
    """
    Wide banner: the entity anchored left, the name set flat on bare paper to
    its right. The contrast is the point - geometric, unmodulated type against
    a body that is nothing but scrawl.
    """
    figure = fit_height(bust_mask, int(HERO[1] * 0.94))
    x = 44
    y = HERO[1] - figure.height
    tx = 620

    for theme, (paper, ink) in THEMES.items():
        canvas = compose(HERO, paper, [(ink_layer(figure, ink), (x, y))])
        canvas = paper_grain(canvas)
        draw = ImageDraw.Draw(canvas)
        sub = SUB[theme]

        tracked(draw, (tx, 138), "JUAN DALVIT", font(BLACK, 82), ink, 2)
        draw.line([(tx, 250), (HERO[0] - 60, 250)], fill=hexrgb(RULE[theme]),
                  width=2)
        tracked(draw, (tx, 282), "ENGINEERING MANAGER", font(BLACK, 25), ink, 7)
        tracked(draw, (tx + 2, 328), "AI · SYSTEMS · AUTOMATION",
                font(BOLD, 20), sub, 5)
        tracked(draw, (tx + 2, 404), "FOUNDER @ FLEXIBASE-PROJECTS",
                font(MONOB, 16), ink, 2)

        save(card(canvas, BORDER[theme], seed=17), "hero-%s.png" % theme)


def build_arise(arise_mask):
    """Closing mark: the reaching figure, centred, with the crown out of reach."""
    scale = min(ARISE[0] / arise_mask.width, ARISE[1] / arise_mask.height)
    w = max(1, round(arise_mask.width * scale))
    h = max(1, round(arise_mask.height * scale))
    figure = arise_mask.resize((w, h), Image.LANCZOS)
    pos = ((ARISE[0] - w) // 2, (ARISE[1] - h) // 2)
    for theme, (paper, ink) in THEMES.items():
        canvas = compose(ARISE, paper, [(ink_layer(figure, ink), pos)])
        canvas = paper_grain(canvas)

        draw = ImageDraw.Draw(canvas)
        tracked(draw, (58, ARISE[1] - 62), "I ARISE", font(BLACK, 30),
                ink, 9)

        save(card(canvas, BORDER[theme], seed=43), "arise-%s.png" % theme)


def largest_blob(mask, threshold=40, work_width=360):
    """
    Bounding box of the biggest connected ink blob, in full-resolution coords.

    A plain bounding box is useless here: the drawings are covered in spatter
    and stray graphite, so any stray speck near a corner blows the box out to
    the whole frame. Labelling and keeping the largest component ignores the
    dust and locks onto the actual object.
    """
    scale = work_width / mask.width
    w, h = work_width, max(1, round(mask.height * scale))
    small = mask.resize((w, h), Image.BILINEAR)
    px = small.load()

    seen = bytearray(w * h)
    best = (0, None)
    for sy in range(h):
        for sx in range(w):
            i = sy * w + sx
            if seen[i] or px[sx, sy] <= threshold:
                continue
            stack, count = [(sx, sy)], 0
            seen[i] = 1
            x0 = x1 = sx
            y0 = y1 = sy
            while stack:
                cx, cy = stack.pop()
                count += 1
                x0, x1 = min(x0, cx), max(x1, cx)
                y0, y1 = min(y0, cy), max(y1, cy)
                for nx, ny in ((cx - 1, cy), (cx + 1, cy),
                               (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not seen[j] and px[nx, ny] > threshold:
                            seen[j] = 1
                            stack.append((nx, ny))
            if count > best[0]:
                best = (count, (x0, y0, x1, y1))

    if best[1] is None:
        return None
    x0, y0, x1, y1 = best[1]
    return (int(x0 / scale), int(y0 / scale),
            int((x1 + 1) / scale), int((y1 + 1) / scale))


def build_crown(bust_mask, band=0.30, height=160, pad=10):
    """
    Isolate the floating crown from the bust.

    The crown is the only object in the top band of the source - the head
    starts below it, by definition, because the crown never touches it.
    """
    top = bust_mask.crop((0, 0, bust_mask.width, int(bust_mask.height * band)))
    box = largest_blob(top)
    if box is None:
        sys.exit("crown not found in the top %d%% of src-bust.png"
                 % int(band * 100))
    x0, y0, x1, y1 = box
    box = (max(0, x0 - pad), max(0, y0 - pad),
           min(top.width, x1 + pad), min(top.height, y1 + pad))
    crown = fit_height(top.crop(box), height)
    for theme, (_paper, ink) in THEMES.items():
        save(ink_layer(crown, ink), "crown-%s.png" % theme)
    return box


# --------------------------------------------------------------------------- #
def main():
    missing = [p for p in (SRC_BUST, SRC_ARISE) if not os.path.exists(p)]
    if missing:
        sys.exit("missing source drawings:\n  " + "\n  ".join(
            os.path.relpath(p, ROOT) for p in missing))

    # The sources are already composed drawings - they are placed whole.
    # Auto-cropping them fights the spatter, which is part of the artwork.
    bust = load_ink(SRC_BUST)
    arise = load_ink(SRC_ARISE)

    build_crown(bust)
    build_hero(bust)
    build_arise(arise)


if __name__ == "__main__":
    main()
