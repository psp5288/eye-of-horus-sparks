# Brand Guidelines — Eye of Horus: Sparks

> Minimal. Monochrome. Alive.

---

## Brand Identity

**Eye of Horus: Sparks** is a professional crowd-intelligence product. The brand communicates precision, authority, and quiet intelligence — never loud, never decorative. Every element earns its place.

### Brand Voice

| Attribute | Meaning | Example |
|-----------|---------|---------|
| **Precise** | Numbers, not vague claims | "93.3% backtest accuracy" not "highly accurate" |
| **Calm** | Even under critical alerts | "L3 · Critical — Intervene now" not "DANGER!!!" |
| **Directive** | Tells operators what to do | "Open gates 3 and 4" not "Consider opening gates" |
| **Minimal** | Says more by saying less | "See. Predict. Act." — three words, complete thought |

### Tagline

> **See. Predict. Act.**

Use this verbatim. Do not paraphrase. The three-beat structure is deliberate.

---

## The Mark — Wedjat Minimal

The Eye of Horus logo is a geometric reduction of the ancient Wedjat symbol to its five essential strokes:

```
① Upper lid arc    — the brow and eyelid in one unbroken curve
② Pupil            — solid disc, visual anchor of the mark
③ Lower lash wedge — diagonal at outer corner; gives direction
④ Spiral tail      — the only organic element; carries character
⑤ Vertical mark    — short drop below cheek; often removed at small sizes
```

### The Six Glyph Variants

| Variant | Strokes | Use Case |
|---------|---------|----------|
| **Wedjat** | All 5 | Primary mark, hero usage, print |
| **Essence** | Lid + pupil + tail | Secondary mark, medium contexts |
| **Brow** | Lid + pupil + lash | Alternative, no tail |
| **Linework** | All 5, outline only | Light backgrounds, watermarks |
| **Glyph** | 4 compressed | Favicon, 16–32px, app icons |
| **Symbol** | Lid + pupil only | Absolute minimum (≤16px) |

### Usage Rules

**Do:**
- Use `currentColor` so the mark inherits the text color
- Use single colour only — the mark is monochrome
- Maintain clear space equal to 25% of the mark's width on all sides
- Use **Wedjat** variant for anything ≥ 64px
- Use **Glyph** variant for anything 16–40px (favicon, app icon)

**Don't:**
- Add drop shadows, gradients, or glows to the mark
- Rotate or skew the mark
- Place the mark on a patterned background without sufficient contrast
- Stretch or non-uniformly scale the mark
- Use more than one colour within the mark

### Animated Mark

The mark has three sanctioned animation states:

| Animation | Trigger | Description |
|-----------|---------|-------------|
| **Blink** | Auto, 4–8s interval | Organic eye blink with pupil settle |
| **Hover** | Cursor enter | Squash-bounce, wordmark "Horus" reveals |
| **Idle** | Continuous | Pupil saccade + subtle breath |

**Severity states** (in-product use only, not brand materials):

| State | Level | Pupil Behaviour |
|-------|-------|----------------|
| Nominal | L0 · Calm | Slow calm pulse |
| Watch | L1 · Signals rising | Gentle lateral scan |
| Elevated | L2 · Pressure building | Erratic micro-movement |
| Critical | L3 · Intervene now | Rapid pulse, max urgency |

---

## Colour Palette

### Core (monochrome)

| Name | Hex | Usage |
|------|-----|-------|
| **Bone** | `#F4F1EA` | Light background, default foreground on dark |
| **Sand** | `#E8DFCE` | Light-variant background |
| **Graphite** | `#17181B` | Dark background (default theme) |
| **Ink** | `#0A0B0D` | Darkest background variant |

### Severity (functional, UI only)

| Level | Hex | Name |
|-------|-----|------|
| L0 Nominal | `#4CAF7D` | Green |
| L1 Watch | `#C8A84B` | Amber |
| L2 Elevated | `#E07A30` | Orange |
| L3 Critical | `#E05252` | Red |

