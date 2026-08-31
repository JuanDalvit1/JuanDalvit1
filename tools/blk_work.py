#!/usr/bin/env python3
"""
BLK.SYSTEM - the selected-work cards.

One card per flagship system, each anchored by a single oversized figure -
the one number that tells the story. Everything on a card is verifiable in
the system's own repository (README, PROJECT.md, inventories); the repos are
private, so the cards are how the work gets counted without exposing a line
of it.

The hero figures, and where they come from:

    SSO           18  apps fronted        ISONLINE application catalog
    FoccoAPI       0  writes allowed      SELECT-only invariant, PROJECT.md
    platform-ops  92  containers mapped   inventory/runtime-containers.yaml
    PMC           19  RLS policies        README (Seguranca e Permissoes)
    SGI          B/G  deploy model        platform blue-green standard

What is deliberately absent: hostnames, IPs, internal topology, client name.
The client is described by profile in the section header, which is the
standard way to show NDA work.

Usage    python tools/blk_work.py
Outputs  assets/sections/work-<slug>-{light,dark}.svg
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 1280, 228
RADIUS = 24
STROKE = 3
EDGE_INSET = 6

LEFT = 52
NUM_X = W - 64          # right edge of the hero figure
LEFT_MAX = 88           # mono chars that fit before the hero column

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

# (slug, seed, index, name, tag, hero, hero_label, description, fact, chips)
SYSTEMS = [
    ("sso", 211, "01",
     "SSO / IDENTITY PLATFORM", "IN PRODUCTION",
     "18", "APPS FRONTED",
     "Central identity: OAuth2/OIDC, MFA, session governance and audit "
     "for the ecosystem.",
     "One login fronting every production app - fail-closed authorization",
     ["TypeScript", "Fastify", "Next.js", "Supabase", "PostgreSQL",
      "Docker", "NGINX"]),

    ("foccoapi", 223, "02",
     "FOCCOAPI / ERP DATA PLATFORM", "IN PRODUCTION",
     "0", "WRITES ALLOWED",
     "Read-only REST + MCP facade over the factory's Oracle ERP. Stable, "
     "versioned contracts.",
     "Active/standby topology - immutable SHA deploys, automatic rollback",
     ["TypeScript", "Fastify", "Oracle", "OpenAPI", "MCP", "GHCR",
      "GitHub Actions"]),

    ("platform-ops", 227, "03",
     "PLATFORM-OPS / CONTROL PLANE", "SOURCE OF TRUTH",
     "92", "CONTAINERS MAPPED",
     "The source of truth: sanitized inventory, ADRs, runbooks, evidence, "
     "change governance.",
     "28 services, 28 domains, 3 hosts - read-only collectors, SHA-256 "
     "evidence",
     ["Python", "YAML", "OpenSSH", "GitHub CLI", "Docker", "Ubuntu"]),

    ("pmc", 229, "04",
     "PMC / PROJECT PORTFOLIO", "IN PRODUCTION",
     "19", "RLS POLICIES",
     "Corporate project portfolio - scoring matrix, 5W2H plans and formal "
     "approval flow.",
     "Row-level security on every table - full audit trail - xlsx upsert "
     "import",
     ["React", "TypeScript", "Vite", "Supabase", "PostgreSQL", "Tailwind"]),

    ("sgi", 233, "05",
     "SGI / INDUSTRIAL KPIs", "IN PRODUCTION",
     "B/G", "DEPLOY MODEL",
     "Executive dashboard for industrial KPIs - trends, targets and Excel "
     "ingestion.",
     "Behind the central SSO - turns spreadsheet reporting into living "
     "dashboards",
     ["React", "TypeScript", "Vite", "shadcn/ui", "Supabase"]),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size, fill, weight=900, spacing=0, family=FONT,
         opacity=1.0, anchor="start"):
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" '
            'font-weight="%d" letter-spacing="%s" fill="%s" opacity="%s" '
            'text-anchor="%s">%s</text>'
            ) % (x, y, family, size, weight, spacing, fill, opacity,
                 anchor, esc(s))


def hand_underline(rng, x0, x1, y, ink, passes=2):
    """A short scrawled rule - the same hand that drew the border."""
    out = []
    for p in range(passes):
        step = 14.0
        n = max(2, int((x1 - x0) / step))
        pts = []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            pts.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.6) + p))
        d = "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % q for q in pts[1:])
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                   'stroke-linecap="round" opacity="%.2f"/>'
                   % (d, ink, 2.4 - p * 0.8, 0.9 - p * 0.35))
    return out


def build(system, theme):
    slug, seed, index, name, tag, hero, hero_label, desc, fact, chips = system
    for label, line in (("desc", desc), ("fact", fact)):
        if len(line) > LEFT_MAX:
            sys.exit("%s/%s is %d chars; %d is the ceiling - shorten it"
                     % (slug, label, len(line), LEFT_MAX))

    t = THEMES[theme]
    rng = random.Random(seed * 3 + (0 if theme == "light" else 1))
    out = []

    passes = blk_style.sketch(W - EDGE_INSET * 2, H - EDGE_INSET * 2,
                              RADIUS, seed, passes=3)
    shifted = [[(x + EDGE_INSET, y + EDGE_INSET) for x, y in p]
               for p in passes]
    out.append('<path d="%s" fill="%s"/>'
               % (blk_style.svg_path(shifted[0]), t["paper"]))
    for i, pts in enumerate(shifted):
        out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%d" '
                   'stroke-linejoin="round" stroke-linecap="round" '
                   'opacity="%.2f"/>'
                   % (blk_style.svg_path(pts), t["border"],
                      max(1, STROKE - i), 0.98 - 0.26 * i))

    # left column: catalogue index, flat title, the two lines that matter
    out.append(text(LEFT, 74, index, 30, t["sub"], 900, 2, MONO, 0.45))
    out.append(text(LEFT + 64, 76, name, 33, t["ink"], 900, 3))
    out.append(text(LEFT + 1, 116, desc, 16.5, t["sub"], 400, 0.5, MONO,
                    0.95))
    out.append(text(LEFT + 1, 148, fact, 16, t["ink"], 700, 0.5, MONO, 0.95))

    # right column: the hero figure - one number, set like it means it
    out.append(text(NUM_X, 66, tag, 13, t["sub"], 700, 3, MONO, 0.8,
                    anchor="end"))
    out.append(text(NUM_X, 152, hero, 84, t["ink"], 900, 0, FONT,
                    anchor="end"))
    hero_w = max(52, len(hero) * 58)
    out += hand_underline(rng, NUM_X - hero_w, NUM_X, 166, t["ink"])
    out.append(text(NUM_X, 190, hero_label, 13, t["sub"], 700, 3, MONO, 0.85,
                    anchor="end"))

    # bottom: the stack as chips, the same key as every other surface
    out.append('<path d="M%d 168H%d" stroke="%s" stroke-width="1.5"/>'
               % (LEFT, NUM_X - hero_w - 40, t["hair"]))
    cx, cy, ch = float(LEFT), 184.0, 28
    for chip in chips:
        cw = 20 + len(chip) * 7.0
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="8" '
                   'ry="8" fill="%s" stroke="%s" stroke-width="1.3"/>'
                   % (cx, cy, cw, ch, t["chip"], t["chip_edge"]))
        out.append(text(cx + cw / 2, cy + ch / 2 + 4.5, chip, 12.5, t["ink"],
                        700, 0, MONO, 0.95, anchor="middle"))
        cx += cw + 9

    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="%s">%s</svg>'
            % (W, H, W, H,
               esc("%s - %s %s. %s" % (name, hero, hero_label.lower(), desc)),
               "".join(out)))


def main():
    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)
    for system in SYSTEMS:
        for theme in THEMES:
            markup = build(system, theme)
            fname = "work-%s-%s.svg" % (system[0], theme)
            with open(os.path.join(out_dir, fname), "w",
                      encoding="utf-8") as fh:
                fh.write(markup)
            print("assets/sections/%-28s %6.1f KB" % (fname,
                                                      len(markup) / 1024))


if __name__ == "__main__":
    main()
