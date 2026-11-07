#!/usr/bin/env python3
"""
Pixel-Perfect Top-Down RPG Hero (24x24)
Zero gaps, connected anatomy, clean anime/Zelda styling.
"""
import sys, os
from PIL import Image

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

W, H = 24, 24
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

_  = (0, 0, 0, 0)
OL = (24, 20, 32, 255)       # Clean dark outline
SH = (20, 20, 30, 75)        # Ground shadow

# Hair (Chestnut Amber)
H0 = (55, 30, 20, 255)       # Darkest shadow
H1 = (100, 52, 28, 255)      # Shadow
H2 = (155, 88, 44, 255)      # Base midtone
H3 = (205, 130, 65, 255)     # Highlight
H4 = (240, 175, 105, 255)    # Light glint

# Skin (Warm RPG tone)
S0 = (175, 105, 80, 255)     # Deep shadow
S1 = (220, 150, 115, 255)    # Mid shadow
S2 = (248, 195, 165, 255)    # Base
S3 = (255, 222, 200, 255)    # Highlight
BL = (235, 135, 135, 255)    # Blush
EYE = (32, 24, 38, 255)      # Eye pupil
GL  = (255, 255, 255, 255)   # Eye shine

# Tunic (Forest / Emerald Green)
T0 = (18, 45, 35, 255)
T1 = (28, 78, 60, 255)
T2 = (44, 122, 92, 255)
T3 = (68, 168, 128, 255)
WHT = (242, 246, 248, 255)   # Collar

# Leather / Boots
L0 = (45, 25, 16, 255)
L1 = (85, 48, 28, 255)
L2 = (135, 82, 48, 255)
GLD = (248, 195, 50, 255)

# Pants
P0 = (28, 32, 45, 255)
P1 = (48, 55, 75, 255)

