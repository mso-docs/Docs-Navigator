#!/usr/bin/env python3
"""Docs Navigator MCP: a searchable documentation set that is also an MCP server.

Run locally:   python app.py
MCP endpoint:  http://127.0.0.1:7860/gradio_api/mcp/   (schema at /gradio_api/mcp/schema)
"""

from __future__ import annotations

import html
import os

import gradio as gr
from dotenv import load_dotenv

from docs_navigator import __version__, tools
from docs_navigator.connect import client_configs, mcp_url
from docs_navigator.llm import LLMUnavailable, answer_question, configured_models

load_dotenv()

TITLE = "Docs Navigator MCP"
TAGLINE = (
    "Chart a course through the docs. Search here, then take the same compass "
    "into Cursor, Claude, or VS Code over MCP."
)
EXAMPLES = [
    "How do I deploy Aurora AI?",
    "context window size",
    "troubleshooting API timeouts",
    "safety guardrails",
]
SERVER_TOKEN = os.getenv("DOCSNAV_SERVER_TOKEN", "")  # self-hosting only; never set on the public Space
# "Sign in with Hugging Face" only works on a Space. Locally Gradio would need a logged-in machine,
# so the button stays off unless DOCSNAV_ENABLE_LOGIN=1.
LOGIN = bool(os.getenv("SPACE_ID")) or os.getenv("DOCSNAV_ENABLE_LOGIN") == "1"

