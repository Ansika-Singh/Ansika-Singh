#!/usr/bin/env python3
"""
prep_photo.py

Turns a normal photo into a clean, high-contrast, white-background
grayscale image that converts well to ASCII art.

Usage:
    python scripts/prep_photo.py source-photo.jpg [output-name.png]
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def remove_background(input_path: Path) -> Image.Image:
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)
    from io import BytesIO
    return Image.open(BytesIO(output_bytes)).convert("RGBA")


def boost_contrast(rgba_image: Image.Image) -> Image.Image:
    rgba = np.array(rgba_image)
    rgb, alpha = rgba[:, :, :3], rgba[:, :, 3]
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    lab = cv2.merge((l_channel, a_channel, b_channel))
    rgb_boosted = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    out = np.dstack([rgb_boosted, alpha])
    return Image.fromarray(out, mode="RGBA")


def composite_on_white(rgba_image: Image.Image) -> Image.Image:
    white_bg = Image.new("RGBA", rgba_image.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, rgba_image)
    return composited.convert("L")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py <source-photo> [output.png]")
        sys.exit(1)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("source-prepped.png")
    print(f"[1/3] Removing background from {src} ...")
    no_bg = remove_background(src)
    print("[2/3] Boosting local contrast (CLAHE) ...")
    contrasty = boost_contrast(no_bg)
    print("[3/3] Compositing onto white + converting to grayscale ...")
    final = composite_on_white(contrasty)
    final.save(out)
    print(f"Done -> {out}")


if __name__ == "__main__":
    main()