# ==============================================================================
# DOWN (FRONT VIEW)
# ==============================================================================
# 24x24 grid: 
# Y: 0..1 (air)
# Y: 2..10 (Head & Hair)
# Y: 11..16 (Neck, Shoulders, Tunic, Belt)
# Y: 17..21 (Pants & Boots)
# Y: 22..23 (Ground shadow)
def get_down_matrix(step=0):
    bob = -1 if step in (1, 3) else 0
    m = [[_]*W for _ in range(H)]

    # Ground shadow
    for x in range(6, 18): m[22][x] = SH
    for x in range(8, 16): m[23][x] = SH

    # 1. Legs / Boots (Y = 17..21 + bob)
    # Stances:
    # step 0/2: Feet side-by-side
    # step 1: Left foot forward (lower), right foot lifted
    # step 3: Right foot forward (lower), left foot lifted
    ly = 17 + bob
    # Pelvis/Pants (connects directly to belt at Y=16)
    for x in range(8, 16): m[ly][x] = P1
    m[ly][7] = OL; m[ly][11] = OL; m[ly][12] = OL; m[ly][16] = OL

    if step in (0, 2):
        # Left leg
        m[ly+1][8] = P1; m[ly+1][9] = P1; m[ly+1][7] = OL; m[ly+1][10] = OL
        for y, x_range in enumerate([(7, 10), (7, 10), (7, 10)], start=ly+2):
            for x in range(x_range[0], x_range[1]+1): m[y][x] = L1
            m[y][x_range[0]-1] = OL; m[y][x_range[1]+1] = OL
        m[ly+2][8] = L2; m[ly+3][9] = L0; m[ly+4][9] = L0
        for x in range(7, 11): m[ly+5][x] = OL
        # Right leg
        m[ly+1][14] = P1; m[ly+1][15] = P1; m[ly+1][13] = OL; m[ly+1][16] = OL
        for y, x_range in enumerate([(13, 16), (13, 16), (13, 16)], start=ly+2):
            for x in range(x_range[0], x_range[1]+1): m[y][x] = L1
            m[y][x_range[0]-1] = OL; m[y][x_range[1]+1] = OL
        m[ly+2][15] = L2; m[ly+3][14] = L0; m[ly+4][14] = L0
        for x in range(13, 17): m[ly+5][x] = OL

    elif step == 1:
        # Left leg forward (strides down 1px)
        for y in range(ly+1, ly+5):
            for x in range(7, 11): m[y][x] = L1
            m[y][6] = OL; m[y][11] = OL
        m[ly+2][8] = L2; m[ly+4][8] = L0; m[ly+4][9] = L0
        for x in range(7, 11): m[ly+5][x] = OL
        # Right leg lifted (1px shorter)
        for y in range(ly+1, ly+4):
            for x in range(13, 17): m[y][x] = L1
            m[y][12] = OL; m[y][17] = OL
        m[ly+2][15] = L2; m[ly+3][14] = L0
        for x in range(13, 17): m[ly+4][x] = OL

    elif step == 3:
        # Left leg lifted
        for y in range(ly+1, ly+4):
            for x in range(7, 11): m[y][x] = L1
            m[y][6] = OL; m[y][11] = OL
        m[ly+2][8] = L2; m[ly+3][9] = L0
        for x in range(7, 11): m[ly+4][x] = OL
        # Right leg forward (strides down 1px)
        for y in range(ly+1, ly+5):
            for x in range(13, 17): m[y][x] = L1
            m[y][12] = OL; m[y][17] = OL
        m[ly+2][15] = L2; m[ly+4][14] = L0; m[ly+4][15] = L0
        for x in range(13, 17): m[ly+5][x] = OL

    # 2. Torso (Y = 11..16 + bob)
    ty = 11 + bob
    # Shoulders row (ty) - connects solidly under neck
    for x in range(7, 17): m[ty][x] = T2
    m[ty][11] = WHT; m[ty][12] = WHT # V-collar
    m[ty][6] = OL; m[ty][17] = OL
    
    # Chest & Sleeves (ty+1, ty+2)
    for y in (ty+1, ty+2):
        for x in range(6, 18): m[y][x] = T2
        m[y][5] = OL; m[y][18] = OL
    m[ty+1][11] = WHT; m[ty+1][12] = WHT # collar tip
    m[ty+1][8] = T3; m[ty+2][8] = T3 # highlight
    m[ty+1][15] = T1; m[ty+2][15] = T1 # shadow

    # Waist / Hands row (ty+3, ty+4)
    for y in (ty+3, ty+4):
        for x in range(7, 17): m[y][x] = T2
        m[y][6] = OL; m[y][17] = OL
    # Hands at sides
    m[ty+3][5] = S2; m[ty+3][4] = OL; m[ty+4][5] = S1; m[ty+4][4] = OL
    m[ty+3][18] = S2; m[ty+3][19] = OL; m[ty+4][18] = S1; m[ty+4][19] = OL
    m[ty+5][5] = OL; m[ty+5][18] = OL

    # Belt row (ty+5) - SOLID, connects directly to legs
    for x in range(7, 17): m[ty+5][x] = L1
    m[ty+5][6] = OL; m[ty+5][17] = OL
    m[ty+5][11] = GLD; m[ty+5][12] = GLD # Gold Buckle

    # 3. Head & Hair (Y = 2..10 + bob)
    hy = 2 + bob
    # Hair Top Dome
    for x in range(8, 16): m[hy][x] = OL
    for x in range(7, 17): m[hy+1][x] = H2
    m[hy+1][6] = OL; m[hy+1][17] = OL
    for x in range(6, 18): m[hy+2][x] = H2
    m[hy+2][5] = OL; m[hy+2][18] = OL
    # Hair glints
    m[hy+1][10] = H4; m[hy+1][11] = H4; m[hy+2][9] = H3; m[hy+2][10] = H3; m[hy+2][11] = H3

    # Hair mid row / Bangs
    for x in range(6, 18): m[hy+3][x] = H2
    m[hy+3][5] = OL; m[hy+3][18] = OL
    m[hy+3][15] = H1; m[hy+3][16] = H0 # hair shadow right

    # Face Skin area (hy+4..hy+8)
    for y in range(hy+4, hy+9):
        for x in range(6, 18): m[y][x] = S2
        m[y][5] = OL; m[y][18] = OL

    # Bangs locks overlapping forehead
    m[hy+4][6] = H2; m[hy+4][7] = H2; m[hy+4][11] = H3; m[hy+4][12] = H2; m[hy+4][16] = H1; m[hy+4][17] = H0
    m[hy+5][6] = H1; m[hy+5][7] = H2; m[hy+5][16] = H0; m[hy+5][17] = H0
    m[hy+6][6] = H0; m[hy+6][17] = H0

    # Cute Expressive Eyes (hy+6, hy+7)
    # Left eye: x=8,9 | Right eye: x=14,15
    for y in (hy+6, hy+7):
        m[y][8] = EYE; m[y][9] = EYE
        m[y][14] = EYE; m[y][15] = EYE
    m[hy+6][8] = GL; m[hy+6][14] = GL # White catchlights

    # Cheeks / Blush (hy+8)
    m[hy+8][7] = BL; m[hy+8][16] = BL

    # Chin / Jawline (hy+9, hy+10)
    for x in range(7, 17): m[hy+9][x] = S1
    m[hy+9][6] = OL; m[hy+9][17] = OL
    # Chin taper
    m[hy+10][6] = _; m[hy+10][7] = OL
    for x in range(8, 16): m[hy+10][x] = S0 # Neck shadow
    m[hy+10][16] = OL; m[hy+10][17] = _

    return m

