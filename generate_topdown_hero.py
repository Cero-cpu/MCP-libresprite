#!/usr/bin/env python3
"""
Top-Down 4-Direction Character Generator
Canvas: 24x24 px per frame
Directions: Down (0), Up (1), Right (2), Left (3)
"""
import sys, os
from PIL import Image

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

W, H = 24, 24
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

_  = (0, 0, 0, 0)
OL = (20, 16, 28, 255)       # Outline dark plum/charcoal
SH = (15, 12, 22, 90)        # Ground shadow

# Hair (Chestnut/Amber)
H1 = (60, 32, 18, 255)       # Dark shadow
H2 = (115, 62, 32, 255)      # Mid tone
H3 = (175, 105, 52, 255)     # Highlight
H4 = (220, 150, 85, 255)     # Bright strand

# Skin
S1 = (175, 110, 85, 255)     # Shadow
S2 = (225, 165, 130, 255)    # Mid
S3 = (250, 210, 185, 255)    # Highlight
EYE = (25, 20, 32, 255)      # Dark eye
EYE_HI = (255, 255, 255, 255)

# Tunic (Adventurer Emerald / Forest Green)
T1 = (18, 48, 38, 255)       # Dark
T2 = (30, 88, 62, 255)       # Mid
T3 = (48, 140, 96, 255)      # Light
T4 = (80, 188, 130, 255)     # Highlight rim
WH = (235, 240, 245, 255)    # Shirt collar white

# Leather / Belt / Satchel
L1 = (45, 26, 18, 255)       # Dark leather
L2 = (90, 52, 34, 255)       # Mid leather
L3 = (145, 88, 55, 255)      # Light leather
BK = (245, 195, 65, 255)     # Brass buckle

# Pants & Boots
P1 = (28, 32, 48, 255)       # Dark navy pants
P2 = (44, 52, 75, 255)       # Mid navy pants
B1 = (40, 24, 16, 255)       # Boot shadow
B2 = (75, 45, 28, 255)       # Boot mid

