# Design System — Eye of Horus: Sparks

Reference implementation: `frontend/css/style.css` + `frontend/js/logo.js`

---

## Color Palette

### Core

| Token | Value | Usage |
|-------|-------|-------|
| `--primary-color` | `#00D4FF` | CTAs, active states, highlights |
| `--secondary-color` | `#00A0CC` | Secondary buttons, hover states |
| `--bg-dark` | `#0F1419` | Page background (dark theme) |
| `--card-bg` | `#1A1F2E` | Card and panel backgrounds |
| `--text-primary` | `#FFFFFF` | Headings, primary text |
| `--text-secondary` | `#E0E0E0` | Body text, labels |
| `--border-color` | `#2A3042` | Borders, dividers |

### Severity States

| Level | Token | Hex | Usage |
|-------|-------|-----|-------|
| Nominal (L0) | `--sev-nominal` | `#4CAF7D` | LOW risk, safe state |
| Watch (L1) | `--sev-watch` | `#C8A84B` | MODERATE risk |
| Elevated (L2) | `--sev-elevated` | `#E07A30` | HIGH risk |
| Critical (L3) | `--sev-critical` | `#E05252` | CRITICAL / emergency |

### Status

| Token | Hex | Usage |
|-------|-----|-------|
| `--success` | `#10B981` | Successful actions, confirmations |
| `--warning` | `#F59E0B` | Warnings, caution states |
| `--error` | `#EF4444` | Errors, destructive actions |
| `--info` | `#3B82F6` | Info, neutral alerts |

---

## Typography

**Font imports** (Google Fonts):
- **Inter Tight** — UI labels, data, navigation
- **Fraunces** — Display headings, event names
- **JetBrains Mono** — Code, scores, data values

| Scale | Size | Weight | Font | Usage |
|-------|------|--------|------|-------|
| Display | 44px | 700 | Fraunces | Hero headings |
| H1 | 32px | 700 | Inter Tight | Page titles |
| H2 | 24px | 600 | Inter Tight | Section headings |
| H3 | 18px | 600 | Inter Tight | Card headings |
| Body | 16px | 400 | Inter Tight | Default body text |
| Small | 14px | 400 | Inter Tight | Labels, captions |
| Micro | 12px | 400 | Inter Tight | Timestamps, badges |
| Code | 14px | 400 | JetBrains Mono | Scores, API values |

---

## Component Library

### Button

```css
/* Primary */
.btn-primary {
  background: var(--primary-color);
  color: #000;
  padding: 10px 20px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-primary:hover { background: var(--secondary-color); }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; }

/* Secondary */
.btn-secondary {
  background: transparent;
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

/* Danger */
.btn-danger { background: var(--error); color: #fff; }
```

### Card

```css
.card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
}
```

### Alert

```css
.alert { padding: 12px 16px; border-left: 4px solid; }
.alert-success { border-color: var(--success); background: rgba(16,185,129,0.1); }
.alert-warning { border-color: var(--warning); background: rgba(245,158,11,0.1); }
.alert-error   { border-color: var(--error);   background: rgba(239,68,68,0.1); }
.alert-info    { border-color: var(--info);     background: rgba(59,130,246,0.1); }
```

### Severity Chip

```css
.sev-chip { padding: 6px 14px; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; }
.sev-chip[data-sev="nominal"]  { background: rgba(76,175,125,0.15); color: var(--sev-nominal); }
.sev-chip[data-sev="watch"]    { background: rgba(200,168,75,0.15);  color: var(--sev-watch); }
.sev-chip[data-sev="elevated"] { background: rgba(224,122,48,0.15);  color: var(--sev-elevated); }
.sev-chip[data-sev="critical"] { background: rgba(224,82,82,0.2);    color: var(--sev-critical); }
```

### KPI Score Card

```css
.score-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 20px;
  text-align: center;
}
.score-card .score-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 44px;
  font-weight: 700;
  color: var(--primary-color);
}
.score-card .score-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-secondary);
  margin-top: 4px;
}
```

### Signal Bar

```css
.signal-bar { height: 6px; background: var(--border-color); overflow: hidden; }
.signal-bar-fill { height: 100%; transition: width 0.3s ease, background 0.3s ease; }
/* Color by value: <0.3 → nominal, 0.3–0.6 → watch, 0.6–0.8 → elevated, >0.8 → critical */
```

### Modal

```css
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  padding: 32px;
  max-width: 560px; width: 90%;
}
```

---

## Responsive Breakpoints

| Name | Width | Description |
|------|-------|-------------|
| Mobile | `< 640px` | Single column, compact spacing |
| Tablet | `640–1024px` | 2-column grid |
| Desktop | `> 1024px` | Full 4-column dashboard layout |

---

## Dark Theme

Default theme is dark (`data-theme="dark"` on `<html>`). Light theme available via `data-theme="light"`.

```css
[data-theme="dark"] {
  --bg: #0F1419;
  --card-bg: #1A1F2E;
  --text-primary: #FFFFFF;
  --text-secondary: #E0E0E0;
}
[data-theme="light"] {
  --bg: #F8F9FA;
  --card-bg: #FFFFFF;
  --text-primary: #0F1419;
  --text-secondary: #4A5568;
}
```

---

## Accessibility

- Primary text contrast ratio: **12.6:1** (WCAG AAA)
- Minimum font size: 12px
- All interactive elements: focus rings via `:focus-visible`
- Reduced motion: `@media (prefers-reduced-motion: reduce)` disables all CSS animations
- Severity conveyed by color AND text label (never color alone)