# ==============================================================================
# UP (BACK VIEW)
# ==============================================================================
def get_up_matrix(step=0):
    bob = -1 if step in (1, 3) else 0
    m = [[_]*W for _ in range(H)]

    # Ground shadow
    for x in range(6, 18): m[22][x] = SH
    for x in range(8, 16): m[23][x] = SH

    # Legs & Boots
    ly = 17 + bob
    for x in range(8, 16): m[ly][x] = P1
    m[ly][7] = OL; m[ly][11] = OL; m[ly][12] = OL; m[ly][16] = OL

    if step in (0, 2):
        for y in range(ly+1, ly+5):
            for x in range(7, 11): m[y][x] = L0
            m[y][6] = OL; m[y][11] = OL
            for x in range(13, 17): m[y][x] = L0
            m[y][12] = OL; m[y][17] = OL
        for x in range(7, 11): m[ly+5][x] = OL
        for x in range(13, 17): m[ly+5][x] = OL
    elif step == 1:
        # Left foot step
        for y in range(ly+1, ly+4):
            for x in range(7, 11): m[y][x] = L1
            m[y][6] = OL; m[y][11] = OL
        for x in range(7, 11): m[ly+4][x] = OL
        for y in range(ly+1, ly+5):
            for x in range(13, 17): m[y][x] = L0
            m[y][12] = OL; m[y][17] = OL
        for x in range(13, 17): m[ly+5][x] = OL
    elif step == 3:
        for y in range(ly+1, ly+5):
            for x in range(7, 11): m[y][x] = L0
            m[y][6] = OL; m[y][11] = OL
        for x in range(7, 11): m[ly+5][x] = OL
        for y in range(ly+1, ly+4):
            for x in range(13, 17): m[y][x] = L1
            m[y][12] = OL; m[y][17] = OL
        for x in range(13, 17): m[ly+4][x] = OL

    # Torso (Back view with backpack)
    ty = 11 + bob
    # Shoulders
    for x in range(7, 17): m[ty][x] = T1
    m[ty][6] = OL; m[ty][17] = OL
    for y in (ty+1, ty+2):
        for x in range(6, 18): m[y][x] = T1
        m[y][5] = OL; m[y][18] = OL
    # Backpack (rests in center x=8..15, y=ty+1..ty+4)
    for y in range(ty+1, ty+5):
        for x in range(8, 16): m[y][x] = L1
        m[y][7] = OL; m[y][16] = OL
    m[ty+1][10] = L2; m[ty+1][11] = L2; m[ty+1][12] = L2; m[ty+1][13] = L2 # top flap highlight
    m[ty+2][11] = GLD; m[ty+2][12] = GLD # backpack buckle
    m[ty+4][8] = L0; m[ty+4][15] = L0 # side depth

    # Belt line
    for x in range(7, 17): m[ty+5][x] = L1
    m[ty+5][6] = OL; m[ty+5][17] = OL

    # Head (Back of Hair - voluminous, rounded, layered)
    hy = 2 + bob
    for x in range(8, 16): m[hy][x] = OL
    for x in range(7, 17): m[hy+1][x] = H2
    m[hy+1][6] = OL; m[hy+1][17] = OL
    for y in range(hy+2, hy+9):
        for x in range(6, 18): m[y][x] = H2
        m[y][5] = OL; m[y][18] = OL
    # Hair volume highlight & shadows
    m[hy+2][10] = H3; m[hy+2][11] = H4; m[hy+2][12] = H3
    for y in range(hy+5, hy+9):
        for x in range(14, 18): m[y][x] = H1
        m[y][17] = H0
    # Hair bottom nape
    for x in range(7, 17): m[hy+9][x] = H1
    m[hy+9][6] = OL; m[hy+9][17] = OL
    for x in range(8, 16): m[hy+10][x] = H0
    m[hy+10][7] = OL; m[hy+10][16] = OL

    return m

