#!/usr/bin/env python3
"""
make_boot_svg.py

Builds boot-sequence.svg: a fake terminal boot log that types itself
in line by line, with a real animated progress bar (not just a text
percentage) on the "compiling ambition" line, and a persistent
blinking cursor at the end once it's done.

Set STATIC=1 for a frozen preview frame.
"""
import os
from pathlib import Path

TITLE = "ansika@DESKTOP: bootstrap.sh"

LINES = [
    ("OK",   "module: backend-services", "node.js \u00b7 fastapi \u00b7 express"),
    ("OK",   "module: frontend-frameworks", "react \u00b7 next.js \u00b7 vite"),
    ("OK",   "module: system-design", "lld/hld \u00b7 scalable apis \u00b7 db indexing"),
    ("OK",   "module: ai-ml-integration", "tensorflow.js \u00b7 gemini-api"),
    ("RUN",  "compiling ambition: full-stack \u2192 ai/ml engineer", 81),
    ("RUN",  "problem solving: dsa \u00b7 leetcode", 50),
    ("OK",   "hackathons indexed", "3 podium finishes"),
    ("OK",   "open-source", "Social Winter of Code contributor \u00b7 Open Source Connect India project admin"),
    ("DONE", "status", "shipping"),
]
PROGRESS_TARGET = 81  # fallback %

TAG_COLORS = {"OK": "#3fb950", "RUN": "#58a6ff", "DONE": "#bc8cff", "WARN": "#e3b341"}
TAG_ICON = {"OK": "\u25b8", "RUN": "\u25c9", "DONE": "\u2726", "WARN": "\u25b3"}

BG_COLOR = "#0a0d12"
BORDER_COLOR = "#22283a"
LABEL_COLOR = "#c9d1d9"
DETAIL_COLOR = "#6e7681"
PROMPT_COLOR = "#58a6ff"
FONT_FAMILY = "'JetBrains Mono', Consolas, monospace"

WIDTH = 860
LEFT_MARGIN = 26
LINE_HEIGHT = 26
TOP_PADDING = 64
LINE_STAGGER = 0.5
CURSOR_BLINK = 0.9

STATIC = os.environ.get("STATIC") == "1"


