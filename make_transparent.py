#!/usr/bin/env python3
"""
Punch a transparent window through the white rectangle in the Knicks frame.

It flood-fills outward from the center of the image across the connected
near-white pixels (the photo box) and makes exactly that region transparent,
leaving the logo, text, player, and blue border untouched.

Usage: python3 make_transparent.py [input.png] [output.png]
"""
import sys
from PIL import Image, ImageDraw

src = sys.argv[1] if len(sys.argv) > 1 else "frame.png"
out = sys.argv[2] if len(sys.argv) > 2 else "frame_transparent.png"

img = Image.open(src).convert("RGBA")
w, h = img.size

# Work on an RGB copy for flood fill, mark the box with a sentinel color.
rgb = img.convert("RGB")
SENTINEL = (255, 0, 255)  # magenta — won't appear in the artwork

# Seed from the geometric center, which is inside the white photo box.
seed = (w // 2, h // 2)
ImageDraw.floodfill(rgb, seed, SENTINEL, thresh=40)

# Wherever we painted the sentinel, set alpha to 0 in the original.
px_rgb = rgb.load()
px_img = img.load()
count = 0
for y in range(h):
    for x in range(w):
        if px_rgb[x, y] == SENTINEL:
            r, g, b, _ = px_img[x, y]
            px_img[x, y] = (r, g, b, 0)
            count += 1

img.save(out)
print(f"Done. Made {count} pixels transparent ({count / (w * h) * 100:.1f}% of image).")
print(f"Image size: {w}x{h}")
print(f"Saved: {out}")
