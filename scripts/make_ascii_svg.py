#!/usr/bin/env python3
"""
make_ascii_svg.py

Converts source-prepped.png into avi-ascii.svg: a monochrome ASCII
portrait that "types" itself in row by row via SMIL animation.

Usage:
    python scripts/make_ascii_svg.py [input.png] [output.svg]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
GRID_COLS = 100
GRID_ROWS = 53
FONT_FAMILY = "Consolas, 'Courier New', monospace"
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
FILL_COLOR = "#c9d1d9"
CURSOR_COLOR = "#39d353"
ROW_STAGGER = 0.035
ROW_DURATION = 0.5


def image_to_ascii_grid(img_path: Path, cols: int, rows: int) -> list[str]:
    img = Image.open(img_path).convert("L")
    img = img.resize((cols, rows))
    pixels = np.array(img)
    ramp_len = len(RAMP)
    lines = []
    for row in pixels:
        line = "".join(RAMP[min(int(p / 255 * ramp_len), ramp_len - 1)] for p in row)
        lines.append(line)
    return lines


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(lines: list[str]) -> str:
    width = GRID_COLS * CHAR_W
    height = GRID_ROWS * CHAR_H
    row_elements = []
    for i, line in enumerate(lines):
        row_w = len(line) * CHAR_W
        start = round(i * ROW_STAGGER, 3)
        row_elements.append(f'''
    <clipPath id="clip{i}">
      <rect x="0" y="{round(i * CHAR_H, 2)}" width="0" height="{CHAR_H}">
        <animate attributeName="width" from="0" to="{row_w}"
                 begin="{start}s" dur="{ROW_DURATION}s"
                 fill="freeze" calcMode="linear" />
      </rect>
    </clipPath>''')
    text_and_cursors = []
    for i, line in enumerate(lines):
        safe_line = escape_xml(line)
        row_w = len(line) * CHAR_W
        start = round(i * ROW_STAGGER, 3)
        y = round((i + 0.8) * CHAR_H, 2)
        text_and_cursors.append(f'''
    <g clip-path="url(#clip{i})">
      <text x="0" y="{y}" font-family="{FONT_FAMILY}" font-size="{FONT_SIZE}"
            fill="{FILL_COLOR}" xml:space="preserve">{safe_line}</text>
    </g>
    <rect x="0" y="{round(i * CHAR_H, 2)}" width="{CHAR_W * 1.1}" height="{CHAR_H}"
          fill="{CURSOR_COLOR}" opacity="0.85">
      <animate attributeName="x" from="0" to="{row_w}"
               begin="{start}s" dur="{ROW_DURATION}s"
               fill="freeze" calcMode="linear" />
      <animate attributeName="opacity" from="0.85" to="0"
               begin="{start + ROW_DURATION}s" dur="0.25s" fill="freeze" />
    </rect>''')
    svg = f'''<svg viewBox="0 0 {round(width, 2)} {round(height, 2)}"
     xmlns="http://www.w3.org/2000/svg" font-weight="500">
  <defs>{"".join(row_elements)}
  </defs>
  <rect x="0" y="0" width="{round(width, 2)}" height="{round(height, 2)}" fill="none" />
  {"".join(text_and_cursors)}
</svg>
'''
    return svg


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-prepped.png")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("avi-ascii.svg")
    if not input_path.exists():
        print(f"Input image not found: {input_path}")
        print("Run prep_photo.py first.")
        sys.exit(1)
    lines = image_to_ascii_grid(input_path, GRID_COLS, GRID_ROWS)
    svg = build_svg(lines)
    output_path.write_text(svg)
    print(f"Done -> {output_path}")


if __name__ == "__main__":
    main()