# -------------------------------------------------------------
# 1. DOWN (FRENTE / ABAJO)
# -------------------------------------------------------------
down_matrix = [
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,OL,OL,OL,OL,OL,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,H3,H3,H4,H3,H3,H3,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,H2,H3,H4,H4,H3,H3,H2,H2,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H2,H3,H3,H3,H2,H2,H3,H2,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H2,S2,S2,S2,S2,S2,H2,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,S2,S3,S3,S3,S3,S3,S2,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,S1,S2,EYE,S3,S3,S3,EYE,S2,S1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,S1,S2,EYE_HI,S2,S1,S2,EYE_HI,S2,S1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,S1,S2,S2,S2,S2,S2,S1,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,T1,OL,WH,WH,WH,WH,OL,T1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,OL,T2,T2,OL,T3,T3,T2,T2,OL,T2,T1,OL,_,_,_,_,_,_,_],
    [_,_,_,_,OL,T3,T2,OL,T3,T3,T2,T2,OL,T2,T1,OL,_,_,_,_,_,_,_],
    [_,_,_,_,OL,S2,S1,OL,L2,BK,L2,L2,OL,S2,S1,OL,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,OL,OL,T2,T3,T2,T1,OL,OL,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,P2,P2,P1,P1,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,P2,P2,P1,P1,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,B2,B2,OL,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,B1,B1,OL,OL,B1,B1,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,OL,OL,_,_,OL,OL,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,SH,SH,SH,SH,SH,SH,SH,SH,SH,SH,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,SH,SH,SH,SH,SH,SH,SH,SH,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

# -------------------------------------------------------------
# 2. UP (ESPALDA / ARRIBA)
# -------------------------------------------------------------
up_matrix = [
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,OL,OL,OL,OL,OL,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,H3,H3,H4,H3,H3,H3,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,H2,H3,H4,H4,H3,H3,H2,H2,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H2,H2,H3,H3,H2,H2,H2,H1,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H2,H2,H2,H2,H2,H1,H1,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H1,H2,H2,H2,H1,H1,H1,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H1,H1,H1,H1,H1,H1,H1,H1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,H1,H1,H1,H1,H1,H1,H1,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,S1,S1,S1,S1,S1,S1,S1,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,T1,OL,T2,T2,T2,T2,OL,T1,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,OL,T2,T2,OL,L2,L3,L3,L2,OL,T2,T1,OL,_,_,_,_,_,_,_],
    [_,_,_,_,OL,T2,T1,OL,L2,L3,L3,L2,OL,T2,T1,OL,_,_,_,_,_,_,_],
    [_,_,_,_,OL,S2,S1,OL,L1,L2,L2,L1,OL,S2,S1,OL,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,OL,OL,T2,T2,T1,T1,OL,OL,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,P2,P2,P1,P1,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,P2,P2,P1,P1,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,B2,B2,OL,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,B1,B1,OL,OL,B1,B1,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,OL,OL,_,_,OL,OL,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,SH,SH,SH,SH,SH,SH,SH,SH,SH,SH,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,SH,SH,SH,SH,SH,SH,SH,SH,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

# -------------------------------------------------------------
# 3. RIGHT (PERFIL DERECHA)
# -------------------------------------------------------------
right_matrix = [
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,OL,OL,OL,OL,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,H3,H4,H3,H3,H3,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,H2,H3,H4,H3,H3,H2,OL,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H2,H2,H3,H2,S2,S3,S3,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H2,H2,S2,S3,S3,S3,S2,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H1,H1,S2,S3,EYE,S3,OL,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,H1,H1,S1,S2,S3,EYE_HI,S2,OL,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,H1,S1,S2,S2,S2,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,S1,S1,S2,S2,OL,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,L1,OL,WH,WH,OL,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,OL,L2,L3,OL,T3,T3,T2,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,OL,L2,L2,OL,T3,T2,T1,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,OL,L1,L1,OL,L2,BK,L2,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,OL,OL,OL,T2,T2,T1,OL,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,P2,P2,P1,OL,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,OL,P2,P2,P1,OL,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,B2,B2,B1,OL,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,B1,B1,B1,OL,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,OL,OL,OL,OL,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,SH,SH,SH,SH,SH,SH,SH,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,SH,SH,SH,SH,SH,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
    [_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_,_],
]

def mat_to_img(mat):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for y in range(min(H, len(mat))):
        row = mat[y]
        for x in range(min(W, len(row))):
            im.putpixel((x, y), row[x])
    return im

img_down  = mat_to_img(down_matrix)
img_up    = mat_to_img(up_matrix)
img_right = mat_to_img(right_matrix)
# Left is horizontal flip of right
img_left  = img_right.transpose(Image.FLIP_LEFT_RIGHT)

frames = [img_down, img_up, img_right, img_left]
names  = ["down", "up", "right", "left"]

# Save single PNGs
for f, name in zip(frames, names):
    f.save(f"{TARGET_DIR}/personaje_{name}.png")

# Spritesheet (96x24 px)
sheet = Image.new('RGBA', (W * 4, H), (0, 0, 0, 0))
for i, f in enumerate(frames):
    sheet.paste(f, (i * W, 0))
sheet.save(f"{TARGET_DIR}/personaje_spritesheet.png")

# Preview 8x (768x192 px)
prev_sheet = sheet.resize((W * 4 * 8, H * 8), Image.NEAREST)
prev_sheet.save(f"{TARGET_DIR}/personaje_preview_8x.png")
prev_sheet.save(f"{BRAIN}/personaje_topdown_preview_8x.png")

# Native ASE for LibreSprite with 4 Direction Tags
tags = [
    {"name": "Down",  "from": 0, "to": 0, "anim_direction": 0, "color": (100, 200, 100)},
    {"name": "Up",    "from": 1, "to": 1, "anim_direction": 0, "color": (100, 150, 240)},
    {"name": "Right", "from": 2, "to": 2, "anim_direction": 0, "color": (240, 180, 80)},
    {"name": "Left",  "from": 3, "to": 3, "anim_direction": 0, "color": (240, 100, 180)},
]

save_ase_multilayer(
    filepath=f"{TARGET_DIR}/personaje.ase",
    layers_data=[("Hero_Base", frames)],
    duration_ms=150,
    tags=tags
)

print(f"✓ Personaje Top-Down en 4 direcciones creado con éxito en: {TARGET_DIR}")
