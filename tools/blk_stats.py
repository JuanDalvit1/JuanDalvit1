#!/usr/bin/env python3
"""
BLK.SYSTEM - the signals card.

Renders real GitHub numbers as a BLK card instead of leaning on a third-party
badge service. That is the whole reason this file exists: the public
github-readme-stats instance answers 503 often enough that a profile built on
it ships a broken image, and a broken image on a profile reads as neglect.

Form follows the data's job. Counts have no shape to compare, so they are
stat tiles, not a chart. The language split is parts-of-a-whole, so it is one
stacked bar. Identity never rests on colour - the system is monochrome by
definition, so every segment carries a written label.

Stars and followers are deliberately not shown: real numbers, but they count
fame, not work. The tiles count work - repositories, apps in production,
containers in operation, contributions.

Scope note: without a personal token this can only see what any visitor sees -
public repos owned by the user. Work living in private repos or in an org with
no public repos is invisible to the API, and the card says so rather than
inflating the number. Set METRICS_TOKEN to a personal access token with `repo`
and `read:org` and it counts everything that token can see.

Usage    python tools/blk_stats.py [user]
Env      METRICS_TOKEN  personal token; unlocks private + org repos
         GITHUB_TOKEN   fallback; lifts rate limits and unlocks the
                        contribution count (GraphQL requires auth)
Outputs  assets/sections/stats-{light,dark}.svg
"""

import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import blk_style

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER = sys.argv[1] if len(sys.argv) > 1 else "JuanDalvit1"
# METRICS_TOKEN first: the workflow's GITHUB_TOKEN is scoped to this one repo
# and cannot see anything private, org-wide or otherwise.
TOKEN = (os.environ.get("METRICS_TOKEN", "").strip()
         or os.environ.get("GITHUB_TOKEN", "").strip())

W, H = 1280, 312
MARGIN_BOTTOM = 22
RADIUS = 24
STROKE = 3
EDGE_INSET = 6

FONT = "'Arial Black','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular',Menlo,Consolas,monospace"

THEMES = {
    "light": {
        "paper": "#f4f2ee", "ink": "#101010", "sub": "#57534c",
        "border": "#1c1a17", "hair": "#e2ddd2",
        # sequential graphite ramp, dark -> light: magnitude, not identity
        "ramp": ["#101010", "#3c3a35", "#6b675f", "#99948a", "#c2bcb0"],
    },
    "dark": {
        "paper": "#0a0a0a", "ink": "#ece8e0", "sub": "#8d887f",
        "border": "#cfc9c0", "hair": "#242424",
        "ramp": ["#ece8e0", "#b9b4ab", "#8d887f", "#5f5b54", "#3a3733"],
    },
}

MAX_LANGS = 5

# Platform facts, sourced from the org's own platform-ops inventory
# (inventory/runtime-containers.yaml, services.yaml) and the ISONLINE
# application catalog. Static by nature - update them when the platform grows.
APPS_IN_PRODUCTION = 18
CONTAINERS_CATALOGED = 92


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def api(url, data=None):
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "blk-system"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    body = None
    if data is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())


def paged(url_template):
    items, page = [], 1
    while page <= 10:
        batch = api(url_template % page)
        items += batch
        if len(batch) < 100:
            break
        page += 1
    return items


def fetch_repos():
    """
    Every repo the credentials can see - private and org included when the
    token allows it, falling back to the public listing when it does not.
    """
    if TOKEN:
        try:
            repos = paged("https://api.github.com/user/repos?per_page=100"
                          "&affiliation=owner,organization_member&page=%d")
            if repos:
                return repos, True
        except urllib.error.HTTPError:
            pass          # a repo-scoped token cannot use /user/repos
    return paged("https://api.github.com/users/" + USER +
                 "/repos?per_page=100&type=owner&page=%d"), False


def fetch_profile():
    user = api("https://api.github.com/users/%s" % USER)
    repos, full_scope = fetch_repos()
    stars = sum(r.get("stargazers_count", 0) for r in repos)

    # Weight languages by bytes, not by repo count - one big service and one
    # throwaway script are not the same amount of a language.
    langs = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            for name, size in api(repo["languages_url"]).items():
                langs[name] = langs.get(name, 0) + size
        except urllib.error.URLError:
            continue

    return {
        "repos": len(repos) or user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "stars": stars,
        "contributions": fetch_contributions(),
        "languages": langs,
        "full_scope": full_scope,
    }


def fetch_contributions():
    """Contribution total for the last year. GraphQL only, so token-gated."""
    if not TOKEN:
        return None
    query = ("query($login:String!){user(login:$login){contributionsCollection"
             "{contributionCalendar{totalContributions}}}}")
    try:
        res = api("https://api.github.com/graphql",
                  {"query": query, "variables": {"login": USER}})
        return (res["data"]["user"]["contributionsCollection"]
                ["contributionCalendar"]["totalContributions"])
    except (urllib.error.URLError, KeyError, TypeError):
        return None