# Fraunces is the display face (an atlas / field-guide serif). Figtree is the body.
# Loaded here as well as in the theme, so the hero title still renders if Blocks head is dropped.
HEAD = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Source+Code+Pro:wght@500;600&display=swap" rel="stylesheet">
"""

NAV_THEME = gr.themes.Base(
    primary_hue="indigo",
    secondary_hue="purple",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Figtree"), "ui-sans-serif", "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Source Code Pro"), "ui-monospace", "monospace"],
    radius_size="lg",
).set(
    body_background_fill="#f5f4fb",
    body_background_fill_dark="#0c0a1d",
    body_text_color="#1e1b4b",
    body_text_color_dark="#eef2ff",
    background_fill_primary="#ffffff",
    background_fill_primary_dark="#16132c",
    background_fill_secondary="#eef2ff",
    background_fill_secondary_dark="#1c1836",
    border_color_accent="#6d28d9",
    border_color_accent_dark="#c4b5fd",
    border_color_primary="#ddd9f3",
    border_color_primary_dark="rgba(165,180,252,0.22)",
    button_primary_background_fill="#4338ca",
    button_primary_background_fill_hover="#3730a3",
    button_primary_background_fill_dark="#818cf8",
    button_primary_background_fill_hover_dark="#a5b4fc",
    button_primary_text_color="#ffffff",
    button_primary_text_color_hover="#ffffff",
    button_primary_text_color_dark="#1e1b4b",
    button_primary_text_color_hover_dark="#1e1b4b",
    button_secondary_background_fill="#eef2ff",
    button_secondary_background_fill_hover="#e0e7ff",
    button_secondary_background_fill_dark="#221e40",
    button_secondary_background_fill_hover_dark="#2a2550",
    button_secondary_text_color="#3730a3",
    button_secondary_text_color_dark="#e0e7ff",
    link_text_color="#3730a3",
    link_text_color_dark="#c4b5fd",
    block_radius="16px",
    button_large_radius="14px",
    button_small_radius="999px",
)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Source+Code+Pro:wght@500;600&display=swap');

:root {
  --dn-ink: #1e1b4b;
  --dn-muted: #57538a;
  --dn-bg: #f5f4fb;
  --dn-surface: #ffffff;
  --dn-line: #ddd9f3;
  --dn-wash: #eef2ff;
  --dn-indigo: #4338ca;
  --dn-indigo-2: #3730a3;
  --dn-indigo-950: #1e1b4b;
  --dn-violet: #6d28d9;
  --dn-star: #e0e7ff;
  --dn-hero-text: #eef2ff;
  --dn-hero-muted: #c7d2fe;
  --dn-glow: rgba(109, 40, 217, 0.22);
  --dn-display: "Fraunces", Georgia, "Iowan Old Style", "Palatino Linotype", serif;
  --dn-body: "Figtree", ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
  --dn-mono: "Source Code Pro", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}

.dark {
  --dn-ink: #eef2ff;
  --dn-muted: #b4b0d8;
  --dn-bg: #0c0a1d;
  --dn-surface: #16132c;
  --dn-line: rgba(165, 180, 252, 0.22);
  --dn-wash: #1c1836;
  --dn-indigo: #818cf8;
  --dn-indigo-2: #a5b4fc;
  --dn-violet: #c4b5fd;
  --dn-glow: rgba(129, 140, 248, 0.32);
}

html, body, .gradio-container, .gradio-container .main, .app, .contain {
  font-family: var(--dn-body) !important;
  background: var(--dn-bg) !important;
  color: var(--dn-ink) !important;
}

body, html {
  background:
    radial-gradient(900px 420px at 100% -8%, rgba(109, 40, 217, 0.10), transparent 55%),
    radial-gradient(620px 340px at -8% 0%, rgba(67, 56, 202, 0.10), transparent 50%),
    var(--dn-bg) !important;
}
.dark body, .dark html, body.dark, html.dark {
  background:
    radial-gradient(900px 420px at 100% -8%, rgba(167, 139, 250, 0.16), transparent 55%),
    radial-gradient(620px 340px at -8% 0%, rgba(99, 102, 241, 0.14), transparent 50%),
    var(--dn-bg) !important;
}

.gradio-container {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 1080px !important;
  margin: 0 auto !important;
  box-sizing: border-box;
  padding: 18px 16px 36px !important;
  background: transparent !important;
}
.gradio-container a { color: var(--dn-indigo-2) !important; }
footer { display: none !important; }

/* ---- Hero: a night-sky chart, in both themes, like the landing-page header ---- */
#dn-hero {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  color: var(--dn-hero-text);
  border-radius: 24px;
  padding: 28px 30px 26px;
  margin-bottom: 16px;
  background:
    radial-gradient(680px 260px at 100% -10%, rgba(167, 139, 250, 0.42), transparent 55%),
    radial-gradient(520px 240px at -8% 120%, rgba(99, 102, 241, 0.38), transparent 55%),
    linear-gradient(160deg, #1e1b4b 0%, #312e81 42%, #4338ca 74%, #6d28d9 100%);
  box-shadow: 0 18px 40px rgba(49, 46, 129, 0.28);
  border: 1px solid rgba(224, 231, 255, 0.16);
}
#dn-hero .dn-stars-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    radial-gradient(1.4px 1.4px at 8% 22%, #fff, transparent),
    radial-gradient(1px 1px at 16% 68%, #e0e7ff, transparent),
    radial-gradient(1.6px 1.6px at 24% 38%, #fff, transparent),
    radial-gradient(1px 1px at 33% 14%, #c7d2fe, transparent),
    radial-gradient(1.2px 1.2px at 41% 78%, #fff, transparent),
    radial-gradient(1px 1px at 52% 30%, #e0e7ff, transparent),
    radial-gradient(1.5px 1.5px at 63% 58%, #fff, transparent),
    radial-gradient(1px 1px at 71% 18%, #c7d2fe, transparent),
    radial-gradient(1.3px 1.3px at 78% 82%, #fff, transparent),
    radial-gradient(1px 1px at 86% 44%, #e0e7ff, transparent),
    radial-gradient(1.6px 1.6px at 93% 12%, #fff, transparent),
    radial-gradient(1px 1px at 96% 70%, #c7d2fe, transparent);
  animation: dn-drift-stars 48s linear infinite;
  opacity: 0.9;
}
#dn-hero .dn-hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 22px;
  align-items: center;
}
#dn-hero h1 {
  margin: 0 0 8px;
  font-family: var(--dn-display) !important;
  font-weight: 600;
  font-size: clamp(2rem, 5vw, 3.05rem);
  letter-spacing: -0.03em;
  line-height: 1.08;
  color: #fff !important;
}
#dn-hero .eyebrow {
  margin: 0 0 6px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--dn-hero-muted);
}
#dn-hero p.lede {
  margin: 0;
  color: var(--dn-hero-muted);
  font-size: 1.06rem;
  max-width: 40rem;
  line-height: 1.5;
}
#dn-hero .chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}
#dn-hero .chip {
  background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.22);
  color: #fff;
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}
#dn-hero .mcp-pill {
  display: inline-block;
  margin-left: 10px;
  vertical-align: middle;
  font-family: var(--dn-body);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 3px 9px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.35);
  color: #fff;
  position: relative;
  top: -0.28em;
}

/* Compass + constellation mark */
.dn-mark { width: 118px; height: 118px; display: block; color: #eef2ff; filter: drop-shadow(0 0 12px rgba(196,181,253,0.45)); }
.dn-compass { transform-origin: 80px 80px; animation: dn-spin 64s linear infinite; }
.dn-star { transform-origin: center; animation: dn-twinkle 3.4s ease-in-out infinite; }
.dn-star:nth-child(2n) { animation-delay: 0.5s; }
.dn-star:nth-child(3n) { animation-delay: 1.1s; }
.dn-star:nth-child(4n) { animation-delay: 1.8s; }
.dn-star:nth-child(5n) { animation-delay: 2.4s; }

@keyframes dn-spin { to { transform: rotate(360deg); } }
@keyframes dn-twinkle {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
@keyframes dn-drift-stars {
  from { transform: translate3d(0, 0, 0); }
  to { transform: translate3d(-18px, 10px, 0); }
}
@keyframes dn-needle {
  from { transform: rotate(-18deg); }
  to { transform: rotate(18deg); }
}

/* ---- Search console ---- */
#dn-search {
  background: var(--dn-surface);
  border: 1px solid var(--dn-line);
  border-radius: 20px;
  padding: 10px 12px;
  box-shadow: 0 8px 28px rgba(30, 27, 75, 0.06);
}
#dn-search textarea, #dn-search input, #dn-query textarea, #dn-query input {
  font-size: 1.08rem !important;
  font-family: var(--dn-body) !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}
#dn-query, #dn-query .block, #dn-query label, #dn-query .input-container,
#dn-query .show_textbox_border {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}
@media (min-width: 801px) {
  #dn-search .styler {
    display: grid !important;
    grid-template-columns: 1fr auto auto;
    align-items: center;
    gap: 0 10px;
  }
  #dn-search-actions {
    display: contents !important;
    margin-top: 0 !important;
  }
  #dn-search-actions button {
    width: auto !important;
    min-width: 132px;
  }
}
#dn-search textarea:focus, #dn-search input:focus,
#dn-search:focus-within {
  outline: none;
}
#dn-search:focus-within {
  border-color: var(--dn-violet);
  box-shadow: 0 0 0 4px var(--dn-glow), 0 8px 28px rgba(30, 27, 75, 0.08);
}
#dn-search button {
  font-family: var(--dn-body) !important;
  font-weight: 700 !important;
  letter-spacing: 0.01em;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease !important;
}
#dn-search button:hover { transform: translateY(-1px); }
#dn-search button:active { transform: translateY(0); }
#dn-search button:focus-visible,
#dn-suggest button:focus-visible,
#dn-hero + * button:focus-visible {
  outline: 2px solid var(--dn-violet) !important;
  outline-offset: 2px !important;
}

/* Example chips */
#dn-suggest {
  margin: 4px 0 2px !important;
}
#dn-suggest .dn-suggest-label {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--dn-muted);
  margin: 8px 2px 0;
}
#dn-suggest button,
button.dn-chip {
  font-family: var(--dn-body) !important;
  font-weight: 600 !important;
  font-size: 0.88rem !important;
  border-radius: 999px !important;
  border: 1px solid var(--dn-line) !important;
  background: var(--dn-surface) !important;
  color: var(--dn-indigo-2) !important;
  box-shadow: none !important;
  min-height: 36px !important;
  padding: 4px 14px !important;
  transition: transform 0.16s ease, background 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease !important;
}
#dn-suggest button:hover,
button.dn-chip:hover {
  transform: translateY(-1px);
  background: var(--dn-wash) !important;
  border-color: var(--dn-indigo) !important;
  box-shadow: 0 6px 16px var(--dn-glow) !important;
}

.dn-note {
  color: var(--dn-muted);
  font-size: 0.9rem;
  margin: 8px 4px 2px;
  line-height: 1.45;
}
.dn-note code {
  font-family: var(--dn-mono);
  font-size: 0.86em;
  background: var(--dn-wash);
  padding: 1px 6px;
  border-radius: 6px;
}

/* ---- Results ---- */
.dn-hit {
  border: 1px solid var(--dn-line);
  border-left: 4px solid var(--dn-indigo);
  border-radius: 14px;
  padding: 14px 16px 14px 18px;
  margin: 12px 0;
  background: var(--dn-surface);
  box-shadow: 0 4px 14px rgba(30, 27, 75, 0.04);
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.dn-hit:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 22px var(--dn-glow);
}
.dn-hit .meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
  font-size: 0.82rem;
  color: var(--dn-muted);
}
.dn-file {
  background: var(--dn-wash);
  color: var(--dn-indigo-2);
  border-radius: 6px;
  padding: 1px 8px;
  font-weight: 600;
  font-family: var(--dn-mono);
  font-size: 0.8rem;
}
.dn-score { color: var(--dn-muted); }
.dn-hit mark {
  background: rgba(109, 40, 217, 0.18);
  color: inherit;
  border-radius: 3px;
  padding: 0 2px;
}
.dark .dn-hit mark { background: rgba(167, 139, 250, 0.28); }

.dn-answer {
  border: 1px solid var(--dn-violet);
  background: var(--dn-wash);
  color: var(--dn-ink);
  border-radius: 16px;
  padding: 16px 18px;
  margin: 10px 0 14px;
  box-shadow: 0 8px 24px var(--dn-glow);
}
.dn-answer::before {
  content: "From the chart";
  display: block;
  font-family: var(--dn-display);
  font-weight: 600;
  font-size: 0.95rem;
  letter-spacing: -0.01em;
  margin-bottom: 6px;
  color: var(--dn-indigo-2);
}

.dn-empty {
  text-align: center;
  padding: 34px 18px 30px;
  color: var(--dn-muted);
  background: var(--dn-surface);
  border: 1px dashed var(--dn-line);
  border-radius: 18px;
}
.dn-empty-sky { width: 88px; height: 88px; margin: 0 auto 10px; color: var(--dn-indigo); }
.dn-empty-title {
  font-family: var(--dn-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--dn-ink);
  margin: 0 0 6px;
  letter-spacing: -0.02em;
}
.dn-empty-hint { margin: 0; font-size: 0.95rem; }

/* Loading: a compass needle while Gradio marks the block as generating */
#dn-results.generating .dn-empty,
.generating #dn-results .dn-empty,
.generating .dn-empty {
  color: transparent;
}
#dn-results.generating .dn-empty-title,
#dn-results.generating .dn-empty-hint,
.generating .dn-empty-title,
.generating .dn-empty-hint { visibility: hidden; }
#dn-results.generating .dn-empty-sky .dn-needle,
.generating .dn-empty-sky .dn-needle {
  animation: dn-needle 0.9s ease-in-out infinite alternate;
  transform-origin: 44px 44px;
}
.generating .dn-empty::after,
#dn-results.generating .dn-empty::after {
  content: "Plotting a course…";
  display: block;
  color: var(--dn-muted);
  font-family: var(--dn-display);
  font-size: 1.15rem;
  margin-top: -8px;
}

.dn-colophon {
  margin: 22px 4px 0;
  color: var(--dn-muted);
  font-size: 0.86rem;
  text-align: center;
}
.dn-colophon a { font-weight: 600; }

.dn-catalog { display: grid; gap: 8px; margin: 4px 0 14px; }
.dn-doc {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  align-items: baseline;
  background: var(--dn-surface);
  border: 1px solid var(--dn-line);
  border-radius: 12px;
  padding: 10px 14px;
}
.dn-doc-meta { color: var(--dn-muted); font-size: 0.86rem; }

#dn-search-actions { margin-top: 8px !important; }
#dn-search-actions button { width: 100%; }

@media (max-width: 700px) {
  #dn-hero { padding: 22px 18px 20px; border-radius: 18px; }
  #dn-hero .dn-hero-inner { grid-template-columns: 1fr; gap: 12px; text-align: left; }
  .dn-mark { width: 86px; height: 86px; }
  #dn-hero h1 { font-size: 1.7rem; }
  .dn-file { word-break: break-all; }
  #dn-search { padding: 12px; }
  #dn-search-actions { flex-wrap: nowrap !important; }
  #dn-search-actions button { min-width: 0 !important; flex: 1 1 0 !important; }
  #dn-suggest button, button.dn-chip { white-space: normal !important; height: auto !important; }
}

@media (prefers-reduced-motion: reduce) {
  .dn-compass, .dn-star, #dn-hero .dn-stars-bg, .dn-needle,
  #dn-results.generating .dn-empty-sky .dn-needle,
  .generating .dn-empty-sky .dn-needle {
    animation: none !important;
  }
  #dn-search button, #dn-suggest button, button.dn-chip, .dn-hit {
    transition: none !important;
  }
  #dn-search button:hover, #dn-suggest button:hover, .dn-hit:hover {
    transform: none;
  }
}
"""

