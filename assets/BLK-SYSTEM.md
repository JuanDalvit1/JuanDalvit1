# BLK.SYSTEM

The design system behind this profile. One concept — **BLK.ENTITY** — rendered
with enough rules that every section looks like it came from the same hand.

---

## 1. The concept

BLK.ENTITY is not a character. It is an existential concept translated into
tactile art.

- **Immaterial and void.** No flesh, no bone, no muscle, no face. A featureless
  silhouette: the anonymous, the observer, raw presence.
- **The myth of the crown.** The imperfect, floating crown is sovereignty over
  one's own chaos. It never touches the head — it hovers a millimetre away, a
  tactile halo. A permanent state of ascension (*I arise*), not an achievement.
- **Projections.** The small figures, the smoke and the dust are extensions of
  BLK itself — fragments of thought, noise, other manifestations of the same
  void.

Everything on this profile is signed **BLK**. Everything on it is the work of
**Juan Dalvit**, engineer. The mark is the voice; the work is professional.

---

## 2. Visual language

| Rule | Meaning |
|---|---|
| **Organic scrawl** | The body is a dense, tangled web of chalk, graphite and ink. No clean vector strokes, no perfect digital fills. Anatomy is implied by *density*, never by outline. |
| **Matter, not glow** | No bloom, no neon, no artificial light. White is dusty chalk or matte graphite; black is dense ink or charcoal. Paper tooth, organic grain and tactile dust on every surface. |
| **Absolute monochrome** | Black, white, and only the greys produced by accumulated charcoal haze. Never a hue. |
| **Flat typography** | Heavy, direct, wide-tracked. No bevel, no drop shadow, no outline. The brutal contrast between geometric type and scrawled chaos *is* the design. |

### Palette

| Token | Light | Dark |
|---|---|---|
| paper | `#f4f2ee` | `#0a0a0a` |
| ink (stroke) | `#101010` | `#ece8e0` |
| sub (secondary text) | `#57534c` | `#8d887f` |
| rule (hairlines) | `#cfcabf` | `#2b2b2b` |

The two themes are not two designs. The drawing's luminance is read as **ink
coverage** and re-inked per theme — nanquim on paper, or chalk on charcoal.

---

## 3. The card

Every surface on the profile is the same object — the banner, each section
header, the stack grid, the signals card. Nothing floats loose on the page.

```
.------------------------------------------------------------------.
|  [index]  [FLAT TITLE]                                   [crown]  |
|  [lowercase mono subtitle]                                        |
`------------------------------------------------------------------'
```

- `index` — two digits, mono, 50% opacity. The catalogue, not the content.
- `title` — Arial Black, wide tracking, full ink. The order.
- `crown` — the drawn crown, right-anchored. The mark.
- `subtitle` — mono, lowercase, secondary. The aside, held *inside* the card.

### Titles are keywords; subtitles carry the voice

A section title is the line a recruiter or a peer scans, and the line a search
engine indexes. It gets spent on the plain term — `TECH STACK`, `GITHUB STATS`,
`CONTRIBUTION GRAPH` — never on flavour. `MANIFESTO` and `THE SERPENT` read
well and find nobody.

The voice moves down one line, into the subtitle, where it costs nothing:

| Title (findable) | Subtitle (the voice) |
|---|---|
| `WHAT I BUILD` | ai systems, automation, and the platforms that keep them running |
| `CONTRIBUTION GRAPH` | the void devours every commit / rebuilt every 12h |

The mark is the artwork. It does not need to be spelled out on the page, and
the pseudonym is never set as a label on the banner.

### The organic edge

The border is drawn, not computed — a rounded rectangle that wobbles like a
hand traced it around a ruler. Two rules make it read as hand-drawn instead of
as noise:

- **The wobble is low frequency.** Independent jitter per point looks fuzzy and
  digital. A smooth offset resampled every few dozen pixels gives the slow
  drift of a hand that cannot hold a straight line.
- **It is drawn more than once.** A pen never lands twice in the same place, so
  each pass gets its own offsets and slightly lower opacity.

That outline is also the card's **silhouette**, not a stroke laid over a
geometric shape — so the corners themselves are organic, and the page
background shows through them. One implementation
([`tools/blk_style.py`](../tools/blk_style.py)) feeds both the PNG banners and
the SVG cards, so the edge cannot drift between formats.

Every card carries its own seed, so no two edges are the same line.

**Adding a section:** append a tuple to `SECTIONS` in
[`tools/blk_sections.py`](../tools/blk_sections.py), rerun it, and reference the
pair with a `<picture>` block in the README.

**Changing the stack:** edit `STACK` in
[`tools/blk_stack.py`](../tools/blk_stack.py) and rerun. It is the single source
of truth for the chip grid.

> Anything set in the mono stack must use **ASCII separators only**. The middle
> dot renders as tofu in the mono fallback on some platforms — use `/` or `-`.

---

## 4. Build

The committed assets are generated. Do not edit them by hand — edit the source
drawings or the scripts and rebuild.

```bash
python tools/blk_images.py && python tools/blk_sections.py && python tools/blk_stack.py && python tools/blk_stats.py
```

| Path | Role |
|---|---|
| `assets/blk/src-bust.png` | Source drawing — the bust under the floating crown |
| `assets/blk/src-arise.png` | Source drawing — the figure reaching for the crown |
| `tools/blk_style.py` | The shared hand-drawn edge, used by every card in both formats |
| `tools/blk_images.py` | Derives the themed hero, closing mark and isolated crown |
| `tools/blk_sections.py` | Renders the section headers (crown embedded as a data URI) |
| `tools/blk_stack.py` | Renders the stack chip grid; icons inlined from Simple Icons |
| `tools/blk_stats.py` | Renders the signals card from the GitHub API |
| `tools/simple-icons.json` | Committed icon cache, so builds work offline |
| `.github/workflows/snake.yml` | Redraws the snake onto `output` and the signals card onto `main`, every 12h |

Sources are 8-bit grayscale — the artwork is strictly monochrome, so colour
channels would be redundant weight.

### Why the crown is embedded as a data URI

README images are served through GitHub's image proxy, which resolves the SVG
itself but not any relative `href` inside it. A linked crown would render as a
broken box for every visitor. Embedding is the only reliable option.

### Why nothing is fetched at read time

The obvious way to build this page is `github-readme-stats` and `shields.io`
badge URLs. The public github-readme-stats instance answered **503 on every
attempt** while this profile was being built, and a broken image on a profile
reads as neglect. So the numbers, the chips and the snake are all generated
into committed files by [`snake.yml`](../.github/workflows/snake.yml). The
README depends on nobody's uptime but GitHub's own.

### Why the data drives the form, not the decoration

Four counts have no shape to compare against, so they are stat tiles — a
number set as a number, no gauge and no ring. The language split is
parts-of-a-whole, so it is one stacked bar. And because the system is
monochrome by definition, colour can never carry identity: every bar segment
and every chip is labelled in words.

### Why every asset ships in two files

GitHub has no CSS in READMEs. Theme switching is done with `<picture>` and
`prefers-color-scheme`, which needs a real file per theme — hence `-light` and
`-dark` for every asset.
