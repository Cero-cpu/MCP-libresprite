#!/usr/bin/env python3
"""
Tiny 8-bit unique character: "Champiñón Paladín" (16x16 px)
2-frame idle animation loop
"""
import sys, os
sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from PIL import Image

W, H = 16, 16
OUT = '/home/cachy/Escritorio'
BRAIN = '/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0'

# Palette (PICO-8 / Retro style)
_ = (0, 0, 0, 0)             # Transparent
K = (24, 20, 37, 255)         # Outline / Dark violet
C1 = (38, 92, 66, 255)        # Dark teal cap
C2 = (62, 137, 72, 255)       # Mid green cap
C3 = (99, 199, 77, 255)       # Bright lime cap
W1 = (254, 231, 97, 255)      # Yellow spore spots / cap glow
S1 = (238, 195, 154, 255)     # Skin face
E = (24, 20, 37, 255)         # Eyes
EH = (255, 255, 255, 255)     # Eye twinkle
M1 = (194, 133, 105, 255)     # Scarf/cape brown
L1 = (217, 87, 99, 255)       # Crimson badge
SW = (190, 200, 210, 255)     # Tiny blade
SG = (255, 213, 65, 255)      # Sword hilt

# Frame 0: Stand
f0 = [
    [_,_,_,_,K,K,K,K,K,K,_,_,_,_,_,_],
    [_,_,_,K,C3,C3,W1,C3,C3,C3,K,_,_,_,_,_],
    [_,_,K,C3,C3,C2,C2,C3,W1,C3,C3,K,_,_,_,_],
    [_,K,C3,W1,C2,C1,C1,C2,C2,C3,C3,C3,K,_,_,_],
    [_,K,C2,C2,C1,C1,C1,C1,C2,C2,C3,C3,K,_,_,_],
    [K,C2,C1,C1,C1,C1,C1,C1,C1,C1,C2,C2,C3,K,_,_],
    [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
    [_,_,K,S1,S1,S1,S1,S1,S1,S1,S1,K,SW,_,_,_],
    [_,_,K,S1,E,S1,S1,S1,E,S1,S1,K,SW,_,_,_],
    [_,_,K,S1,EH,S1,S1,S1,EH,S1,S1,K,SG,_,_,_],
    [_,_,K,S1,S1,S1,L1,S1,S1,S1,S1,K,K,_,_,_],
    [_,_,_,K,M1,M1,M1,M1,M1,M1,K,_,_,_,_,_],
    [_,_,_,K,M1,M1,M1,M1,M1,M1,K,_,_,_,_,_],
    [_,_,_,_,K,M1,K,_,K,M1,K,_,_,_,_,_],
    [_,_,_,K,K,K,_,_,_,K,K,K,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

# Frame 1: Bob down (breathing / step)
f1 = [
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,K,K,K,K,K,K,_,_,_,_,_,_],
    [_,_,_,K,C3,C3,W1,C3,C3,C3,K,_,_,_,_,_],
    [_,_,K,C3,C3,C2,C2,C3,W1,C3,C3,K,_,_,_,_],
    [_,K,C3,W1,C2,C1,C1,C2,C2,C3,C3,C3,K,_,_,_],
    [_,K,C2,C2,C1,C1,C1,C1,C2,C2,C3,C3,K,_,_,_],
    [K,C2,C1,C1,C1,C1,C1,C1,C1,C1,C2,C2,C3,K,_,_],
    [K,K,K,K,K,K,K,K,K,K,K,K,K,K,K,K],
    [_,_,K,S1,S1,S1,S1,S1,S1,S1,S1,K,SW,_,_,_],
    [_,_,K,S1,E,S1,S1,S1,E,S1,S1,K,SW,_,_,_],
    [_,_,K,S1,EH,S1,L1,S1,EH,S1,S1,K,SG,_,_,_],
    [_,_,_,K,M1,M1,M1,M1,M1,M1,K,_,K,_,_,_],
    [_,_,_,K,M1,M1,M1,M1,M1,M1,K,_,_,_,_,_],
    [_,_,_,K,K,K,_,_,_,K,K,K,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

def matrix_to_img(mat):
    im = Image.new('RGBA', (W, H))
    for y in range(H):
        for x in range(W):
            im.putpixel((x, y), mat[y][x])
    return im

img0 = matrix_to_img(f0)
img1 = matrix_to_img(f1)
frames = [img0, img1]

# 1. Base PNG
img0.save(f'{OUT}/personaje_8bit.png')

# 2. Spritesheet
sheet = Image.new('RGBA', (W * 2, H), (0, 0, 0, 0))
sheet.paste(img0, (0, 0))
sheet.paste(img1, (W, 0))
sheet.save(f'{OUT}/personaje_8bit_sheet.png')

# 3. GIF (bucle retro)
gif_p = [f.convert('RGB').quantize(colors=32, method=2) for f in [img0, img1]]
gif_p[0].save(
    f'{OUT}/personaje_8bit.gif',
    save_all=True, append_images=[gif_p[1]],
    loop=0, duration=220, optimize=False
)

# 4. Preview 16x (256x256 px)
prev = img0.resize((W * 16, H * 16), Image.NEAREST)
prev.save(f'{OUT}/personaje_8bit_preview_16x.png')
prev.save(f'{BRAIN}/personaje_8bit_preview_16x.png')

# 5. ASE nativo LibreSprite
from ase_format import save_ase_multilayer
save_ase_multilayer(
    filepath=f'{OUT}/personaje_8bit.ase',
    layers_data=[("Hero_8Bit", frames)],
    duration_ms=220,
    tags=[{"name": "Idle", "from": 0, "to": 1, "anim_direction": 0, "color": (120, 200, 80)}]
)

print(f"✓ Personaje 8-bit 'Champiñón Paladín' creado en {OUT}")