# Compass rose + constellation. Decorative; the heading carries the name.
HERO_MARK = """
<svg class="dn-mark" viewBox="0 0 160 160" role="img" aria-hidden="true">
  <defs>
    <radialGradient id="dn-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#c4b5fd" stop-opacity="0.4"/>
      <stop offset="70%" stop-color="#6366f1" stop-opacity="0.08"/>
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <circle cx="80" cy="80" r="78" fill="url(#dn-glow)"/>
  <circle cx="80" cy="80" r="70" fill="none" stroke="#e0e7ff" stroke-width="0.75" opacity="0.4"/>
  <circle cx="80" cy="80" r="52" fill="none" stroke="#e0e7ff" stroke-width="0.6" opacity="0.28" stroke-dasharray="2 6"/>
  <g class="dn-compass" fill="#eef2ff" stroke="none">
    <polygon points="80,16 86,80 80,70 74,80" fill="#fff"/>
    <polygon points="80,144 86,80 80,90 74,80" fill="#a5b4fc"/>
    <polygon points="144,80 80,86 90,80 80,74" fill="#c4b5fd"/>
    <polygon points="16,80 80,86 70,80 80,74" fill="#c4b5fd"/>
    <polygon points="116,28 84,76 88,80 80,76" fill="#e0e7ff" opacity="0.85"/>
    <polygon points="44,28 76,76 80,76 72,80" fill="#e0e7ff" opacity="0.85"/>
    <polygon points="116,132 84,84 88,80 80,84" fill="#a5b4fc" opacity="0.9"/>
    <polygon points="44,132 76,84 80,84 72,80" fill="#a5b4fc" opacity="0.9"/>
    <circle cx="80" cy="80" r="6" fill="#fff"/>
    <circle cx="80" cy="80" r="2.4" fill="#4338ca"/>
    <text x="80" y="12" text-anchor="middle" fill="#fff" font-size="9" font-family="Figtree, sans-serif" font-weight="700">N</text>
  </g>
  <g fill="none" stroke="#c7d2fe" stroke-width="1" opacity="0.8">
    <path d="M38 34 L52 56 L28 70"/>
    <path d="M122 30 L130 56 L150 48"/>
    <path d="M26 112 L48 126 L36 146"/>
    <path d="M124 122 L142 130 L150 108"/>
  </g>
  <g fill="#fff">
    <circle class="dn-star" cx="38" cy="34" r="1.8"/>
    <circle class="dn-star" cx="52" cy="56" r="1.3"/>
    <circle class="dn-star" cx="28" cy="70" r="1.5"/>
    <circle class="dn-star" cx="122" cy="30" r="1.7"/>
    <circle class="dn-star" cx="130" cy="56" r="1.2"/>
    <circle class="dn-star" cx="150" cy="48" r="1.6"/>
    <circle class="dn-star" cx="26" cy="112" r="1.4"/>
    <circle class="dn-star" cx="48" cy="126" r="1.2"/>
    <circle class="dn-star" cx="36" cy="146" r="1.6"/>
    <circle class="dn-star" cx="124" cy="122" r="1.3"/>
    <circle class="dn-star" cx="142" cy="130" r="1.7"/>
    <circle class="dn-star" cx="150" cy="108" r="1.2"/>
  </g>
</svg>
"""