**Rule:** Severity colours are used exclusively for status indicators and alerts. They never appear in the logo or typographic wordmark.

### Do not invent colours

The palette is intentionally small. Do not introduce additional colours without brand approval. If a situation seems to demand a new colour, question whether it's necessary.

---

## Typography

### Type Stack

| Role | Font | Weight | Usage |
|------|------|--------|-------|
| **Display / UI** | Inter Tight | 300 · 400 · 500 · 600 | Headlines, body, buttons |
| **Serif accent** | Fraunces (italic) | 300 | Italic moments in display text |
| **Data / labels** | JetBrains Mono | 400 · 500 | Scores, timestamps, badges, code |

### Typographic Pairings

**Display headline (correct):**
```
The Wedjat, reduced to its
five essential strokes.
         ↑ "five" in Fraunces italic
```

**Wordmark (correct):**
```
Eye of Horus   ← Inter Tight 300
      ↑ "Horus" in Fraunces italic
Sparks         ← JetBrains Mono, uppercase, muted
```

### Letter Spacing

| Context | Value |
|---------|-------|
| Display (large) | `-0.045em` |
| Heading | `-0.02em` |
| Body | `-0.01em` |
| Mono labels | `+0.08em` to `+0.14em` |
| Mono uppercase | `+0.12em` to `+0.18em` |

**Rule:** All Inter Tight text uses negative letter-spacing. JetBrains Mono labels use positive tracking (uppercase, small). Mixing these creates the editorial tension that makes the design feel designed.

---

## Iconography

The icon set follows the same hybrid rule as the Wedjat: **filled primary shape + stroke accents**.

- 24u grid
- Geometric spine with organic terminals (rounded stroke ends)
- `currentColor` only
- No fill + stroke on the same element (either filled OR stroked, not both at once — except as a designed accent)

Icons animate on hover with motion tied to their meaning (radar spins, signal waves, etc.).

---

## Layout Principles

### Grid
- Sharp corners throughout — `border-radius: 0` for containers
- 1px borders using `color-mix(in oklab, var(--fg) 14%, transparent)`
- Sections separated by thin hairlines, not whitespace alone
- Content constrained to `max-width: 1600px`

### Spacing
- Base unit: 8px
- Section gaps: 48–80px
- Component gaps: 12–24px
- Inner padding: 20–40px

### Density Modes
- **Compact** — reduced gaps (12px grid)
- **Regular** — default (20px grid)
- **Comfortable** — generous gaps (28px grid)

---

## Writing Style

### Severity Alerts

```
✓ Correct:
"Main stage area approaching critical density (85% capacity).
 Twitter shows increasing urgency. Activate crowd flow staff."

✗ Incorrect:
"WARNING: The crowd is getting very dangerous!! You should probably
 do something about the gates right away!"
```

### Metric Labels (JetBrains Mono, uppercase, muted)

```
✓  EVA · 14 MIN 7 SEC
✓  RISK · 0.72
✓  L2 · ELEVATED
✓  CONFIDENCE · 84%

✗  Evacuation Time: 14 minutes 7 seconds
✗  Risk Level: ELEVATED (72%)
```

### Recommendation Format (Claude output)

```
✓  Priority 1 · Open emergency gates 3 and 4
   Location: North perimeter
   Timing: At incident detection (T+0s)
   Impact: Reduces evacuation time by ~3 minutes

✗  You should consider opening some of the gates
   on the north side of the venue.
```

---

## Incorrect Usage Examples

| What | Wrong | Right |
|------|-------|-------|
| Logo colour | Blue/gold/coloured mark | Monochrome only |
| Logo background | On a photo without contrast | On solid Bone or Graphite |
| Severity colour in wordmark | "Eye of Horus" in green | Black or white only |
| Tagline variant | "See, Predict & Act!" | "See. Predict. Act." — exact |
| Metric display | Gaudy gradient speedometer | Clean doughnut, 1px stroke |
| Severity label | "DANGER" or "ALERT" | "L3 · Critical" |
