#!/usr/bin/env python3
"""
Pixel Art Pine Tree for Video Games (64x96 px)
"""
import sys, os, math
sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from PIL import Image, ImageDraw

W, H = 64, 96
OUT = '/home/cachy/Escritorio'
BRAIN = '/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0'

# Palettes
TRUNK_D3 = (35, 20, 15, 255)
TRUNK_D2 = (55, 32, 22, 255)
TRUNK_M  = (85, 50, 32, 255)
TRUNK_L  = (125, 78, 48, 255)

PINE_D3  = (12, 32, 24, 255)    # deepest shadow
PINE_D2  = (22, 54, 38, 255)    # dark shadow
PINE_D1  = (34, 82, 56, 255)    # base green
PINE_M   = (48, 115, 76, 255)   # mid green
PINE_L   = (76, 160, 98, 255)   # highlight
PINE_HL  = (120, 200, 130, 255) # bright tip highlight
SHADOW_G = (15, 25, 20, 100)
OUTLINE  = (8, 20, 15, 255)

img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# 1. Ground Shadow
d.ellipse([14, 82, 50, 93], fill=SHADOW_G)

# 2. Trunk
# Tapering trunk from y=55 down to 88
d.polygon([(29, 58), (35, 58), (38, 88), (26, 88)], fill=TRUNK_M)
d.polygon([(26, 88), (29, 58), (31, 58), (28, 88)], fill=TRUNK_D2)
d.polygon([(26, 88), (27, 85), (29, 88)], fill=TRUNK_D3)
d.line([(34, 60), (37, 87)], fill=TRUNK_L, width=1)
# Roots
d.polygon([(26, 86), (22, 90), (28, 89)], fill=TRUNK_D2)
d.polygon([(36, 86), (42, 90), (37, 89)], fill=TRUNK_M)

# 3. Pine Foliage Tiers (from bottom to top)
# Each tier is a conical skirt with jagged pine branch tufts
tiers = [
    # (top_y, bot_y, width_spread, curve)
    (54, 82, 28),  # Tier 4 (bottom skirt)
    (40, 66, 24),  # Tier 3
    (26, 48, 19),  # Tier 2
    (14, 34, 14),  # Tier 1
    (4,  20, 8),   # Tip Tier
]

cx = 32

for ty, by, spread in tiers:
    th = by - ty
    # Fill main cone
    poly = [(cx, ty), (cx + spread, by), (cx - spread, by)]
    d.polygon(poly, fill=PINE_D1)
    
    # Bottom jagged fringe (pine needle tufts)
    num_teeth = spread // 3 + 1
    for i in range(-num_teeth, num_teeth + 1):
        bx = cx + int(i * (spread / num_teeth))
        tooth_len = 3 + (abs(i) % 2) * 2
        d.polygon([(bx - 2, by), (bx + 2, by), (bx, by + tooth_len)], fill=PINE_D2)
    
    # Left / Bottom shading
    d.polygon([(cx - spread, by), (cx, ty), (cx, by)], fill=PINE_D2)
    d.polygon([(cx - spread, by), (cx - spread//2, by), (cx - spread//2, by - 4), (cx - spread, by - 2)], fill=PINE_D3)
    
    # Under-skirt shadow
    d.rectangle([cx - spread + 2, by - 3, cx + spread - 2, by], fill=PINE_D3)
    
    # Sunlight highlights (top-right side)
    d.polygon([(cx, ty), (cx + spread - 3, by - 4), (cx + 2, ty + 4)], fill=PINE_M)
    d.polygon([(cx + 2, ty + 2), (cx + spread - 6, by - 8), (cx + 4, ty + 6)], fill=PINE_L)

    # Needle cluster highlights
    for ny in range(ty + 6, by - 4, 5):
        ratio = (ny - ty) / th
        r_spread = int(spread * ratio)
        hx = cx + int(r_spread * 0.45)
        d.line([(hx - 2, ny), (hx + 2, ny + 1)], fill=PINE_HL, width=1)
        d.line([(hx, ny - 1), (hx + 1, ny + 2)], fill=PINE_L, width=1)
        
        # Shadow notches on left
        sx = cx - int(r_spread * 0.5)
        d.line([(sx - 2, ny), (sx + 1, ny + 1)], fill=PINE_D3, width=1)

# Very top tip of pine
d.polygon([(cx, 2), (cx - 2, 7), (cx + 2, 7)], fill=PINE_L)
d.point([(cx, 2), (cx + 1, 3)], fill=PINE_HL)
d.point([(cx - 1, 4)], fill=PINE_D2)

# 4. Subtle outline pass (selective dark outline)
src = img.load()
out_img = img.copy()
opx = out_img.load()

for y in range(1, H - 1):
    for x in range(1, W - 1):
        _, _, _, a = src[x, y]
        if a < 20:
            # check neighbor
            for dx, dy in ((-1,0), (1,0), (0,-1), (0,1)):
                nr, ng, nb, na = src[x + dx, y + dy]
                if na > 150:
                    opx[x, y] = OUTLINE
                    break

# Save standard files
out_img.save(f'{OUT}/pino.png')

# 8x preview
preview = out_img.resize((W * 8, H * 8), Image.NEAREST)
preview.save(f'{OUT}/pino_preview_8x.png')
preview.save(f'{BRAIN}/pino_preview_8x.png')

# Save ASE
from ase_format import save_ase_multilayer
save_ase_multilayer(
    filepath=f'{OUT}/pino.ase',
    layers_data=[("Pino_Sprite", [out_img])],
    duration_ms=100
)

print(f"✓ Pino generado exitosamente: {OUT}/pino.png & pino.ase")