EMPTY_MARK = """
<svg class="dn-empty-sky" viewBox="0 0 88 88" aria-hidden="true">
  <circle cx="44" cy="44" r="36" fill="none" stroke="currentColor" stroke-width="1" opacity="0.35"/>
  <circle cx="44" cy="44" r="24" fill="none" stroke="currentColor" stroke-width="0.8" opacity="0.25" stroke-dasharray="2 5"/>
  <g class="dn-needle" fill="currentColor">
    <polygon points="44,16 48,44 44,40 40,44"/>
    <polygon points="44,72 48,44 44,48 40,44" opacity="0.45"/>
    <circle cx="44" cy="44" r="3.2"/>
  </g>
  <g fill="currentColor">
    <circle class="dn-star" cx="18" cy="22" r="1.4"/>
    <circle class="dn-star" cx="70" cy="20" r="1.2"/>
    <circle class="dn-star" cx="16" cy="64" r="1.1"/>
    <circle class="dn-star" cx="72" cy="66" r="1.5"/>
  </g>
</svg>
"""

HIDE = gr.update(value="", visible=False)


def empty_html(title: str, hint: str = "") -> str:
    hint_html = f'<p class="dn-empty-hint">{html.escape(hint)}</p>' if hint else ""
    return (
        f'<div class="dn-empty">{EMPTY_MARK}'
        f'<p class="dn-empty-title">{html.escape(title)}</p>{hint_html}</div>'
    )


