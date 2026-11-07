#!/usr/bin/env python3
"""
Top-Down 4-Direction Walk Cycle Generator
Canvas: 24x24 px per frame
Animations:
- Walk_Down (4 frames: 0-3)
- Walk_Up (4 frames: 4-7)
- Walk_Right (4 frames: 8-11)
- Walk_Left (4 frames: 12-15)
Total: 16 frames
"""
import sys, os
from PIL import Image

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

W, H = 24, 24
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

_  = (0, 0, 0, 0)
OL = (20, 16, 28, 255)
SH = (15, 12, 22, 90)

# Hair
H1 = (60, 32, 18, 255)
H2 = (115, 62, 32, 255)
H3 = (175, 105, 52, 255)
H4 = (220, 150, 85, 255)

# Skin
S1 = (175, 110, 85, 255)
S2 = (225, 165, 130, 255)
S3 = (250, 210, 185, 255)
EYE = (25, 20, 32, 255)
EYE_HI = (255, 255, 255, 255)

# Tunic
T1 = (18, 48, 38, 255)
T2 = (30, 88, 62, 255)
T3 = (48, 140, 96, 255)
T4 = (80, 188, 130, 255)
WH = (235, 240, 245, 255)

# Leather / Buckle
L1 = (45, 26, 18, 255)
L2 = (90, 52, 34, 255)
L3 = (145, 88, 55, 255)
BK = (245, 195, 65, 255)

# Pants / Boots
P1 = (28, 32, 48, 255)
P2 = (44, 52, 75, 255)
B1 = (40, 24, 16, 255)
B2 = (75, 45, 28, 255)

def mat_to_img(mat):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for y in range(min(H, len(mat))):
        row = mat[y]
        for x in range(min(W, len(row))):
            im.putpixel((x, y), row[x])
    return im

def shift_vertical(mat, dy):
    """Bobs head/torso vertically by dy pixels while keeping ground/shadow in place."""
    out = [[_]*W for _ in range(H)]
    for y in range(min(H, len(mat))):
        row = mat[y]
        for x in range(min(W, len(row))):
            c = row[x]
            if c == SH:
                out[y][x] = SH
            elif c != _:
                ny = y + dy
                if 0 <= ny < H:
                    out[ny][x] = c
    return out

# Base templates
from generate_topdown_hero import down_matrix, up_matrix, right_matrix

# -------------------------------------------------------------
# DOWN WALK FRAMES
# -------------------------------------------------------------
# Frame 0: Idle down
f_down_0 = down_matrix

