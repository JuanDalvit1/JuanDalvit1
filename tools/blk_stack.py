#!/usr/bin/env python3
"""
BLK.SYSTEM - the stack card.

A labelled grid of chips, monochrome. Brand colour is the whole point of the
usual badge wall, and this system does not have colour to spend - so identity
is carried by the glyph and the word, and every chip is the same key as every
other surface in the profile.

Icons come from Simple Icons at build time and are inlined as raw paths, then
cached in tools/simple-icons.json. Nothing is fetched when the README is read:
a profile that depends on a third-party badge service being up is a profile
with a broken image the first time that service has a bad day.

Edit STACK below to change what is shown - it is the single source of truth.

Usage    python tools/blk_stack.py [--refresh]
Outputs  assets/sections/tech-stack-{light,dark}.svg
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "simple-icons.json")
CDN = "https://cdn.jsdelivr.net/npm/simple-icons/icons/%s.svg"

# (label, [(display name, simple-icons slug or None)])
STACK = [
    ("LANGUAGES", [
        ("Python", "python"), ("TypeScript", "typescript"),
        ("JavaScript", "javascript"), ("Dart", "dart"),
        ("SQL", "postgresql"), ("PowerShell", "powershell"),
        ("Bash", "gnubash"), ("HTML", "html5"), ("CSS", "css"),
    ]),
    ("AI / LLM", [
        ("Claude", "anthropic"), ("ChatGPT", "openai"),
        ("Gemini", "googlegemini"), ("Grok", "x"),
        ("DeepSeek", "deepseek"), ("Ollama", "ollama"),
        ("MCP", "modelcontextprotocol"), ("LangChain", "langchain"),
        ("Hugging Face", "huggingface"), ("n8n", "n8n"),
    ]),
    ("BACKEND", [
        ("FastAPI", "fastapi"), ("Node.js", "nodedotjs"),
        ("Express", "express"), ("Django", "django"),
        ("Flask", "flask"), ("NestJS", "nestjs"),
        ("GraphQL", "graphql"), ("Socket.IO", "socketdotio"),
    ]),
    ("DATA", [
        ("PostgreSQL", "postgresql"), ("MySQL", "mysql"),
        ("MongoDB", "mongodb"), ("Redis", "redis"),
        ("SQLite", "sqlite"), ("Supabase", "supabase"),
        ("Pandas", "pandas"), ("NumPy", "numpy"),
        ("OpenCV", "opencv"),
    ]),
    ("FRONTEND", [
        ("React", "react"), ("Next.js", "nextdotjs"),
        ("Vue", "vuedotjs"), ("Nuxt", "nuxt"),
        ("Flutter", "flutter"), ("Tailwind", "tailwindcss"),
        ("shadcn/ui", "shadcnui"), ("Radix", "radixui"),
        ("Vite", "vite"),
    ]),
    ("INFRA", [
        ("Docker", "docker"), ("Kubernetes", "kubernetes"),
        ("GitHub Actions", "githubactions"), ("Linux", "linux"),
        ("Ubuntu", "ubuntu"), ("Nginx", "nginx"),
        ("Cloudflare", "cloudflare"), ("Vercel", "vercel"),
        ("Grafana", "grafana"), ("Git", "git"), ("VS Code", "vscodium"),
    ]),
]

W = 1280
MARGIN_BOTTOM = 22
RADIUS = 24
STROKE = 3
EDGE_INSET = 6

PAD_X, PAD_TOP = 38, 178
GUTTER = 124           # width of the row-label column
CHIP_H = 33
CHIP_PAD = 10
CHIP_GAP = 8
ROW_GAP = 13
ICON = 15
LABEL_SIZE = 13
CHAR_W = 7.1           # mono advance at LABEL_SIZE, measured not guessed

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

THEMES = {
    "light": {"paper": "#f4f2ee", "ink": "#101010", "sub": "#57534c",
              "border": "#1c1a17", "hair": "#e2ddd2",
              "chip": "#eae7e0", "chip_edge": "#d5cfc3"},
    "dark": {"paper": "#0a0a0a", "ink": "#ece8e0", "sub": "#8d887f",
             "border": "#cfc9c0", "hair": "#242424",
             "chip": "#151515", "chip_edge": "#303030"},
}


# --------------------------------------------------------------------------- #
def load_cache():
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def fetch_icon(slug):
    """Pull one Simple Icons glyph and return just its path data."""
    req = urllib.request.Request(CDN % slug,
                                 headers={"User-Agent": "blk-system"})
    with urllib.request.urlopen(req, timeout=20) as res:
        markup = res.read().decode()
    match = re.search(r'\sd="([^"]+)"', markup)
    return match.group(1) if match else None


def resolve_icons(refresh=False):
    cache = {} if refresh else load_cache()
    wanted = {slug for _label, items in STACK for _name, slug in items if slug}
    missing = sorted(wanted - set(cache))

    for slug in missing:
        try:
            path = fetch_icon(slug)
        except urllib.error.HTTPError as err:
            print("  ! %s -> HTTP %s (chip will be text-only)"
                  % (slug, err.code))
            path = None
        except urllib.error.URLError as err:
            sys.exit("cannot reach the icon CDN (%s). Run once online; the "
                     "cache is committed so later builds work offline."
                     % err.reason)
        cache[slug] = path
        print("  + %s" % slug if path else "  ! %s -> no path" % slug)

    if missing:
        with open(CACHE, "w", encoding="utf-8") as fh:
            json.dump(cache, fh, indent=1, sort_keys=True)
    return cache


# --------------------------------------------------------------------------- #
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def text(x, y, s, size, fill, weight=900, spacing=0, family=FONT,
         opacity=1.0, anchor="start"):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" '
            'font-weight="%d" letter-spacing="%s" fill="%s" opacity="%s" '
            'text-anchor="%s">%s</text>'
            ) % (x, y, family, size, weight, spacing, fill, opacity,
                 anchor, esc(s))


def chip_width(name, has_icon):
    width = CHIP_PAD * 2 + len(name) * CHAR_W
    if has_icon:
        width += ICON + 7
    return width


def layout():
    """
    Wrap chips inside each labelled row and return the placed geometry.

    Done as a measure pass so the card's height follows its content - a fixed
    canvas would either clip a long row or leave dead paper under a short one.
    """
    rows, y = [], PAD_TOP
    max_x = W - PAD_X
    for label, items in STACK:
        lines, line, x = [], [], GUTTER
        for name, slug in items:
            width = chip_width(name, bool(slug))
            if line and x + width > max_x:
                lines.append(line)
                line, x = [], GUTTER
            line.append((x, name, slug, width))
            x += width + CHIP_GAP
        if line:
            lines.append(line)

        rows.append((label, y, lines))
        y += len(lines) * CHIP_H + (len(lines) - 1) * 6 + ROW_GAP
    return rows, int(y - ROW_GAP + 34)


def build(theme, icons, rows, height):
    t = THEMES[theme]
    out = []

    out.append(blk_style.anim_css())
    out.append(blk_style.draw_card(W, height, RADIUS, 59, t["paper"],
                                   t["border"]))
    out.append(blk_style.header(ROOT, theme, t, "03", "TECH STACK",
                                "languages, ai, backend, data, frontend, "
                                "infrastructure", W, FONT, MONO))

    for label, y, lines in rows:
        out.append(text(GUTTER - 20, y + CHIP_H / 2 + 5, label, 13, t["sub"],
                        700, 3, MONO, 0.9, anchor="end"))

        for row_i, line in enumerate(lines):
            top = y + row_i * (CHIP_H + 6)
            for x, name, slug, width in line:
                out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" '
                           'rx="9" ry="9" fill="%s" stroke="%s" '
                           'stroke-width="1.5"/>'
                           % (x, top, width, CHIP_H, t["chip"],
                              t["chip_edge"]))

                tx = x + CHIP_PAD
                path = icons.get(slug) if slug else None
                if path:
                    scale = ICON / 24.0
                    gx = tx
                    gy = top + (CHIP_H - ICON) / 2
                    out.append('<g transform="translate(%.1f %.1f) '
                               'scale(%.4f)"><path d="%s" fill="%s"/></g>'
                               % (gx, gy, scale, path, t["ink"]))
                    tx += ICON + 7

                out.append(text(tx, top + CHIP_H / 2 + 5, name, LABEL_SIZE,
                                t["ink"], 700, 0, MONO, 0.95))

    th = height + MARGIN_BOTTOM
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="%s">%s</svg>'
            % (W, th, W, th, esc(alt_text()), "".join(out)))


def alt_text():
    return "03 Tech Stack: " + "; ".join(
        "%s - %s" % (label, ", ".join(n for n, _s in items))
        for label, items in STACK)


# --------------------------------------------------------------------------- #
def main():
    icons = resolve_icons(refresh="--refresh" in sys.argv)
    rows, height = layout()

    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)
    for theme in THEMES:
        name = "tech-stack-%s.svg" % theme
        markup = build(theme, icons, rows, height)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(markup)
        print("assets/sections/%-24s %4d x %-4d %6.1f KB"
              % (name, W, height, len(markup) / 1024))


if __name__ == "__main__":
    main()