def hero_html() -> str:
    s = tools.get_corpus().stats()
    return (
        f'<div id="dn-hero"><div class="dn-stars-bg" aria-hidden="true"></div>'
        f'<div class="dn-hero-inner">{HERO_MARK}<div>'
        f'<p class="eyebrow">Mac Labs AI · a compass for your documentation</p>'
        f'<h1>Docs Navigator <span class="mcp-pill">MCP</span></h1>'
        f'<p class="lede">{html.escape(TAGLINE)}</p>'
        f'<div class="chips"><span class="chip">{s["documents"]} documents</span>'
        f'<span class="chip">{s["passages"]} searchable passages</span>'
        f'<span class="chip">tools: list_docs · search_docs · read_doc</span>'
        f'<span class="chip">v{__version__}</span></div>'
        f"</div></div></div>"
    )


def render_catalog(docs: list[dict]) -> str:
    if not docs:
        return empty_html("No documents on the map.", "Point DOCS_DIR at a folder to load your own files.")
    rows = []
    for d in docs:
        kind = html.escape(str(d.get("type") or "file"))
        name = html.escape(d["file"])
        passages = int(d.get("passages") or 0)
        chars = int(d.get("chars") or 0)
        rows.append(
            "<div class='dn-doc'>"
            f"<span class='dn-file'>{name}</span>"
            f"<span class='dn-doc-meta'>{kind} · {passages:,} passages · {chars:,} characters</span>"
            "</div>"
        )
    return "<div class='dn-catalog'>" + "".join(rows) + "</div>"


