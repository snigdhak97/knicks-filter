#!/usr/bin/env python3
"""
Punch a transparent photo window through the white box of the Knicks frame,
but STOP below the logo so the logo keeps its white/blue background (the photo
must not bleed through the logo's white parts).

How it works:
  1. Flood-fill from the image center across connected near-white pixels -> the
     white box region (this also catches the logo's white parts + white around it).
  2. Find the bottom of the logo (lowest orange logo pixel up top).
  3. Make transparent ONLY the box pixels BELOW that line. Everything above
     (logo, banner, skyline, white matte around the logo) stays opaque.

Usage: python3 make_transparent.py [input.png] [output.png]
"""
import sys
from PIL import Image, ImageDraw

src = sys.argv[1] if len(sys.argv) > 1 else "knicks frame 1.png"
out = sys.argv[2] if len(sys.argv) > 2 else "frame_transparent.png"

img = Image.open(src).convert("RGBA")
W, H = img.size
rgb = img.convert("RGB")

# 1) Flood-fill the white box from the center.
SENT = (255, 0, 255)
ImageDraw.floodfill(rgb, (W // 2, H // 2), SENT, thresh=40)
fp = rgb.load()

# 2) Bottom of the logo = lowest orange pixel in the upper-center region.
op = img.load()
logo_bottom = 0
for y in range(0, int(H * 0.45)):
    for x in range(int(W * 0.20), int(W * 0.80)):
        r, g, b, a = op[x, y]
        if a > 200 and r > 180 and 55 < g < 175 and b < 100:   # Knicks orange
            if y > logo_bottom:
                logo_bottom = y
Y0 = logo_bottom + 10   # small margin below the logo
print(f"logo bottom at y={logo_bottom}, photo window starts at y={Y0}")

# 3) Make transparent only the flood-filled box pixels at or below Y0.
px = img.load()
count = 0
miny = H
for y in range(H):
    for x in range(W):
        if fp[x, y] == SENT and y >= Y0:
            r, g, b, _ = px[x, y]
            px[x, y] = (r, g, b, 0)
            count += 1
            if y < miny:
                miny = y

img.save(out)
print(f"Made {count} px transparent. Window top y={miny}. Image {W}x{H} -> {out}")