def top_languages(langs, limit=MAX_LANGS):
    """Top N by bytes, with the tail folded into 'Other' - never a 9th hue."""
    total = sum(langs.values())
    if not total:
        return []
    ranked = sorted(langs.items(), key=lambda kv: kv[1], reverse=True)
    head = ranked[:limit]
    tail = sum(v for _k, v in ranked[limit:])
    out = [(name, 100.0 * size / total) for name, size in head]
    if tail:
        out.append(("Other", 100.0 * tail / total))
    return out


# --------------------------------------------------------------------------- #
# render
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


def compact(n):
    if n >= 1000:
        return "%.1fk" % (n / 1000.0)
    return str(n)


def build(stats, theme):
    t = THEMES[theme]
    out = []

    # same hand-drawn edge as every other surface in the system
    passes = blk_style.sketch(W - EDGE_INSET * 2, H - EDGE_INSET * 2,
                              RADIUS, seed=71, passes=3)
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

    scope = "REPOSITORIES" if stats["full_scope"] else "PUBLIC REPOS"
    tiles = [(compact(stats["repos"]), scope),
             (compact(APPS_IN_PRODUCTION), "APPS IN PRODUCTION"),
             (compact(CONTAINERS_CATALOGED), "CONTAINERS IN OPERATION")]
    if stats["contributions"] is not None:
        tiles.append((compact(stats["contributions"]), "CONTRIBUTIONS / 1Y"))

    # A count has no shape to compare against - it is a number, so it is set as
    # one. No sparkline, no gauge, no ring.
    span = (W - 112) / len(tiles)
    for i, (value, label) in enumerate(tiles):
        x = 56 + span * i
        out.append(text(x, 118, value, 56, t["ink"], 900, 0))
        out.append(text(x + 2, 150, label, 14, t["sub"], 700, 3, MONO, 0.9))

    langs = stats["languages"]
    if not langs:
        return svg(out)

    out.append('<path d="M56 190H%d" stroke="%s" stroke-width="2"/>'
               % (W - 56, t["hair"]))
    out.append(text(56, 222, "LANGUAGES / BY BYTES WRITTEN", 13, t["sub"],
                    700, 3, MONO, 0.9))

    bar_x, bar_y, bar_w, bar_h, gap = 56.0, 238.0, float(W - 112), 18.0, 3.0
    radius = bar_h / 2
    cursor = bar_x
    for i, (_name, pct) in enumerate(langs):
        seg = bar_w * pct / 100.0
        width = max(2.0, seg - (gap if i < len(langs) - 1 else 0))
        # rounded data-ends only at the two ends of the whole bar
        out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" '
                   'rx="%.1f" ry="%.1f" fill="%s"/>'
                   % (cursor, bar_y, width, bar_h,
                      radius if i in (0, len(langs) - 1) else 2, 2,
                      t["ramp"][i % len(t["ramp"])]))
        cursor += seg

    # Monochrome cannot carry identity, so every segment is written out.
    lx = 56.0
    for i, (name, pct) in enumerate(langs):
        out.append('<rect x="%.1f" y="278" width="11" height="11" rx="3" '
                   'ry="3" fill="%s"/>'
                   % (lx, t["ramp"][i % len(t["ramp"])]))
        # never round a real share down to a flat 0%
        label = "%s %s%%" % (name, "%.1f" % pct if pct < 1 else "%.0f" % pct)
        out.append(text(lx + 19, 288, label, 14, t["ink"], 700, 0, MONO, 0.95))
        lx += 19 + 8.4 * len(label) + 30

    return svg(out)


def svg(body):
    th = H + MARGIN_BOTTOM
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" height="%d" role="img" '
            'aria-label="GitHub statistics for %s">%s</svg>'
            % (W, th, W, th, esc(USER), "".join(body)))


# --------------------------------------------------------------------------- #
def main():
    try:
        raw = fetch_profile()
    except urllib.error.HTTPError as err:
        sys.exit("GitHub API %s for %s - %s"
                 % (err.code, USER, err.reason))

    stats = dict(raw, languages=top_languages(raw["languages"]))
    print("repos=%(repos)d stars=%(stars)d followers=%(followers)d "
          "contributions=%(contributions)s full_scope=%(full_scope)s" % stats)
    if not stats["full_scope"]:
        print("note: public scope only - set METRICS_TOKEN to include "
              "private and org repositories")
    print("languages: " + ", ".join("%s %.1f%%" % lang
                                    for lang in stats["languages"]))

    out_dir = os.path.join(ROOT, "assets", "sections")
    os.makedirs(out_dir, exist_ok=True)

    # Never let a public-scope run clobber a full-scope card: the committed
    # numbers were produced with a personal token, and overwriting them with
    # the public-only count would silently shrink 64 repositories back to 13.
    existing = os.path.join(out_dir, "stats-light.svg")
    if not stats["full_scope"] and os.path.exists(existing):
        print("public scope + full-scope card already committed: keeping it. "
              "Set METRICS_TOKEN to refresh with full scope.")
        return

    for theme in THEMES:
        name = "stats-%s.svg" % theme
        markup = build(stats, theme)
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as fh:
            fh.write(markup)
        print("assets/sections/%-20s %6.1f KB" % (name, len(markup) / 1024))


if __name__ == "__main__":
    main()