def render_hits(hits) -> str:
    if not hits:
        return empty_html(
            "Nothing in this part of the map.",
            "Try a shorter phrase, or tap one of the headings below to set a new course.",
        )
    cards = []
    for h in hits:
        section = f" › {html.escape(h.heading)}" if h.heading else ""
        cards.append(
            f'<div class="dn-hit"><div class="meta"><span class="dn-file">{html.escape(h.doc)}</span>'
            f'<span>{section.lstrip(" ›")}</span><span class="dn-score">score {h.score:.2f}</span></div>'
            f"<div>{h.snippet}</div></div>"
        )
    return "".join(cards)


def search_ui(query: str):
    query = (query or "").strip()
    if not query:
        return HIDE, empty_html("Where to?", "Type a question or a few keywords, and I will plot a course.")
    return HIDE, render_hits(tools.get_corpus().search(query, limit=6))


def ask_ui(query: str, oauth_token: gr.OAuthToken | None = None):
    query = (query or "").strip()
    if not query:
        return HIDE, empty_html("Ask a question first.", "I will read the matching passages and answer from them.")
    hits = tools.get_corpus().search(query, limit=6)
    token = oauth_token.token if oauth_token else SERVER_TOKEN
    try:
        result = answer_question(query, hits, token)
    except LLMUnavailable as exc:
        note = f'<div class="dn-answer">{html.escape(str(exc))}</div>'
        return gr.update(value=note, visible=True), render_hits(hits)
    body = html.escape(result.text).replace("\n", "<br>")
    answer = (
        f'<div class="dn-answer">{body}<div class="dn-note">Answered by {html.escape(result.model)} '
        "from the passages below, using your Hugging Face inference credits.</div></div>"
    )
    return gr.update(value=answer, visible=True), render_hits(hits)


