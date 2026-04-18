/**
 * logo.js — Wedjat (Eye of Horus) SVG glyph system
 *
 * All glyphs on a 256×256 canvas, currentColor, single-colour.
 * Matches Logo Exploration v2 design spec.
 */

// ── Glyph path definitions ──────────────────────────────────

const WEDJAT_GLYPHS = {
  /** Full mark: upper lid + pupil + lower lash wedge + spiral tail + vertical mark */
  wedjat: {
    path: `
      <path d="M 20 118
               C 60 70, 120 64, 176 74
               C 206 80, 222 96, 226 114
               C 200 110, 168 104, 128 104
               C 88 104, 52 110, 20 118 Z"
            fill="currentColor"/>
      <circle cx="128" cy="120" r="16" fill="currentColor"/>
      <path d="M 20 126
               L 100 140
               L 58 188 Z"
            fill="currentColor"/>
      <path d="M 210 122
               C 232 128, 240 156, 222 176
               C 204 196, 176 192, 170 172
               C 166 158, 178 146, 192 150
               C 202 154, 204 166, 196 170"
            stroke="currentColor" stroke-width="11" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      <path d="M 102 152 L 92 214"
            stroke="currentColor" stroke-width="11" stroke-linecap="round"/>
    `,
    name: 'Wedjat',
    tag: 'Full · 5 strokes',
  },

  /** Essence: lid + pupil + spiral only */
  essence: {
    path: `
      <path d="M 28 118
               C 68 72, 124 66, 176 76
               C 204 82, 220 98, 226 114
               C 200 112, 168 106, 128 106
               C 90 106, 56 110, 28 118 Z"
            fill="currentColor"/>
      <circle cx="128" cy="118" r="15" fill="currentColor"/>
      <path d="M 208 124
               C 230 130, 238 156, 220 176
               C 202 194, 176 190, 170 170
               C 166 156, 180 146, 192 152"
            stroke="currentColor" stroke-width="11" stroke-linecap="round" fill="none"/>
    `,
    name: 'Essence',
    tag: 'Lid · pupil · tail',
  },

  /** Brow: almond silhouette + pupil + lash wedge, no tail */
  brow: {
    path: `
      <path d="M 24 122
               C 68 72, 124 66, 180 74
               C 216 80, 234 100, 234 120
               C 200 118, 160 114, 128 114
               C 92 114, 56 118, 24 122 Z"
            fill="currentColor"/>
      <circle cx="130" cy="118" r="15" fill="currentColor"/>
      <path d="M 24 130
               L 104 144
               L 60 192 Z"
            fill="currentColor"/>
    `,
    name: 'Brow',
    tag: 'Almond · lash',
  },

  /** Linework: outline-only stroke version */
  linework: {
    path: `
      <path d="M 24 120
               C 68 72, 124 66, 180 76
               C 214 82, 230 102, 228 122"
            stroke="currentColor" stroke-width="12" stroke-linecap="round" fill="none"/>
      <circle cx="128" cy="118" r="12" fill="currentColor"/>
      <path d="M 28 130 L 104 144 L 62 188 Z"
            stroke="currentColor" stroke-width="10" stroke-linejoin="round" stroke-linecap="round" fill="none"/>
      <path d="M 208 126
               C 230 134, 236 158, 220 176
               C 204 192, 180 188, 174 172"
            stroke="currentColor" stroke-width="12" stroke-linecap="round" fill="none"/>
      <path d="M 104 152 L 94 212"
            stroke="currentColor" stroke-width="11" stroke-linecap="round"/>
    `,
    name: 'Linework',
    tag: 'Outline only',
  },

  /** Symbol: lid + pupil only — simplest */
  symbol: {
    path: `
      <path d="M 28 120
               C 72 72, 128 66, 184 76
               C 216 82, 232 102, 232 122
               C 196 118, 160 114, 128 114
               C 92 114, 58 118, 28 120 Z"
            fill="currentColor"/>
      <circle cx="130" cy="120" r="16" fill="currentColor"/>
    `,
    name: 'Symbol',
    tag: 'Lid · pupil',
  },

  /** Glyph: favicon-safe compressed version */
  glyph: {
    path: `
      <path d="M 28 132
               C 72 86, 128 80, 180 88
               C 214 94, 226 112, 226 128
               C 196 126, 160 122, 128 122
               C 94 122, 60 124, 28 132 Z"
            fill="currentColor"/>
      <circle cx="128" cy="124" r="17" fill="currentColor"/>
      <path d="M 28 138 L 102 148 L 66 188 Z" fill="currentColor"/>
      <path d="M 206 134
               C 226 142, 228 166, 214 178
               C 200 190, 184 182, 184 170"
            stroke="currentColor" stroke-width="14" stroke-linecap="round" fill="none"/>
    `,
    name: 'Glyph',
    tag: 'Favicon-safe',
  },
};

