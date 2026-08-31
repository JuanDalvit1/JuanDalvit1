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

## 3. The section pattern

Every section of the README is the same object, only the words change:

```
 [index]  [FLAT TITLE]                                            [crown]
 ───────────────────────────────────────────────────────────────────────
 [lowercase mono subtitle]
```

- `index` — two digits, mono, 50% opacity. The catalogue, not the content.
- `title` — Arial Black, wide tracking, full ink. The order.
- `crown` — the drawn crown, right-anchored at the end of the rule. The mark.
- `rule` — a 2px hairline. The only geometry allowed.
- `subtitle` — mono, lowercase, secondary. The aside.

Both theme variants are generated from one definition, so a new section can
never drift from the rest.

**Adding a section:** append a tuple to `SECTIONS` in
[`tools/blk_sections.py`](../tools/blk_sections.py), rerun it, and reference the
pair with a `<picture>` block in the README.

---

## 4. Build

The committed assets are generated. Do not edit them by hand — edit the source
drawings or the scripts and rebuild.

```bash
python tools/blk_images.py && python tools/blk_sections.py
```

| Path | Role |
|---|---|
| `assets/blk/src-bust.png` | Source drawing — the bust under the floating crown |
| `assets/blk/src-arise.png` | Source drawing — the figure reaching for the crown |
| `tools/blk_images.py` | Derives the themed hero, closing mark and isolated crown |
| `tools/blk_sections.py` | Renders the section headers (crown embedded as a data URI) |
| `.github/workflows/snake.yml` | Renders the contribution graph as a snake, in BLK's palette, onto the `output` branch |

Sources are 8-bit grayscale — the artwork is strictly monochrome, so colour
channels would be redundant weight.

### Why the crown is embedded as a data URI

README images are served through GitHub's image proxy, which resolves the SVG
itself but not any relative `href` inside it. A linked crown would render as a
broken box for every visitor. Embedding is the only reliable option.

### Why every asset ships in two files

GitHub has no CSS in READMEs. Theme switching is done with `<picture>` and
`prefers-color-scheme`, which needs a real file per theme — hence `-light` and
`-dark` for every asset.