def ask_ui_signed_in(query: str, oauth_token: gr.OAuthToken | None):
    return ask_ui(query, oauth_token)


def ask_ui_plain(query: str):
    return ask_ui(query, None)


def browse_ui(name: str):
    if not name:
        return ""
    try:
        return tools.read_doc(name)
    except (FileNotFoundError, ValueError) as exc:
        return str(exc)


def fill_example(text: str):
    return text


def build_demo() -> gr.Blocks:
    corpus = tools.get_corpus()
    file_choices = [d["file"] for d in corpus.list_docs()]
    url = mcp_url()
    configs = client_configs(url)

    with gr.Blocks(title=TITLE, fill_width=False) as demo:
        gr.HTML(hero_html())

        with gr.Group(elem_id="dn-search"):
            query = gr.Textbox(
                placeholder="Where should we look? Ask a question, or name a topic…",
                show_label=False,
                lines=1,
                container=False,
                autofocus=True,
                elem_id="dn-query",
            )
            with gr.Row(elem_id="dn-search-actions"):
                search_btn = gr.Button("Search", variant="primary", scale=1)
                ask_btn = gr.Button("Ask with AI", scale=1)

        with gr.Row(elem_id="dn-suggest"):
            with gr.Column(scale=5):
                gr.HTML('<p class="dn-suggest-label">Try a heading</p>')
                with gr.Row():
                    chip_buttons = [
                        gr.Button(ex, size="sm", elem_classes=["dn-chip"], min_width=80) for ex in EXAMPLES
                    ]
            if LOGIN:
                with gr.Column(scale=2, min_width=200):
                    gr.LoginButton("Sign in with Hugging Face to use Ask", size="sm")

        if LOGIN:
            gr.HTML(
                '<div class="dn-note">Search is always free and needs no sign-in. '
                "“Ask with AI” uses an open model through Hugging Face Inference Providers "
                "and is paid from your own free monthly credits.</div>"
            )
        else:
            gr.HTML(
                '<div class="dn-note">Search needs no key. “Ask with AI” runs when <code>DOCSNAV_SERVER_TOKEN</code> '
                "is set to a Hugging Face token. The hosted Space uses Sign in with Hugging Face instead.</div>"
            )
        answer_box = gr.HTML(visible=False)
        results_box = gr.HTML(
            empty_html(
                "The chart is clear.",
                "Type a question, or tap a heading above to set a course.",
            ),
            elem_id="dn-results",
        )

        with gr.Tabs():
            with gr.Tab("Browse documents"):
                gr.HTML(
                    "<p class='dn-note' style='margin-top:0'>Every file currently on the map. Open one to read it in full.</p>"
                    + render_catalog(corpus.list_docs())
                )
                picker = gr.Dropdown(file_choices, label="Open a document", value=None)
                viewer = gr.Textbox(label="Contents", lines=16, max_lines=28, interactive=False)
            with gr.Tab("Connect via MCP"):
                gr.Markdown(
                    f"This app is an MCP server — the same compass, in your editor. "
                    f"Point your client at `{url}` and it can call "
                    "`list_docs`, `search_docs`, and `read_doc`. The tool schema is at "
                    f"`{url}schema`."
                )
                with gr.Tabs():
                    for name, cfg in configs.items():
                        with gr.Tab(name):
                            gr.Markdown(cfg["hint"])
                            gr.Code(cfg["code"], language=cfg["language"], show_label=False, interactive=False)
                gr.Markdown(
                    "Hosted tools search the sample Aurora AI docs. To search your own files, run the app or "
                    "`mcp_server.py` yourself with `DOCS_DIR` pointing at a folder."
                )

        outputs = [answer_box, results_box]
        search_btn.click(search_ui, query, outputs, api_visibility="private")
        query.submit(search_ui, query, outputs, api_visibility="private")
        ask_btn.click(ask_ui_signed_in if LOGIN else ask_ui_plain, query, outputs, api_visibility="private")
        picker.change(browse_ui, picker, viewer, api_visibility="private")
        for ex, chip in zip(EXAMPLES, chip_buttons, strict=True):
            chip.click(lambda e=ex: e, outputs=query, api_visibility="private").then(
                search_ui, query, outputs, api_visibility="private"
            )

        # MCP tools. gr.api registers each function as an API endpoint and an MCP tool, with no UI.
        gr.api(tools.list_docs, api_name="list_docs")
        gr.api(tools.search_docs, api_name="search_docs")
        gr.api(tools.read_doc, api_name="read_doc")

        gr.HTML(
            '<div class="dn-colophon">A Mac Labs AI project. '
            '<a href="https://mso-docs.github.io/Docs-Navigator/">Project page</a> · '
            '<a href="https://huggingface.co/collections/mackenzietechdocs/docs-navigator">Collection</a> · '
            '<a href="https://github.com/mso-docs/Docs-Navigator">Source</a></div>'
        )

    # The login button registers an internal endpoint; keep it out of the MCP tool list.
    for fn in demo.fns.values():
        if fn.api_name == "_check_login_status":
            fn.api_visibility = "private"
    return demo


demo = build_demo()

if __name__ == "__main__":
    demo.launch(
        mcp_server=True,
        theme=NAV_THEME,
        css=CSS,
        server_name=os.getenv("GRADIO_SERVER_NAME", "0.0.0.0" if os.getenv("SPACE_ID") else "127.0.0.1"),
        server_port=int(os.getenv("PORT", os.getenv("GRADIO_SERVER_PORT", "7860"))),
        show_error=True,
        head=HEAD,
    )