# ==============================================================================
# RIGHT (SIDE PROFILE)
# ==============================================================================
# Natural anime chibi side silhouette: rounded head, subtle nose curve,
# solid connected body, clean walking stride.
def get_right_matrix(step=0):
    bob = -1 if step in (1, 3) else 0
    m = [[_]*W for _ in range(H)]

    # Ground shadow
    for x in range(7, 18): m[22][x] = SH
    for x in range(9, 16): m[23][x] = SH

    # Legs & Boots
    ly = 17 + bob
    for x in range(10, 15): m[ly][x] = P1
    m[ly][9] = OL; m[ly][15] = OL

    if step in (0, 2):
        # Standing stance: front boot & slightly visible rear boot
        for y in range(ly+1, ly+5):
            for x in range(10, 15): m[y][x] = L1
            m[y][9] = OL; m[y][15] = OL
        m[ly+2][12] = L2; m[ly+3][13] = L0; m[ly+4][14] = L0
        for x in range(10, 16): m[ly+5][x] = OL
    elif step == 1:
        # Right leg strides forward
        for y in range(ly+1, ly+5):
            for x in range(12, 17): m[y][x] = L1
            m[y][11] = OL; m[y][17] = OL
        m[ly+2][14] = L2
        for x in range(12, 17): m[ly+5][x] = OL
        # Left leg back
        for y in range(ly+1, ly+4):
            for x in range(8, 12): m[y][x] = L0
            m[y][7] = OL; m[y][12] = OL
        for x in range(8, 12): m[ly+4][x] = OL
    elif step == 3:
        # Left leg strides forward
        for y in range(ly+1, ly+4):
            for x in range(12, 16): m[y][x] = L0
            m[y][11] = OL; m[y][16] = OL
        for x in range(12, 16): m[ly+4][x] = OL
        # Right leg pushed back
        for y in range(ly+1, ly+5):
            for x in range(8, 12): m[y][x] = L1
            m[y][7] = OL; m[y][12] = OL
        for x in range(8, 12): m[ly+5][x] = OL

    # Torso (Side profile: Backpack at back, Tunic center, Arm at front)
    ty = 11 + bob
    # Shoulder / Chest row
    for x in range(8, 16): m[ty][x] = T2
    m[ty][15] = WHT # Collar corner
    m[ty][7] = OL; m[ty][16] = OL

    # Torso body (ty+1..ty+4)
    for y in range(ty+1, ty+5):
        # Backpack at back (x=7..9)
        m[y][7] = OL; m[y][8] = L1; m[y][9] = L1
        # Tunic middle
        for x in range(10, 16): m[y][x] = T2
        m[y][16] = OL
    m[ty+1][8] = L2 # backpack highlight

    # Arm with hand
    arm_x = 12 + (2 if step == 1 else (-1 if step == 3 else 0))
    for y in (ty+1, ty+2):
        m[y][arm_x] = T3
        m[y][arm_x-1] = OL; m[y][arm_x+1] = OL
    # Hand
    m[ty+3][arm_x] = S2; m[ty+3][arm_x-1] = OL; m[ty+3][arm_x+1] = OL
    m[ty+4][arm_x] = OL

    # Belt (ty+5)
    for x in range(9, 16): m[ty+5][x] = L1
    m[ty+5][12] = GLD
    m[ty+5][8] = OL; m[ty+5][16] = OL

    # Head (Side profile: Y = 2..10 + bob)
    hy = 2 + bob
    for x in range(9, 16): m[hy][x] = OL
    for x in range(8, 16): m[hy+1][x] = H2
    m[hy+1][7] = OL; m[hy+1][16] = OL
    for y in range(hy+2, hy+5):
        for x in range(7, 16): m[y][x] = H2
        m[y][6] = OL; m[y][16] = OL
    m[hy+1][12] = H4; m[hy+2][11] = H3; m[hy+2][12] = H3

    # Back hair curl
    for y in range(hy+5, hy+9):
        m[y][6] = OL; m[y][7] = H1; m[y][8] = H2
    m[hy+9][7] = OL; m[hy+9][8] = H0
    m[hy+10][8] = OL

    # Face Skin (hy+5..hy+9, x=9..15)
    for y in range(hy+5, hy+9):
        for x in range(9, 16): m[y][x] = S2
    # Bangs
    m[hy+4][13] = H2; m[hy+4][14] = H3; m[hy+4][15] = H2; m[hy+4][16] = OL
    m[hy+5][14] = H2; m[hy+5][15] = H1

    # Eye (hy+6, hy+7 at x=13)
    m[hy+6][13] = EYE; m[hy+7][13] = EYE
    m[hy+6][13] = GL # Glint
    m[hy+8][14] = BL # Blush

    # Smooth profile curve (NO giant nose!)
    # y=hy+5: forehead
    m[hy+5][16] = OL
    # y=hy+6: eye brow line
    m[hy+6][16] = OL
    # y=hy+7: soft nose curve (just at x=16, no jutting!)
    m[hy+7][16] = OL
    # y=hy+8: mouth/cheek
    m[hy+8][15] = OL
    # y=hy+9: chin
    for x in range(9, 15): m[hy+9][x] = S1
    m[hy+9][15] = OL
    # y=hy+10: neck
    for x in range(9, 14): m[hy+10][x] = S0
    m[hy+10][8] = OL; m[hy+10][14] = OL

    return m