def build_svg() -> str:
    n_lines = len(LINES)
    height = TOP_PADDING + n_lines * LINE_HEIGHT + 40

    # Calculate unified progress bar start position so stacked progress bars align neatly
    bar_x = round(max(LEFT_MARGIN + 34 + len(msg) * 7.9 + 14 for _, msg, detail in LINES if not isinstance(detail, str)), 1)
    bar_w = WIDTH - bar_x - 70

    rows = []
    for i, (tag, msg, detail) in enumerate(LINES):
        y = TOP_PADDING + i * LINE_HEIGHT
        delay = round(i * LINE_STAGGER, 2)
        color = TAG_COLORS.get(tag, "#8b949e")
        icon = TAG_ICON.get(tag, "\u25b8")

        if STATIC:
            opacity_attr = "1"
            anim = ""
        else:
            opacity_attr = "0"
            anim = f'''
        <animate attributeName="opacity" from="0" to="1"
                 begin="{delay}s" dur="0.25s" fill="freeze" />'''

        if isinstance(detail, str):
            rows.append(f'''
    <g opacity="{opacity_attr}">
      {anim}
      <text x="{LEFT_MARGIN}" y="{y}" font-family="{FONT_FAMILY}" font-size="13" fill="{color}">[{icon}]</text>
      <text x="{LEFT_MARGIN + 34}" y="{y}" font-family="{FONT_FAMILY}" font-size="13" fill="{LABEL_COLOR}">{msg}</text>
      <text x="{LEFT_MARGIN + 34 + len(msg) * 7.9 + 14}" y="{y}" font-family="{FONT_FAMILY}" font-size="13" fill="{DETAIL_COLOR}">{detail}</text>
    </g>''')
        else:
            target_pct = detail if isinstance(detail, (int, float)) else PROGRESS_TARGET
            fill_w = round(bar_w * target_pct / 100, 1)
            fill_delay = delay + 0.25
            fill_dur = 1.6
            label_delay = fill_delay + fill_dur

            if STATIC:
                fill_attr_w = fill_w
                fill_anim = ""
                label_opacity = "1"
                label_anim = ""
            else:
                fill_attr_w = 0
                fill_anim = f'''
        <animate attributeName="width" from="0" to="{fill_w}"
                 begin="{fill_delay}s" dur="{fill_dur}s" fill="freeze"
                 calcMode="spline" keySplines="0.3 0.8 0.3 1" />'''
                label_opacity = "0"
                label_anim = f'''
        <animate attributeName="opacity" from="0" to="1"
                 begin="{label_delay}s" dur="0.3s" fill="freeze" />'''

            rows.append(f'''
    <g opacity="{opacity_attr}">
      {anim}
      <text x="{LEFT_MARGIN}" y="{y}" font-family="{FONT_FAMILY}" font-size="13" fill="{color}">[{icon}]</text>
      <text x="{LEFT_MARGIN + 34}" y="{y}" font-family="{FONT_FAMILY}" font-size="13" fill="{LABEL_COLOR}">{msg}</text>
      <rect x="{bar_x}" y="{y - 10}" width="{bar_w}" height="8" rx="4" fill="#161b22" stroke="{BORDER_COLOR}" stroke-width="1" />
      <rect x="{bar_x}" y="{y - 10}" width="{fill_attr_w}" height="8" rx="4" fill="{PROMPT_COLOR}">{fill_anim}</rect>
      <text x="{bar_x + bar_w + 10}" y="{y}" font-family="{FONT_FAMILY}" font-size="13" fill="{PROMPT_COLOR}" opacity="{label_opacity}">{int(target_pct)}%{label_anim}</text>
    </g>''')

    total_delay = n_lines * LINE_STAGGER
    cursor_delay = round(total_delay + 0.5, 2)
    prompt_y = TOP_PADDING + n_lines * LINE_HEIGHT + 22

    if STATIC:
        prompt_opacity = "1"
        prompt_anim = ""
        cursor_delay_attr = "0"
    else:
        prompt_opacity = "0"
        prompt_anim = f'''
      <animate attributeName="opacity" from="0" to="1"
               begin="{cursor_delay}s" dur="0.3s" fill="freeze" />'''
        cursor_delay_attr = str(cursor_delay)

    cursor_x = LEFT_MARGIN + len("ansika@DESKTOP:~$") * 7.9 + 12
    cursor = f'''
    <g opacity="{prompt_opacity}">
      {prompt_anim}
      <text x="{LEFT_MARGIN}" y="{prompt_y}" font-family="{FONT_FAMILY}" font-size="13" fill="{PROMPT_COLOR}">ansika@DESKTOP:~$</text>
      <rect x="{cursor_x}" y="{prompt_y - 10}" width="8" height="13" fill="{PROMPT_COLOR}" opacity="0">
        <animate attributeName="opacity" from="0" to="0" begin="0s" dur="{cursor_delay_attr}s" fill="freeze" />
        <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.01;0.5;1"
                 begin="{cursor_delay}s" dur="{CURSOR_BLINK}s" repeatCount="indefinite" />
      </rect>
    </g>'''

    svg = f'''<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bootGlow" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.45" />
      <stop offset="50%" stop-color="#bc8cff" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0.45" />
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="11"
        fill="none" stroke="url(#bootGlow)" stroke-width="1.4" />
  <rect x="2" y="2" width="{WIDTH - 4}" height="{height - 4}" rx="9"
        fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1" />

  <circle cx="26" cy="24" r="5" fill="#ff5f56" />
  <circle cx="44" cy="24" r="5" fill="#ffbd2e" />
  <circle cx="62" cy="24" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="29" font-family="{FONT_FAMILY}" font-size="13"
        fill="#8b949e" text-anchor="middle">{TITLE}</text>
  <line x1="2" y1="42" x2="{WIDTH - 2}" y2="42" stroke="{BORDER_COLOR}" stroke-width="1" />

  {"".join(rows)}
  {cursor}
</svg>
'''
    return svg


def main():
    out = Path("boot-sequence.svg")
    out.write_text(build_svg(), encoding="utf-8")
    print(f"Done -> {out}" + (" (static frame)" if STATIC else ""))


if __name__ == "__main__":
    main()