# Frame 1: Left foot step forward (foot lowers, left arm swings forward)
f_down_1 = [row[:] for row in down_matrix]
f_down_1[17] = [_,_,_,_,_,_,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_down_1[18] = [_,_,_,_,_,_,OL,B2,B2,OL,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_]
f_down_1[19] = [_,_,_,_,_,_,OL,B1,B1,OL,OL,B1,B1,OL,_,_,_,_,_,_,_,_,_,_]
f_down_1[20] = [_,_,_,_,_,_,OL,OL,OL,_,OL,OL,OL,_,_,_,_,_,_,_,_,_,_,_]
f_down_1 = shift_vertical(f_down_1, -1)

# Frame 2: Idle pass
f_down_2 = down_matrix

# Frame 3: Right foot step forward
f_down_3 = [row[:] for row in down_matrix]
f_down_3[17] = [_,_,_,_,_,_,_,_,_,_,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_]
f_down_3[18] = [_,_,_,_,_,_,OL,B2,B2,OL,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_]
f_down_3[19] = [_,_,_,_,_,_,OL,B1,B1,OL,OL,B1,B1,OL,_,_,_,_,_,_,_,_,_,_]
f_down_3[20] = [_,_,_,_,_,_,_,OL,OL,OL,_,OL,OL,OL,_,_,_,_,_,_,_,_,_,_]
f_down_3 = shift_vertical(f_down_3, -1)

# -------------------------------------------------------------
# UP WALK FRAMES
# -------------------------------------------------------------
f_up_0 = up_matrix

f_up_1 = [row[:] for row in up_matrix]
f_up_1[17] = [_,_,_,_,_,_,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_up_1[18] = [_,_,_,_,_,_,OL,B2,B2,OL,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_]
f_up_1[19] = [_,_,_,_,_,_,OL,B1,B1,OL,OL,B1,B1,OL,_,_,_,_,_,_,_,_,_,_]
f_up_1 = shift_vertical(f_up_1, -1)

f_up_2 = up_matrix

f_up_3 = [row[:] for row in up_matrix]
f_up_3[17] = [_,_,_,_,_,_,_,_,_,_,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_]
f_up_3[18] = [_,_,_,_,_,_,OL,B2,B2,OL,OL,B2,B2,OL,_,_,_,_,_,_,_,_,_,_]
f_up_3[19] = [_,_,_,_,_,_,OL,B1,B1,OL,OL,B1,B1,OL,_,_,_,_,_,_,_,_,_,_]
f_up_3 = shift_vertical(f_up_3, -1)

# -------------------------------------------------------------
# RIGHT WALK FRAMES
# -------------------------------------------------------------
f_right_0 = right_matrix

# Frame 1: Right leg forward stride
f_right_1 = [row[:] for row in right_matrix]
f_right_1[17] = [_,_,_,_,_,_,_,OL,B2,B2,B2,OL,_,_,_,_,_,_,_,_,_,_,_,_]
f_right_1[18] = [_,_,_,_,_,OL,B2,B1,B1,B1,OL,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_right_1[19] = [_,_,_,_,_,OL,OL,OL,OL,OL,_,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_right_1 = shift_vertical(f_right_1, -1)

f_right_2 = right_matrix

# Frame 3: Left leg back stride
f_right_3 = [row[:] for row in right_matrix]
f_right_3[17] = [_,_,_,_,_,OL,B2,B2,B1,OL,_,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_right_3[18] = [_,_,_,_,_,_,OL,B1,B1,B2,OL,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_right_3[19] = [_,_,_,_,_,_,OL,OL,OL,OL,_,_,_,_,_,_,_,_,_,_,_,_,_,_]
f_right_3 = shift_vertical(f_right_3, -1)

# Generate PIL Images
down_imgs  = [mat_to_img(m) for m in [f_down_0, f_down_1, f_down_2, f_down_3]]
up_imgs    = [mat_to_img(m) for m in [f_up_0, f_up_1, f_up_2, f_up_3]]
right_imgs = [mat_to_img(m) for m in [f_right_0, f_right_1, f_right_2, f_right_3]]
left_imgs  = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in right_imgs]

all_frames = down_imgs + up_imgs + right_imgs + left_imgs

# Spritesheet (16 frames: 4x4 grid or 16x1 horizontal)
# Let's save a clean 4 columns x 4 rows spritesheet (96x96 px)
grid_sheet = Image.new('RGBA', (W * 4, H * 4), (0, 0, 0, 0))
dirs = [down_imgs, up_imgs, right_imgs, left_imgs]
for row_idx, d_imgs in enumerate(dirs):
    for col_idx, f_img in enumerate(d_imgs):
        grid_sheet.paste(f_img, (col_idx * W, row_idx * H))

grid_sheet.save(f"{TARGET_DIR}/personaje_walk_grid.png")

# Horizontal strip (384x24 px)
strip_sheet = Image.new('RGBA', (W * 16, H), (0, 0, 0, 0))
for i, f_img in enumerate(all_frames):
    strip_sheet.paste(f_img, (i * W, 0))
strip_sheet.save(f"{TARGET_DIR}/personaje_walk_strip.png")

# Preview 8x of Grid
preview = grid_sheet.resize((W * 4 * 8, H * 4 * 8), Image.NEAREST)
preview.save(f"{TARGET_DIR}/personaje_walk_preview_8x.png")
preview.save(f"{BRAIN}/personaje_walk_preview_8x.png")

# Animated GIFs for each direction and full demo
gif_down = [f.convert('RGB').quantize(colors=32, method=2) for f in down_imgs]
gif_down[0].save(
    f"{TARGET_DIR}/walk_down.gif",
    save_all=True, append_images=gif_down[1:],
    loop=0, duration=150, optimize=False
)

# LibreSprite Multilayer Project with Tags
tags = [
    {"name": "Walk_Down",  "from": 0,  "to": 3,  "anim_direction": 0, "color": (100, 220, 100)},
    {"name": "Walk_Up",    "from": 4,  "to": 7,  "anim_direction": 0, "color": (100, 160, 240)},
    {"name": "Walk_Right", "from": 8,  "to": 11, "anim_direction": 0, "color": (240, 190, 80)},
    {"name": "Walk_Left",  "from": 12, "to": 15, "anim_direction": 0, "color": (240, 110, 190)},
]

save_ase_multilayer(
    filepath=f"{TARGET_DIR}/personaje_animado.ase",
    layers_data=[("Hero_Walk", all_frames)],
    duration_ms=150,
    tags=tags
)

print(f"✓ Walk Cycle completo (16 frames) generado en: {TARGET_DIR}")
