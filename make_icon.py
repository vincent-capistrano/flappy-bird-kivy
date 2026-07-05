"""Generate icon.png (512x512) for Flappy Bird."""
from PIL import Image, ImageDraw
import math

SIZE = 512
img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# ── Sky background (rounded square) ──────────────────────────────
def rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.ellipse([x0, y0, x0 + radius*2, y0 + radius*2], fill=fill)
    draw.ellipse([x1 - radius*2, y0, x1, y0 + radius*2], fill=fill)
    draw.ellipse([x0, y1 - radius*2, x0 + radius*2, y1], fill=fill)
    draw.ellipse([x1 - radius*2, y1 - radius*2, x1, y1], fill=fill)

rounded_rect(draw, (0, 0, SIZE, SIZE), 80, (74, 186, 255))  # sky blue

# ── Clouds ───────────────────────────────────────────────────────
for (cx, cy, r) in [(110, 120, 45), (155, 100, 55), (200, 118, 40),
                    (330, 90, 40), (375, 72, 50), (415, 90, 38)]:
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(255, 255, 255, 200))

# ── Ground strip ─────────────────────────────────────────────────
rounded_rect(draw, (0, 440, SIZE, SIZE), 0, (101, 67, 33))   # brown
draw.rectangle([0, 440, SIZE, 475], fill=(34, 170, 34))       # grass

# ── Pipes (left gap) ─────────────────────────────────────────────
PIPE_COLOR  = (34, 170, 34)
PIPE_DARK   = (20, 120, 20)
CAP_H = 28

# Bottom pipe
draw.rectangle([18, 310, 110, 440], fill=PIPE_COLOR)
draw.rectangle([8,  310, 120, 310+CAP_H], fill=PIPE_DARK)   # cap top

# Top pipe
draw.rectangle([18, 0, 110, 175], fill=PIPE_COLOR)
draw.rectangle([8, 175-CAP_H, 120, 175], fill=PIPE_DARK)    # cap bottom

# Right pipe
draw.rectangle([402, 340, 494, 440], fill=PIPE_COLOR)
draw.rectangle([392, 340, 504, 340+CAP_H], fill=PIPE_DARK)

draw.rectangle([402, 0, 494, 190], fill=PIPE_COLOR)
draw.rectangle([392, 190-CAP_H, 504, 190], fill=PIPE_DARK)

# ── Bird body ────────────────────────────────────────────────────
BX, BY = 256, 248   # center
BR = 72             # body radius
draw.ellipse([BX-BR, BY-BR, BX+BR, BY+BR], fill=(255, 220, 0))    # yellow
draw.ellipse([BX-BR+6, BY-BR+6, BX+BR-6, BY+BR-6], fill=(255, 235, 60))

# Wing
draw.ellipse([BX-BR-18, BY-20, BX+10, BY+40], fill=(255, 180, 0))

# Eye white
draw.ellipse([BX+18, BY-38, BX+62, BY+6], fill=(255, 255, 255))
# Pupil
draw.ellipse([BX+32, BY-28, BX+54, BY-6], fill=(30, 30, 30))
# Eye shine
draw.ellipse([BX+34, BY-26, BX+42, BY-18], fill=(255, 255, 255))

# Beak
beak = [(BX+58, BY-8), (BX+96, BY+4), (BX+58, BY+18)]
draw.polygon(beak, fill=(255, 120, 0))

# Cheek blush
draw.ellipse([BX+10, BY+14, BX+44, BY+42], fill=(255, 160, 160, 160))

# ── Score coins ──────────────────────────────────────────────────
for i, (cx, cy) in enumerate([(170, 390), (215, 382), (260, 390),
                               (305, 382), (350, 390)]):
    draw.ellipse([cx-14, cy-14, cx+14, cy+14], fill=(255, 210, 0))
    draw.ellipse([cx-10, cy-10, cx+10, cy+10], fill=(255, 235, 80))

img.save("icon.png")
print("icon.png saved (512x512)")