def mat_to_img(mat):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            im.putpixel((x, y), mat[y][x])
    return im

# Build frames
down_frames  = [mat_to_img(get_down_matrix(i)) for i in range(4)]
up_frames    = [mat_to_img(get_up_matrix(i)) for i in range(4)]
right_frames = [mat_to_img(get_right_matrix(i)) for i in range(4)]
left_frames  = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in right_frames]

all_16 = down_frames + up_frames + right_frames + left_frames

# 4x4 Grid Spritesheet (96x96 px)
grid_sheet = Image.new('RGBA', (W * 4, H * 4), (0, 0, 0, 0))
dirs = [down_frames, up_frames, right_frames, left_frames]
for r, d_f in enumerate(dirs):
    for c, f in enumerate(d_f):
        grid_sheet.paste(f, (c * W, r * H))

grid_sheet.save(f"{TARGET_DIR}/personaje_walk_grid.png")
grid_prev = grid_sheet.resize((W * 4 * 8, H * 4 * 8), Image.NEAREST)
grid_prev.save(f"{TARGET_DIR}/personaje_walk_preview_8x.png")
grid_prev.save(f"{BRAIN}/personaje_v3_preview_8x.png")

# Base individual PNGs
down_frames[0].save(f"{TARGET_DIR}/personaje_down.png")
up_frames[0].save(f"{TARGET_DIR}/personaje_up.png")
right_frames[0].save(f"{TARGET_DIR}/personaje_right.png")
left_frames[0].save(f"{TARGET_DIR}/personaje_left.png")

