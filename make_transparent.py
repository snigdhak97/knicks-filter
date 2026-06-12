#!/usr/bin/env python3
"""
Punch a transparent photo window through the white box of the Knicks frame so
the photo fills the WHOLE box, with the top logo floating on top of it — but
keep a tight WHITE halo hugging the logo's shape so it stays readable.

How it works:
  1. Flood-fill from the image center across connected near-white pixels -> the
     white box region (the photo area + the white behind/around/inside the logo).
  2. Build a mask of the logo's own colored pixels (orange/dark/blue) up top,
     and DILATE it by HALO px to get the logo silhouette + a tight outline.
  3. Make transparent every box-white pixel EXCEPT the logo silhouette.
     => photo fills the box right up to the logo edge; logo floats on top.

The logo's OWN internal white (e.g. the "NEW YORK" banner) is kept via a
morphological CLOSE (dilate then erode) — this fills holes inside the logo
WITHOUT adding any outward white border.

Usage: python3 make_transparent.py [input.png] [output.png] [close_px]
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

src   = sys.argv[1] if len(sys.argv) > 1 else "knicks frame 1.png"
out   = sys.argv[2] if len(sys.argv) > 2 else "frame_transparent.png"
CLOSE = int(sys.argv[3]) if len(sys.argv) > 3 else 4

img = Image.open(src).convert("RGBA")
W, H = img.size

# 1) Flood-fill the white box from the center.
rgb = img.convert("RGB")
SENT = (255, 0, 255)
ImageDraw.floodfill(rgb, (W // 2, H // 2), SENT, thresh=40)
fp = rgb.load()

# 2) Logo silhouette = colored (non-white) pixels in the upper-center region,
#    then dilate to cover enclosed whites (banner) + a tight outline.
op = img.load()
logo = Image.new("L", (W, H), 0)
lp = logo.load()
x0, x1 = int(W * 0.12), int(W * 0.88)
for y in range(0, int(H * 0.27)):           # top ~27% holds the logo
    for x in range(x0, x1):
        r, g, b, a = op[x, y]
        if a > 200 and not (r > 235 and g > 235 and b > 235):  # not white = logo ink
            lp[x, y] = 255
# Morphological close = dilate then erode: fills internal holes, no outer border.
filled = logo.filter(ImageFilter.MaxFilter(2 * CLOSE + 1)) \
             .filter(ImageFilter.MinFilter(2 * CLOSE + 1))
hp = filled.load()

# 3) Transparent = box-white AND NOT part of the (hole-filled) logo silhouette.
px = img.load()
count = 0
for y in range(H):
    for x in range(W):
        if fp[x, y] == SENT and hp[x, y] == 0:
            r, g, b, _ = px[x, y]
            px[x, y] = (r, g, b, 0)
            count += 1

img.save(out)
print(f"Close={CLOSE}px. Made {count} px transparent. Image {W}x{H} -> {out}")
