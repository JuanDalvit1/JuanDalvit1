#!/usr/bin/env python3
"""
BLK.SYSTEM - the selected-work card.

One card for the whole section: header on top, the five flagship systems
stacked inside, separated by hairlines. Everything on it is verifiable in
the systems' own repositories (README, PROJECT.md, inventories); the repos
are private, so this card is how the work gets counted without exposing a
line of it.

The right column of each block names the capability the system proves about
its builder - the line a reader hiring a developer actually scans for.
Scale lives in the fact lines, where it belongs.

What is deliberately absent: hostnames, IPs, internal topology, client name.
The client is described by profile in the header, the standard treatment
for NDA work.

Usage    python tools/blk_work.py
Outputs  assets/sections/selected-work-{light,dark}.svg
"""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W = 1280
RADIUS = 24
MARGIN_BOTTOM = 22

LEFT = 52
CAP_X = W - 64          # right edge of the capability column
LEFT_MAX = 88           # mono chars that fit before the capability column

HEADER_H = 170          # header zone inside the card
STRIDE = 188            # vertical rhythm of one system block

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

# (index, name, tag, capability_lines, description, fact, chips)
SYSTEMS = [
    ("01", "SSO / IDENTITY PLATFORM", "IN PRODUCTION",
     ["SECURITY &", "IDENTITY"],
     "Central identity: OAuth2/OIDC, MFA, session governance and audit "
     "for the ecosystem.",
     "One login fronting 18 production apps - fail-closed authorization",
     ["TypeScript", "Fastify", "Next.js", "Supabase", "PostgreSQL",
      "Docker", "NGINX"]),

    ("02", "FOCCOAPI / ERP DATA PLATFORM", "IN PRODUCTION",
     ["LEGACY", "INTEGRATION"],
     "Read-only REST + MCP facade over the factory's Oracle ERP. Stable, "
     "versioned contracts.",
     "Zero writes by invariant - immutable SHA deploys, automatic rollback",
     ["TypeScript", "Fastify", "Oracle", "OpenAPI", "MCP", "GHCR",
      "GitHub Actions"]),

    ("03", "PLATFORM-OPS / CONTROL PLANE", "SOURCE OF TRUTH",
     ["PLATFORM", "GOVERNANCE"],
     "The source of truth: sanitized inventory, ADRs, runbooks, evidence, "
     "change governance.",
     "92 containers, 28 services, 3 hosts - read-only collectors, SHA-256 "
     "evidence",
     ["Python", "YAML", "OpenSSH", "GitHub CLI", "Docker", "Ubuntu"]),

    ("04", "PMC / PROJECT PORTFOLIO", "IN PRODUCTION",
     ["PRODUCT", "DELIVERY"],
     "Corporate project portfolio - scoring matrix, 5W2H plans and formal "
     "approval flow.",
     "Row-level security on every table - full audit trail - xlsx upsert "
     "import",
     ["React", "TypeScript", "Vite", "Supabase", "PostgreSQL", "Tailwind"]),

    ("05", "SGI / INDUSTRIAL KPIs", "IN PRODUCTION",
     ["DATA", "PLATFORMS"],
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
    """
    A short scrawled rule - the same hand that drew the border."""
    out = []
    for p in range(passes):
        n = max(2, int((x1 - x0) / 14.0))
        pts = [(x0 + (x1 - x0) * i / n + rng.gauss(0, 1.2),
                y + rng.gauss(0, 1.6) + p) for i in range(n + 1)]
        d = "M%.1f %.1f" % pts[0] + "".join("L%.1f %.1f" % q for q in pts[1:])
        out.append('<path d="%s" fill="none" stroke="%s" '
                   'stroke-width="%.1f" stroke-linecap="round" '
                   'opacity="%.2f"/>'
                   % (d, ink, 2.4 - p * 0.8, 0.9 - p * 0.35))
    return out


def block(system, b, t, rng):
    """One system, laid out inside the shared card at base offset b."""
    index, name, tag, cap, desc, fact, chips = system
    for label, line in (("desc", desc), ("fact", fact)):
        if len(line) > LEFT_MAX:
            sys.exit("%s/%s is %d chars; %d is the ceiling - shorten it"
                     % (name, label, len(line), LEFT_MAX))

    out = []
    out.append(text(LEFT, b + 40, index, 22, t["sub"], 900, 2, MONO, 0.45))
    name_t = text(LEFT + 52, b + 42, name, 27, t["ink"], 900, 3)
    out.append(name_t.replace('<text ', '<text class="bboil" '
                              'style="animation-delay:-%.2fs" '
                              % rng.uniform(0, 0.9), 1))
    out.append(text(LEFT + 1, b + 76, desc, 15.5, t["sub"], 400, 0.5, MONO,
                    0.95))
    out.append(text(LEFT + 1, b + 106, fact, 15, t["ink"], 700, 0.5, MONO,
                    0.95))

    # capability column
    out.append(text(CAP_X, b + 34, tag, 12, t["sub"], 700, 3, MONO, 0.8,
                    anchor="end"))
    cap_y = b + 82
    cap_delay = rng.uniform(0, 0.9)
    for line in cap:
        cap_t = text(CAP_X, cap_y, line, 26, t["ink"], 900, 2, FONT,
                     anchor="end")
        out.append(cap_t.replace('<text ', '<text class="bboil" '
                                 'style="animation-delay:-%.2fs" '
                                 % cap_delay, 1))
        cap_y += 33
    cap_w = max(130, int(max(len(line) for line in cap) * 18.5))
    out += hand_underline(rng, CAP_X - cap_w, CAP_X, cap_y - 18, t["ink"])
    out.append(text(CAP_X, cap_y + 6, "CAPABILITY", 11, t["sub"], 700, 4,
                    MONO, 0.8, anchor="end"))

    # chips
    cx, cy, ch = float(LEFT), b + 126.0, 26
    for chip in chips:
        cw = 18 + len(chip) * 6.6
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="8" '
                   'ry="8" fill="%s" stroke="%s" stroke-width="1.2"/>'
                   % (cx, cy, cw, ch, t["chip"], t["chip_edge"]))
        out.append(text(cx + cw / 2, cy + ch / 2 + 4, chip, 12, t["ink"],
                        700, 0, MONO, 0.95, anchor="middle"))
        cx += cw + 8
    return out


def build(theme):
    t = THEMES[theme]
    rng = random.Random(151 if theme == "light" else 152)

    card_h = HEADER_H + len(SYSTEMS) * STRIDE - 10
    th = card_h + MARGIN_BOTTOM

    out = [
        blk_style.anim_css(),
        blk_style.draw_card(W, card_h, RADIUS, 61, t["paper"], t["border"]),
        blk_style.header(ROOT, theme, t, "02", "SELECTED WORK",
                         "industrial systems for one of brazil's largest "
                         "furniture manufacturers", W, FONT, MONO),
    ]
    for i, system in enumerate(SYSTEMS):
        b = HEADER_H + i * STRIDE
        if i:
            out.append('<path d="M%d %dH%d" stroke="%s" '
                       'stroke-width="1.5"/>'
                       % (LEFT, b - 12, W - LEFT, t["hair"]))
        out += block(system, b, t, rng)

    alt = "Selected work: " + "; ".join(
        "%s (%s) - %s" % (s[1], " ".join(s[3]).title(), s[4])
        for s in SYSTEMS)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" aria-label="%s">%s</svg>'
            % (W, th, W, th, esc(alt), "".join(out)))


def main():
    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)
    for theme in THEMES:
        markup = build(theme)
        name = "selected-work-%s.svg" % theme
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(markup)
        print("assets/sections/%-28s %6.1f KB" % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