/**
 * Build a plain SVG string for a glyph key.
 * @param {string} key - glyph key from WEDJAT_GLYPHS
 * @param {object} opts
 * @param {number|null} opts.size - explicit width/height in px
 * @param {number} opts.scaleStroke - multiply all stroke-width values
 * @returns {string} SVG HTML string
 */
function wedjatSvg(key, { size = null, scaleStroke = 1 } = {}) {
  const glyph = WEDJAT_GLYPHS[key] || WEDJAT_GLYPHS.wedjat;
  let body = glyph.path;

  if (scaleStroke !== 1) {
    body = body.replace(/stroke-width="(\d+(?:\.\d+)?)"/g,
      (_, w) => `stroke-width="${(parseFloat(w) * scaleStroke).toFixed(2)}"`);
  }

  const sizeAttr = size ? ` width="${size}" height="${size}"` : '';
  return `<svg viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg" fill="none" aria-label="Eye of Horus mark"${sizeAttr}>${body}</svg>`;
}

/**
 * Build an SVG with independently animatable `.glyph-body` and `.pupil` groups.
 * Used for the animated logo variants (blink, hover, idle).
 */
function wedjatAnimatedSvg(key) {
  const glyph = WEDJAT_GLYPHS[key] || WEDJAT_GLYPHS.wedjat;
  const body = glyph.path;

  // Extract the circle (pupil) so it can be animated separately
  const pupilMatch = body.match(/<circle[^>]*r="1[0-9][^"]*"[^>]*\/>/);
  const pupilSvg = pupilMatch
    ? pupilMatch[0].replace('<circle', '<circle class="pupil"')
    : '';
  const rest = pupilMatch ? body.replace(pupilMatch[0], '') : body;

  return `<svg viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg" fill="none" aria-label="Eye of Horus mark">
    <g class="glyph-body">
      ${rest}
      ${pupilSvg}
    </g>
  </svg>`;
}

/**
 * WedjatLogo — animated logo component.
 *
 * Supports three variants:
 *   'blink'  — auto-blinks every 4.5–8s with occasional double-blink
 *   'hover'  — squash-bounce + wordmark reveal on hover
 *   'idle'   — continuous pupil saccade + breath
 *
 * Usage:
 *   const logo = new WedjatLogo(document.getElementById('my-logo'), 'hover');
 *   logo.init('wedjat');
 */
class WedjatLogo {
  constructor(el, variant = 'blink') {
    this.el = el;
    this.variant = variant;
    this._blinkTimer = null;
  }

  init(glyphKey = 'wedjat') {
    this.glyphKey = glyphKey;
    this.el.dataset.variant = this.variant;
    this.el.classList.add('eoh-logo');

    if (this.variant === 'hover') {
      this.el.innerHTML = `
        <div class="wordmark-wrap">${wedjatAnimatedSvg(glyphKey)}</div>
        <div class="wordmark-reveal"><i>Horus</i></div>`;
    } else {
      this.el.innerHTML = wedjatAnimatedSvg(glyphKey);
    }

    if (this.variant === 'blink') {
      this._scheduleBlink();
    }
  }

  rebuild(glyphKey) {
    if (this._blinkTimer) {
      clearTimeout(this._blinkTimer);
      this._blinkTimer = null;
    }
    this.init(glyphKey);
  }

  _scheduleBlink() {
    const wait = 4500 + Math.random() * 3500;
    this._blinkTimer = setTimeout(() => {
      this.el.classList.add('blinking');
      const doubleBlink = Math.random() < 0.2;
      setTimeout(() => {
        this.el.classList.remove('blinking');
        if (doubleBlink) {
          setTimeout(() => {
            this.el.classList.add('blinking');
            setTimeout(() => {
              this.el.classList.remove('blinking');
              this._scheduleBlink();
            }, 420);
          }, 180);
        } else {
          this._scheduleBlink();
        }
      }, 420);
    }, wait);
  }
}

// Export for use in other modules
window.WEDJAT_GLYPHS = WEDJAT_GLYPHS;
window.wedjatSvg = wedjatSvg;
window.wedjatAnimatedSvg = wedjatAnimatedSvg;
window.WedjatLogo = WedjatLogo;
