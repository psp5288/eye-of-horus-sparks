# Design System — Eye of Horus: Sparks

Reference implementation: `frontend/css/style.css` + `frontend/js/logo.js`

---

## Design Tokens

### Colour

```css
/* ── Palette ── */
--graphite: #17181B;   /* Dark background (default) */
--bone:     #F4F1EA;   /* Light background / dark-mode foreground */
--sand:     #E8DFCE;   /* Sand background variant */
--ink:      #0A0B0D;   /* Darkest background */

/* ── Theme-resolved ── */
--bg:   var(--graphite);   /* Background */
--fg:   var(--bone);       /* Foreground / text */
--card: #1B1C20;           /* Elevated surface */

/* ── Derived ── */
--line:        color-mix(in oklab, var(--fg) 14%, transparent);
--line-strong: color-mix(in oklab, var(--fg) 28%, transparent);
--muted:       color-mix(in oklab, var(--fg) 55%, transparent);

/* ── Severity ── */
--sev-nominal:  #4CAF7D;
--sev-watch:    #C8A84B;
--sev-elevated: #E07A30;
--sev-critical: #E05252;
```

### Themes

Apply via `data-theme` attribute on `<html>` or `<body>`:

| Attribute | Background | Foreground | Card |
|-----------|-----------|-----------|------|
| *(default)* | Graphite `#17181B` | Bone `#F4F1EA` | `#1B1C20` |
| `data-theme="light"` | Bone `#F4F1EA` | Graphite `#17181B` | `#F8F6F0` |
| `data-theme="sand"` | Sand `#E8DFCE` | Graphite `#17181B` | `#EFE6D3` |
| `data-theme="ink"` | Ink `#0A0B0D` | Bone `#F4F1EA` | `#111215` |

### Typography

```css
--font-sans:  'Inter Tight', system-ui, sans-serif;
--font-serif: 'Fraunces', Georgia, serif;
--font-mono:  'JetBrains Mono', ui-monospace, monospace;
```

Google Fonts import string:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700
            &family=JetBrains+Mono:wght@400;500
            &family=Fraunces:opsz,wght@9..144,300;9..144,400
            &display=swap" rel="stylesheet" />
```

### Spacing

```
Base unit: 8px

--space-1:  4px
--space-2:  8px
--space-3:  12px
--space-4:  16px
--space-5:  20px
--space-6:  24px
--space-8:  32px
--space-10: 40px
--space-12: 48px
--space-16: 64px
--space-20: 80px
```

### Border Radius

```css
--radius:    0;     /* Sharp corners — primary container style */
--radius-sm: 4px;   /* Small accents only (badges, chips) */
```

### Z-Index Scale

```css
--z-base:    0;
--z-panel:   10;
--z-header:  20;
--z-tweaks:  30;
--z-overlay: 100;
```

---

## Typography Scale

| Token | Font | Weight | Size | Tracking |
|-------|------|--------|------|----------|
| Display | Inter Tight | 300 | `clamp(52px, 7.5vw, 124px)` | `-0.045em` |
| Heading L | Inter Tight | 400 | `22px` | `-0.02em` |
| Heading M | Inter Tight | 400 | `18px` | `-0.02em` |
| Body | Inter Tight | 400 | `14px` | `-0.01em` |
| Body SM | Inter Tight | 400 | `13px` | `-0.01em` |
| Label | JetBrains Mono | 400–500 | `11px` | `+0.08–0.14em` |
| Label XS | JetBrains Mono | 400 | `10px` | `+0.10–0.18em` |
| Serif accent | Fraunces italic | 300 | *inherits* | `-0.03em` |

**Italic rule:** Use `font-family: var(--font-serif)` + `font-style: italic` for single-word or short phrase accents within Inter Tight display text. Never italic an entire paragraph.

---

## Component Library

### Panel

```html
<section class="panel">
  <div class="panel-header">
    <h2>Iris <span class="subtitle">Real-Time</span></h2>
    <button class="btn-icon">↻</button>
  </div>
  <!-- content -->
</section>
```

```css
.panel          → background: var(--card); border: 1px solid var(--line); padding: 24px;
.panel-header   → border-bottom: 1px solid var(--line); padding-bottom: 16px;
.subtitle       → font-mono, 11px, muted, uppercase, +0.1em tracking
```

### Buttons

```html
<!-- Primary (filled) -->
<button class="btn btn-primary">Run Simulation</button>

<!-- Default (ghost) -->
<button class="btn">Ask Claude</button>

<!-- Secondary (subtle border) -->
<button class="btn btn-secondary">Suggest Scenarios</button>

<!-- Monospace simulate -->
<button class="btn btn-simulate">▶ RUN SIMULATION</button>

<!-- Icon button -->
<button class="btn-icon">↻</button>
```

| Class | Background | Border | Text | Font |
|-------|-----------|--------|------|------|
| `.btn` | transparent | `--line-strong` | `--fg` | Inter Tight 500 |
| `.btn-primary` | `--fg` | `--fg` | `--bg` | Inter Tight 500 |
| `.btn-simulate` | `--fg` | `--fg` | `--bg` | JetBrains Mono 600, uppercase |
| `.btn-secondary` | transparent | `--line` | `--fg` | Inter Tight 500 |
| `.btn-icon` | none | none | `--muted` → `--fg` on hover | JetBrains Mono |

### Signal Bar

```html
<div class="signal-row">
  <span class="signal-name mono">Twitter</span>
  <div class="signal-bar-track">
    <div class="signal-bar" style="width: 42%"></div>
  </div>
  <span class="signal-val mono">42%</span>
