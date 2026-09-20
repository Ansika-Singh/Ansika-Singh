#!/usr/bin/env python3
"""
make_info_card.py

Builds info-card.svg: a neofetch-style panel that fades/slides its
lines in on a stagger, with a glowing border and a blinking cursor
after the type-in finishes.

Set STATIC=1 for a frozen preview frame.
"""
import os
from pathlib import Path

TITLE = "ansika@github"
CONTENT = [
    ("\U0001F4BC Role", ["Backend Developer", "AI/ML Integration"]),
    ("\u26A1 Now", ["Backend Developer @ One Tappe", "Frontend Developer @ Open Source Connect", "Founder's Office Intern @ NexFellow"]),
    ("\U0001F6E0 Stack", ["React · Next.js · Node.js", "FastAPI · Python · MongoDB"]),
    ("\U0001F3C6 Wins", ["3x Hackathon Winner", "AIdeastorm '26 · Luminix '26 · Hackhazards '26"]),
    ("\U0001F393 Education", ["B.E. ISE, CIT Bengaluru '28"]),
]
ACCENT = "#39d353"
ACCENT_DIM = "#1f6feb"
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
FONT_FAMILY = "'JetBrains Mono', Consolas, monospace"

WIDTH = 540
LEFT_MARGIN = 30
VALUE_X = 190
BLOCK_GAP = 14
SUBLINE_HEIGHT = 19
TOP_PADDING = 60
STAGGER = 0.16
DURATION = 0.4
CURSOR_BLINK = 0.9

STATIC = os.environ.get("STATIC") == "1"


def _as_lines(value):
    return value if isinstance(value, list) else [value]


def build_svg() -> str:
    block_heights = [len(_as_lines(v)) * SUBLINE_HEIGHT + BLOCK_GAP for _, v in CONTENT]
    content_height = sum(block_heights)
    height = TOP_PADDING + content_height + 34

    rows = []
    y_cursor = TOP_PADDING
    last_delay = 0.0
    for i, (label, value) in enumerate(CONTENT):
        lines = _as_lines(value)
        delay = round(i * STAGGER, 2)
        last_delay = max(last_delay, delay)
        if STATIC:
            opacity_attr = "1"
            transform_attr = "translate(0,0)"
            anim = ""
        else:
            opacity_attr = "0"
            transform_attr = "translate(-8,0)"
            anim = f'''
        <animate attributeName="opacity" from="0" to="1"
                 begin="{delay}s" dur="{DURATION}s" fill="freeze" />
        <animateTransform attributeName="transform" type="translate"
                 from="-8,0" to="0,0" begin="{delay}s" dur="{DURATION}s"
                 fill="freeze" />'''
        label_y = y_cursor
        value_tspans = "".join(
            f'<tspan x="{VALUE_X}" dy="{0 if j == 0 else SUBLINE_HEIGHT}">{line}</tspan>'
            for j, line in enumerate(lines)
        )
        rows.append(f'''
    <g opacity="{opacity_attr}" transform="{transform_attr}">
      {anim}
      <rect x="{LEFT_MARGIN - 14}" y="{label_y - 11}" width="3" height="13" rx="1.5" fill="{ACCENT_DIM}" />
      <text x="{LEFT_MARGIN}" y="{label_y}" font-family="{FONT_FAMILY}" font-size="13"
            font-weight="700" fill="{ACCENT}">{label}</text>
      <text x="{VALUE_X}" y="{label_y}" font-family="{FONT_FAMILY}" font-size="12.5"
            fill="{VALUE_COLOR}">{value_tspans}</text>
    </g>''')
        y_cursor += len(lines) * SUBLINE_HEIGHT + BLOCK_GAP

    cursor_y = y_cursor + 4
    cursor_delay = last_delay + DURATION + 0.1
    cursor = f'''
    <rect x="{LEFT_MARGIN}" y="{cursor_y - 10}" width="8" height="13" fill="{ACCENT}" opacity="0">
      <animate attributeName="opacity" from="0" to="0"
               begin="0s" dur="{cursor_delay}s" fill="freeze" />
      <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.01;0.5;1"
               begin="{cursor_delay}s" dur="{CURSOR_BLINK}s" repeatCount="indefinite" />
    </rect>'''

    svg = f'''<svg viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="borderGlow" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0.55" />
      <stop offset="50%" stop-color="{ACCENT_DIM}" stop-opacity="0.35" />
      <stop offset="100%" stop-color="{ACCENT}" stop-opacity="0.55" />
    </linearGradient>
    <linearGradient id="panelBg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#11161d" />
      <stop offset="100%" stop-color="{BG_COLOR}" />
    </linearGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="11"
        fill="none" stroke="url(#borderGlow)" stroke-width="1.4" />
  <rect x="2" y="2" width="{WIDTH - 4}" height="{height - 4}" rx="9"
        fill="url(#panelBg)" stroke="{BORDER_COLOR}" stroke-width="1" />
  <circle cx="26" cy="24" r="5" fill="#ff5f56" />
  <circle cx="44" cy="24" r="5" fill="#ffbd2e" />
  <circle cx="62" cy="24" r="5" fill="#27c93f" />
  <text x="{WIDTH / 2}" y="29" font-family="{FONT_FAMILY}" font-size="13"
        fill="{LABEL_COLOR}" text-anchor="middle">{TITLE}</text>
  <line x1="2" y1="42" x2="{WIDTH - 2}" y2="42" stroke="{BORDER_COLOR}" stroke-width="1" />
  {"".join(rows)}
  {cursor}
</svg>
'''
    return svg


def main():
    out = Path("info-card.svg")
    out.write_text(build_svg(), encoding="utf-8")
    print(f"Done -> {out}" + (" (static frame)" if STATIC else ""))


if __name__ == "__main__":
    main()