# Horizontal 4-dir strip
strip_4dir = Image.new('RGBA', (W * 4, H), (0, 0, 0, 0))
for i, f in enumerate([down_frames[0], up_frames[0], right_frames[0], left_frames[0]]):
    strip_4dir.paste(f, (i * W, 0))
strip_4dir.save(f"{TARGET_DIR}/personaje_spritesheet.png")

# Save ASE with tags
tags = [
    {"name": "Walk_Down",  "from": 0,  "to": 3,  "anim_direction": 0, "color": (80, 200, 100)},
    {"name": "Walk_Up",    "from": 4,  "to": 7,  "anim_direction": 0, "color": (80, 150, 240)},
    {"name": "Walk_Right", "from": 8,  "to": 11, "anim_direction": 0, "color": (240, 180, 60)},
    {"name": "Walk_Left",  "from": 12, "to": 15, "anim_direction": 0, "color": (240, 100, 180)},
]

save_ase_multilayer(
    filepath=f"{TARGET_DIR}/personaje_animado.ase",
    layers_data=[("Hero_Walk", all_16)],
    duration_ms=140,
    tags=tags
)
save_ase_multilayer(
    filepath=f"{TARGET_DIR}/personaje.ase",
    layers_data=[("Hero_Base", [down_frames[0], up_frames[0], right_frames[0], left_frames[0]])],
    duration_ms=140,
    tags=[
        {"name": "Down",  "from": 0, "to": 0, "anim_direction": 0, "color": (100, 200, 100)},
        {"name": "Up",    "from": 1, "to": 1, "anim_direction": 0, "color": (100, 150, 240)},
        {"name": "Right", "from": 2, "to": 2, "anim_direction": 0, "color": (240, 180, 80)},
        {"name": "Left",  "from": 3, "to": 3, "anim_direction": 0, "color": (240, 100, 180)},
    ]
)

# Smooth Animated Demo GIF
combo = []
for i in range(4):
    c_img = Image.new('RGBA', (W * 2, H * 2), (242, 244, 248, 255))
    c_img.paste(down_frames[i], (0, 0), down_frames[i])
    c_img.paste(up_frames[i], (W, 0), up_frames[i])
    c_img.paste(right_frames[i], (0, H), right_frames[i])
    c_img.paste(left_frames[i], (W, H), left_frames[i])
    c_up = c_img.resize((W * 2 * 6, H * 2 * 6), Image.NEAREST)
    combo.append(c_up.convert('RGB').quantize(colors=48, method=2))

combo[0].save(
    f"{TARGET_DIR}/walk_all_demo.gif",
    save_all=True, append_images=combo[1:],
    loop=0, duration=150, optimize=False
)
combo[0].save(
    f"{BRAIN}/walk_v3_demo.gif",
    save_all=True, append_images=combo[1:],
    loop=0, duration=150, optimize=False
)

print("✓ Sprite v3 pixel-perfect generado.")