</div>
```

Bar color transitions based on score:
- `< 0.3` → `--sev-nominal` (green)
- `0.3–0.6` → `--sev-watch` (amber)
- `0.6–0.8` → `--sev-elevated` (orange)
- `> 0.8` → `--sev-critical` (red)

The bar track is `3px tall`, no border-radius, inheriting the sharp-corner aesthetic.

### Severity Chip

```html
<div class="sev-chip active" data-sev="elevated">
  <div class="sev-mark">
    <!-- Wedjat SVG injected by JS -->
  </div>
  <span class="sev-lbl mono">L2 · Elevated</span>
</div>
```

Active chip: `border-color: var(--sev-color)` + pulsing dot (top-right).

### Alert Box

```html
<div class="alert-box">
  <span class="alert-icon">⚠</span>
  <span>Main stage density approaching critical threshold.</span>
</div>
```

Border and tinted background use `--sev-elevated` (orange) for warning-level alerts, `--sev-critical` for critical.

### Claude Output Block

```html
<div class="claude-output">
  <strong>Primary Risk:</strong> crowd_density<br><br>
  <strong>Alert:</strong> Main stage approaching 85% capacity…<br><br>
  <em>High confidence — 3 concordant signals.</em>
</div>
```

Rendered with a subtle `var(--fg) 5%` tinted background, 1px `--line` border.

### Result Cards

```html
<div class="result-grid">
  <div class="result-card">
    <div class="result-val">14m 7s</div>
    <div class="result-lbl mono">Evacuation Time</div>
  </div>
  <!-- × 4 -->
</div>
```

Grid uses `1px` gaps on a `--line`-coloured background to create hairline dividers between cards (no explicit border per card).

### Stats Bar

Full-width bottom strip. Same 1px gap / `--line` background trick as Result Cards. Values use Inter Tight 300 at 32px with `-0.05em` tracking.

---

## Logo Component

All variants are defined in `frontend/js/logo.js`.

```js
// Plain SVG (any size)
wedjatSvg('wedjat')              // returns SVG string
wedjatSvg('glyph', { size: 32 }) // 32×32 explicit

// Animated SVG (splits pupil into .pupil group)
wedjatAnimatedSvg('wedjat')

// Full animated logo component
const logo = new WedjatLogo(element, 'hover'); // 'blink' | 'hover' | 'idle'
logo.init('wedjat');
logo.rebuild('essence'); // swap glyph variant
```

### Placing the logo in HTML

```html
<!-- Header — hover variant (reveals "Horus") -->
<div class="eoh-logo" id="header-logo" data-variant="hover"
     style="width:40px;max-width:40px"></div>

<!-- Severity display — no variant (static) -->
<div class="sev-mark" id="sev-0">
  <!-- wedjatSvg('glyph') injected by JS -->
</div>
```

### Required CSS classes (already in style.css)

```css
.eoh-logo           /* container */
.glyph-body         /* squash/stretch group */
.pupil              /* independent animation */
.eoh-logo.blinking  /* triggers blink keyframe */
[data-variant="idle"]
[data-variant="hover"]
```

---

## Animation Reference

| Name | Class / Selector | Duration | Easing |
|------|-----------------|----------|--------|
| Blink | `.eoh-logo.blinking .glyph-body` | 380ms | `cubic-bezier(.55,0,.2,1)` |
| Pupil settle | `.eoh-logo.blinking .pupil` | 900ms | `cubic-bezier(.2,.9,.25,1)` |
| Idle breath | `[data-variant="idle"] .glyph-body` | 4.8s ∞ | `ease-in-out` |
| Pupil saccade | `[data-variant="idle"] .pupil` | 7s ∞ | `cubic-bezier(.4,0,.3,1)` |
| Squash-bounce | `[data-variant="hover"]:hover .glyph-body` | 750ms | `cubic-bezier(.3,1.4,.4,1)` |
| Wordmark reveal | `.wordmark-reveal` clip-path | 700ms | `cubic-bezier(.7,0,.2,1)` |
| Live badge pulse | `.badge-live::before` | 2s ∞ | `ease-in-out` |
| Severity pulse | `.sev-chip.active::before` | varies | `ease-in-out` |

All animations respect `@media (prefers-reduced-motion: reduce)`.

---

## Responsive Breakpoints

```css
@media (max-width: 960px) {
  /* Stack panels to single column */
  /* 2-col result grid */
  /* Wrap stats bar */
  /* 2-col severity row */
}
```

No breakpoints below 960px are currently defined — the layout is designed for event-control rooms (desktop-first).

---

## Accessibility

- All SVG marks include `aria-label="Eye of Horus mark"`
- Colour contrast: Bone on Graphite = 12.6:1 (exceeds WCAG AAA)
- Severity states use both colour AND label text (not colour alone)
- `prefers-reduced-motion` disables all animations
- Interactive elements have focus-visible outlines (browser default preserved)
- JetBrains Mono for data values aids readability for screenreaders (clear numeric rendering)

---

## Do / Don't Quick Reference

| ✓ Do | ✗ Don't |
|------|---------|
| Sharp corners on containers | Rounded cards (breaks aesthetic) |
| 1px hairline borders | 2px+ borders (too heavy) |
| Negative tracking on Inter Tight | Default/positive tracking on Inter Tight |
| `currentColor` on all SVG marks | Hard-coded hex in SVG fills |
| JetBrains Mono for scores/labels | Inter Tight for data readouts |
| Severity colours only for status | Severity colours in decorative contexts |
| `color-mix()` for transparency | `rgba()` with hardcoded values |
