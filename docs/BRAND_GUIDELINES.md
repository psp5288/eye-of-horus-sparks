# Brand Guidelines — Eye of Horus: Sparks

> Trustworthy. Tech-forward. Energetic. Clear.

---

## Brand Voice

| Trait | Description | Example |
|-------|-------------|---------|
| **Trustworthy** | Data-grounded. No speculation. | "92.7% backtest accuracy across 3 events." |
| **Tech-forward** | Precise language. Comfortable with complexity. | "10,000-agent swarm simulation" not "AI magic" |
| **Energetic** | Active voice. Short sentences. Action-oriented. | "See. Predict. Act." not "Monitoring and predicting events" |
| **Clear** | No jargon without explanation. Scannable. | Labels on every score. Tooltips on technical terms. |

### Tagline

**"See. Predict. Act."** — Use verbatim only. Never paraphrase. Three words, three periods.

### Do / Don't

| Do | Don't |
|----|-------|
| "Crowd safety intelligence" | "AI-powered magic" |
| "92.7% backtest accuracy" | "Nearly perfect accuracy" |
| "CRITICAL risk detected" | "Something might be wrong" |
| "Deploy 4 staff to Gate 3" | "Consider adding more staff" |

---

## Logo — The Wedjat Mark

The Eye of Horus (Wedjat) is our symbol. Six variants for different contexts:

| Variant | When to use |
|---------|-------------|
| `wedjat` (full, 5 strokes) | Primary mark, hero, marketing |
| `essence` (lid + pupil + tail) | Header, nav, mid-size contexts |
| `brow` (lid + pupil + lash) | Compact contexts, app icon |
| `linework` (outline only) | Watermarks, backgrounds |
| `symbol` (lid + pupil only) | Very small sizes (16–24px) |
| `glyph` (compressed) | Favicon (16px), tiny inline use |

### Sizing Rules

- Minimum size: 16px (glyph only below 24px)
- Clear space: 0.5× mark width on all sides
- Never stretch or distort aspect ratio
- Never add drop shadows or 3D effects

### Animated States

| State | Behavior | Usage |
|-------|----------|-------|
| `blink` | Auto blink every 4–8s | Header logo — idle |
| `hover` | Squash + wordmark reveal on hover | CTAs, interactive logo |
| `idle` | Pupil saccade + breath | Ambient presence |
| Severity pulse | Pupil animation tied to risk level | Severity chips |

---

## Color Usage Rules

| Color | Role | Rules |
|-------|------|-------|
| `#00D4FF` (Primary) | Active states, CTAs, scores | Use sparingly — maximum 20% of UI surface |
| `#0F1419` (BG Dark) | Page background | Never use on text |
| `#1A1F2E` (Card BG) | Cards, panels | Do not lighten further |
| `#FFFFFF` (Text Primary) | Headings, key values | Never use on white/light bg |
| `#4CAF7D` (Nominal) | LOW / safe state | Only for safety status — never decorative |
| `#E05252` (Critical) | CRITICAL state | Never use for non-safety meaning |

Severity colors (`#4CAF7D`, `#C8A84B`, `#E07A30`, `#E05252`) are reserved for risk communication. Do not repurpose them for decorative use.

---

## Typography Pairing

### Display pairing (hero sections)

```
Fraunces 700 (44px) — Event name
Inter Tight 400 (16px) — Supporting detail
```

### Dashboard pairing (data-heavy)

```
Inter Tight 600 (18px) — Card heading
JetBrains Mono 700 (44px) — Score value
Inter Tight 400 (12px) — Label / unit
```

### Alert pairing

```
Inter Tight 600 (14px) — Alert title
Inter Tight 400 (14px) — Alert body
```

---

## Icon Guidelines

- Use outline-style icons at 20px for UI, 16px for labels
- Primary color for active/selected, `--text-secondary` for inactive
- Never use filled icons alongside outline icons in the same context
- The Wedjat mark is not an icon — it's the brand mark; treat it separately

---

## What Not to Do

- Do not use the Wedjat mark in red or green (reserved for severity states)
- Do not use gradient fills on the Wedjat paths
- Do not place the mark on busy photographic backgrounds without a dark overlay
- Do not mix Fraunces with non-system serif fonts
- Do not use the tagline with a different cadence ("See, Predict, Act" — wrong punctuation)
- Do not describe risk scores without confidence percentages in user-facing copy
