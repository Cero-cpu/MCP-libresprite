#!/usr/bin/env python3
"""
Professional Top-Down Character Redesign (24x24 px)
Clean RPG standards (Minish Cap / Pokemon / Eastward style)
"""
import sys, os
from PIL import Image

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

W, H = 24, 24
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

_  = (0, 0, 0, 0)
OL = (25, 20, 30, 255)       # Soft dark contour (never pure black)
SH = (15, 12, 22, 70)        # Ground shadow

# Hair (Warm Golden Brown / Chestnut with rich 4-tone ramp)
H0 = (45, 24, 16, 255)       # Deepest shadow
H1 = (85, 45, 24, 255)       # Shadow
H2 = (145, 82, 40, 255)      # Base mid
H3 = (195, 122, 60, 255)     # Highlight
H4 = (235, 165, 95, 255)     # Bright glint

# Skin (Soft Peach / Warm anime RPG)
S0 = (165, 95, 75, 255)      # Skin shadow
S1 = (215, 145, 115, 255)    # Skin mid-shadow
S2 = (245, 190, 160, 255)    # Skin base
S3 = (255, 220, 200, 255)    # Skin highlight
BL = (230, 130, 130, 255)    # Subtle blush
EYE = (35, 25, 40, 255)      # Deep iris
GLINT = (255, 255, 255, 255) # Eye catchlight

# Tunic (Teal / Forest Emerald)
T0 = (16, 42, 34, 255)       # Deep seam
T1 = (28, 74, 58, 255)       # Shadow
T2 = (42, 118, 90, 255)      # Base
T3 = (65, 165, 125, 255)     # Highlight
T4 = (110, 215, 170, 255)    # Rim light
WHT = (240, 245, 245, 255)   # White collar

# Belt & Boots (Rich Tan Leather)
L0 = (42, 22, 14, 255)       # Leather dark
L1 = (78, 44, 26, 255)       # Leather base
L2 = (125, 75, 45, 255)      # Leather highlight
GLD = (245, 190, 50, 255)    # Buckle gold

# Pants (Charcoal Blue)
P0 = (24, 28, 38, 255)
P1 = (42, 48, 65, 255)
P2 = (68, 76, 100, 255)

# =============================================================
# 1. DOWN (FRENTE) - IDLE & WALK
# =============================================================
# Head is centered: x from 6 to 17 (12 px wide)
# Y=2 to 11 (Head), Y=12 to 16 (Torso), Y=17 to 21 (Legs/Boots)
def get_down_frame(walk_step=0):
    # walk_step: 0=Idle, 1=Left foot forward, 2=Idle, 3=Right foot forward
    bob = -1 if walk_step in (1, 3) else 0
    m = [[_]*W for _ in range(H)]
    
    # Ground shadow (always on ground)
    for sx in range(6, 18):
        m[22][sx] = SH
        if 8 <= sx <= 15:
            m[23][sx] = SH

    # Legs & Boots (Y = 17 to 21 + bob)
    # Left foot: x=7..9, Right foot: x=14..16
    ly = 17 + bob
    # Pants
    for px in range(8, 11): m[ly][px] = P1
    for px in range(13, 16): m[ly][px] = P1
    m[ly][7] = OL; m[ly][11] = OL; m[ly][12] = OL; m[ly][16] = OL

    # Boots depending on walk
    if walk_step == 0 or walk_step == 2:
        # Neutral stance
        for bx in (7, 8, 9):
            m[ly+1][bx] = L1; m[ly+2][bx] = L0; m[ly+3][bx] = L0
        for bx in (14, 15, 16):
            m[ly+1][bx] = L1; m[ly+2][bx] = L0; m[ly+3][bx] = L0
        m[ly+1][8] = L2; m[ly+1][15] = L2 # boot shine
        # Outline
        m[ly+3][6]=OL; m[ly+3][10]=OL; m[ly+3][13]=OL; m[ly+3][17]=OL
        m[ly+4][7]=OL; m[ly+4][8]=OL; m[ly+4][9]=OL
        m[ly+4][14]=OL; m[ly+4][15]=OL; m[ly+4][16]=OL
    elif walk_step == 1:
        # Left foot forward (lower/bigger), Right foot back
        for bx in (7, 8, 9):
            m[ly+2][bx] = L1; m[ly+3][bx] = L1; m[ly+4][bx] = L0
        m[ly+2][8] = L2
        m[ly+5][7]=OL; m[ly+5][8]=OL; m[ly+5][9]=OL
        # Right foot back (higher)
        for bx in (14, 15, 16):
            m[ly+1][bx] = L1; m[ly+2][bx] = L0
        m[ly+3][14]=OL; m[ly+3][15]=OL; m[ly+3][16]=OL
    elif walk_step == 3:
        # Right foot forward, Left foot back
        for bx in (7, 8, 9):
            m[ly+1][bx] = L1; m[ly+2][bx] = L0
        m[ly+3][7]=OL; m[ly+3][8]=OL; m[ly+3][9]=OL
        # Right foot forward
        for bx in (14, 15, 16):
            m[ly+2][bx] = L1; m[ly+3][bx] = L1; m[ly+4][bx] = L0
        m[ly+2][15] = L2
        m[ly+5][14]=OL; m[ly+5][15]=OL; m[ly+5][16]=OL

    # Torso (Y = 12 to 16 + bob)
    ty = 12 + bob
    # Collar
    m[ty][11] = WHT; m[ty][12] = WHT
    m[ty][10] = OL; m[ty][13] = OL
    # Tunic body
    for y in range(ty+1, ty+4):
        for x in range(8, 16):
            m[y][x] = T2
        m[y][7] = OL; m[y][16] = OL
    # Tunic shading
    m[ty+1][8] = T3; m[ty+2][8] = T3; m[ty+1][9] = T3 # highlight left
    m[ty+2][14] = T1; m[ty+2][15] = T1 # shadow right
    # Belt (ty+3)
    for x in range(8, 16): m[ty+3][x] = L1
    m[ty+3][11] = GLD; m[ty+3][12] = GLD # gold buckle
    # Hands/Arms
    arm_l_y = ty + (2 if walk_step == 1 else (0 if walk_step == 3 else 1))
    arm_r_y = ty + (0 if walk_step == 1 else (2 if walk_step == 3 else 1))
    # Left hand
    m[arm_l_y][5] = OL; m[arm_l_y][6] = T1
    m[arm_l_y+1][5] = OL; m[arm_l_y+1][6] = S2; m[arm_l_y+1][7] = OL
    m[arm_l_y+2][6] = OL
    # Right hand
    m[arm_r_y][18] = OL; m[arm_r_y][17] = T1
    m[arm_r_y+1][18] = OL; m[arm_r_y+1][17] = S2; m[arm_r_y+1][16] = OL
    m[arm_r_y+2][17] = OL

    # Head & Hair (Y = 2 to 11 + bob)
    hy = 2 + bob
    # Hair Top Outline
    for x in range(9, 15): m[hy][x] = OL
    m[hy+1][7] = OL; m[hy+1][8] = OL; m[hy+1][15] = OL; m[hy+1][16] = OL
    m[hy+2][6] = OL; m[hy+2][17] = OL
    # Hair volume fill
    for y in range(hy+1, hy+5):
        for x in range(8, 16):
            m[y][x] = H2
    # Hair highlights (top-left glints)
    m[hy+1][10] = H4; m[hy+1][11] = H4; m[hy+2][9] = H3; m[hy+2][10] = H3
    m[hy+2][14] = H1; m[hy+3][15] = H0 # hair shadows
    
    # Face skin area (hy+5 to hy+10)
    for y in range(hy+5, hy+10):
        for x in range(7, 17):
            m[y][x] = S2
        m[y][6] = OL; m[y][17] = OL
    # Chin curve
    m[hy+10][6] = _; m[hy+10][7] = OL
    for x in range(8, 16): m[hy+10][x] = S1
    m[hy+10][16] = OL; m[hy+10][17] = _
    m[hy+11][9] = OL; m[hy+11][10] = OL; m[hy+11][13] = OL; m[hy+11][14] = OL
    m[hy+11][11] = S0; m[hy+11][12] = S0 # neck shadow

    # Hair bangs framing forehead
    m[hy+4][7] = H2; m[hy+4][8] = H2; m[hy+4][11] = H3; m[hy+4][12] = H2; m[hy+4][15] = H1; m[hy+4][16] = H1
    m[hy+5][7] = H1; m[hy+5][8] = H2; m[hy+5][12] = H1; m[hy+5][15] = H0
    m[hy+6][6] = OL; m[hy+6][7] = H1; m[hy+6][16] = H0; m[hy+6][17] = OL # sideburns
    m[hy+7][6] = OL; m[hy+7][17] = OL

    # Eyes (Cute expressive RPG eyes at hy+7, hy+8)
    # Left eye: x=9, Right eye: x=14
    m[hy+7][9] = EYE; m[hy+8][9] = EYE
    m[hy+7][10] = EYE; m[hy+8][10] = EYE
    m[hy+7][9] = GLINT # Catchlight

    m[hy+7][13] = EYE; m[hy+8][13] = EYE
    m[hy+7][14] = EYE; m[hy+8][14] = EYE
    m[hy+7][13] = GLINT # Catchlight

    # Cheeks / Blush
    m[hy+9][8] = BL; m[hy+9][15] = BL
    return m

# =============================================================
# 2. UP (ESPALDA) - IDLE & WALK
# =============================================================
def get_up_frame(walk_step=0):
    bob = -1 if walk_step in (1, 3) else 0
    m = [[_]*W for _ in range(H)]
    
    # Shadow
    for sx in range(6, 18):
        m[22][sx] = SH
        if 8 <= sx <= 15: m[23][sx] = SH

    # Legs & Boots
    ly = 17 + bob
    for px in range(8, 11): m[ly][px] = P1
    for px in range(13, 16): m[ly][px] = P1
    m[ly][7] = OL; m[ly][11] = OL; m[ly][12] = OL; m[ly][16] = OL

    if walk_step in (0, 2):
        for bx in (7, 8, 9):
            m[ly+1][bx] = L0; m[ly+2][bx] = L0; m[ly+3][bx] = L0
        for bx in (14, 15, 16):
            m[ly+1][bx] = L0; m[ly+2][bx] = L0; m[ly+3][bx] = L0
        m[ly+4][7]=OL; m[ly+4][8]=OL; m[ly+4][9]=OL
        m[ly+4][14]=OL; m[ly+4][15]=OL; m[ly+4][16]=OL
    elif walk_step == 1:
        # Left foot steps up (sole visible)
        for bx in (7, 8, 9):
            m[ly+1][bx] = L1; m[ly+2][bx] = L0
        m[ly+3][7]=OL; m[ly+3][8]=OL; m[ly+3][9]=OL
        # Right foot grounded
        for bx in (14, 15, 16):
            m[ly+2][bx] = L0; m[ly+3][bx] = L0
        m[ly+4][14]=OL; m[ly+4][15]=OL; m[ly+4][16]=OL
    elif walk_step == 3:
        for bx in (7, 8, 9):
            m[ly+2][bx] = L0; m[ly+3][bx] = L0
        m[ly+4][7]=OL; m[ly+4][8]=OL; m[ly+4][9]=OL
        for bx in (14, 15, 16):
            m[ly+1][bx] = L1; m[ly+2][bx] = L0
        m[ly+3][14]=OL; m[ly+3][15]=OL; m[ly+3][16]=OL

    # Torso (Back with adventurer backpack)
    ty = 12 + bob
    # Tunic back
    for y in range(ty, ty+4):
        for x in range(8, 16): m[y][x] = T1
        m[y][7] = OL; m[y][16] = OL
    
    # Leather Backpack on back (x=9..14, y=ty+1..ty+3)
    for by in range(ty, ty+4):
        for bx in range(9, 15):
            m[by][bx] = L1
    m[ty][10] = L2; m[ty][11] = L2; m[ty][12] = L2 # top flap highlight
    m[ty+1][11] = GLD; m[ty+1][12] = GLD # backpack buckle
    m[ty+3][9] = L0; m[ty+3][14] = L0 # side straps

    # Arms
    arm_l_y = ty + (2 if walk_step == 1 else (0 if walk_step == 3 else 1))
    arm_r_y = ty + (0 if walk_step == 1 else (2 if walk_step == 3 else 1))
    m[arm_l_y][6] = T1; m[arm_l_y+1][6] = T0; m[arm_l_y][5] = OL; m[arm_l_y+1][5] = OL
    m[arm_r_y][17] = T1; m[arm_r_y+1][17] = T0; m[arm_r_y][18] = OL; m[arm_r_y+1][18] = OL

    # Head (Full Back of Hair with layered volume)
    hy = 2 + bob
    for x in range(9, 15): m[hy][x] = OL
    m[hy+1][7] = OL; m[hy+1][8] = OL; m[hy+1][15] = OL; m[hy+1][16] = OL
    for y in range(hy+1, hy+10):
        for x in range(7, 17):
            m[y][x] = H2
        m[y][6] = OL; m[y][17] = OL
    # Hair back shading & highlights
    m[hy+2][10] = H3; m[hy+2][11] = H4; m[hy+2][12] = H3
    for y in range(hy+6, hy+10):
        for x in range(13, 17): m[y][x] = H1
        m[y][16] = H0
    # Bottom hair curl/edge
    m[hy+10][7] = OL; m[hy+10][16] = OL
    for x in range(8, 16): m[hy+10][x] = H0
    m[hy+11][9] = OL; m[hy+11][10] = OL; m[hy+11][13] = OL; m[hy+11][14] = OL
    return m

# =============================================================
# 3. RIGHT (PERFIL DERECHA) - IDLE & WALK
# =============================================================
# Head is centered: x from 8 to 17
# NO giant protruding nose! Just clean anime chibi profile.
def get_right_frame(walk_step=0):
    bob = -1 if walk_step in (1, 3) else 0
    m = [[_]*W for _ in range(H)]
    
    # Shadow
    for sx in range(7, 18):
        m[22][sx] = SH
        if 9 <= sx <= 16: m[23][sx] = SH

    # Legs / Boots
    ly = 17 + bob
    # Pants
    for px in range(10, 14): m[ly][px] = P1
    m[ly][9] = OL; m[ly][14] = OL

    if walk_step in (0, 2):
        # Neutral side stance: front boot & back boot slightly overlapping
        for bx in range(10, 15): m[ly+1][bx] = L1; m[ly+2][bx] = L0; m[ly+3][bx] = L0
        m[ly+1][12] = L2
        m[ly+3][15] = L0 # toe tip
        m[ly+4][10]=OL; m[ly+4][11]=OL; m[ly+4][12]=OL; m[ly+4][13]=OL; m[ly+4][14]=OL; m[ly+4][15]=OL
        m[ly+1][9]=OL; m[ly+2][9]=OL; m[ly+3][9]=OL
    elif walk_step == 1:
        # Right leg strides forward
        for bx in range(12, 17): m[ly+2][bx] = L1; m[ly+3][bx] = L0
        m[ly+2][14] = L2
        m[ly+4][12]=OL; m[ly+4][13]=OL; m[ly+4][14]=OL; m[ly+4][15]=OL; m[ly+4][16]=OL
        # Left leg back
        for bx in range(8, 12): m[ly+1][bx] = L0; m[ly+2][bx] = L0
        m[ly+3][8]=OL; m[ly+3][9]=OL; m[ly+3][10]=OL; m[ly+3][11]=OL
    elif walk_step == 3:
        # Left leg strides forward (shaded behind)
        for bx in range(12, 16): m[ly+1][bx] = L0; m[ly+2][bx] = L0
        m[ly+3][12]=OL; m[ly+3][13]=OL; m[ly+3][14]=OL; m[ly+3][15]=OL
        # Right leg pushes back
        for bx in range(8, 12): m[ly+2][bx] = L1; m[ly+3][bx] = L0
        m[ly+4][8]=OL; m[ly+4][9]=OL; m[ly+4][10]=OL; m[ly+4][11]=OL

    # Torso (Side profile with arm swing & side backpack)
    ty = 12 + bob
    # Backpack on back (x=7..9)
    for by in range(ty, ty+4):
        m[by][7] = OL; m[by][8] = L1; m[by][9] = L1
    m[ty][8] = L2 # top highlight
    
    # Tunic center
    for y in range(ty, ty+4):
        for x in range(10, 15): m[y][x] = T2
        m[y][15] = OL
    m[ty][14] = WHT # collar
    m[ty+3][11] = L1; m[ty+3][12] = GLD; m[ty+3][13] = L1 # belt

    # Arm (swings with walk)
    arm_x = 11 + (2 if walk_step == 1 else (-1 if walk_step == 3 else 0))
    m[ty+1][arm_x] = T3; m[ty+2][arm_x] = T2
    m[ty+2][arm_x] = S2; m[ty+3][arm_x] = S2 # hand
    m[ty+1][arm_x-1] = OL; m[ty+2][arm_x-1] = OL; m[ty+3][arm_x-1] = OL
    m[ty+1][arm_x+1] = OL; m[ty+2][arm_x+1] = OL; m[ty+3][arm_x+1] = OL
    m[ty+4][arm_x] = OL

    # Head (Y = 2 to 11 + bob)
    hy = 2 + bob
    # Hair Dome
    for x in range(9, 15): m[hy][x] = OL
    m[hy+1][8] = OL; m[hy+1][15] = OL
    for y in range(hy+1, hy+5):
        for x in range(8, 15): m[y][x] = H2
        m[y][7] = OL
    m[hy+1][11] = H4; m[hy+2][10] = H3; m[hy+2][11] = H3
    
    # Back of hair curls down to shoulders (x=7..9)
    for y in range(hy+5, hy+9):
        m[y][7] = OL; m[y][8] = H1; m[y][9] = H2
    m[hy+9][7] = OL; m[hy+9][8] = H0; m[hy+10][8] = OL

    # Face profile (x=10..15, y=hy+5..hy+10)
    for y in range(hy+5, hy+10):
        for x in range(10, 16): m[y][x] = S2
    # Forehead bangs
    m[hy+4][12] = H2; m[hy+4][13] = H3; m[hy+4][14] = H2; m[hy+4][15] = OL
    m[hy+5][13] = H2; m[hy+5][14] = H1

    # Clean profile line (Y=6..10)
    # Eye at x=13, y=hy+7 (1x2 pixel vertical RPG eye)
    m[hy+7][13] = EYE; m[hy+8][13] = EYE
    m[hy+7][13] = GLINT
    # Soft cheek / tiny gentle nose contour
    m[hy+6][15] = OL; m[hy+7][15] = OL
    m[hy+8][16] = OL; m[hy+8][15] = S2 # very subtle 1px nose tip
    m[hy+9][15] = OL; m[hy+9][14] = BL  # cheek blush
    m[hy+10][14] = OL; m[hy+10][13] = S1 # chin
    m[hy+11][11] = OL; m[hy+11][12] = S0 # neck
    return m

def mat_to_img(mat):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            im.putpixel((x, y), mat[y][x])
    return im

# Generate 4 walk frames for each direction
down_frames  = [mat_to_img(get_down_frame(i)) for i in range(4)]
up_frames    = [mat_to_img(get_up_frame(i)) for i in range(4)]
right_frames = [mat_to_img(get_right_frame(i)) for i in range(4)]
# Left is clean horizontal flip of Right
left_frames  = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in right_frames]

all_16 = down_frames + up_frames + right_frames + left_frames

# 4x4 Spritesheet
grid_sheet = Image.new('RGBA', (W * 4, H * 4), (0, 0, 0, 0))
dirs = [down_frames, up_frames, right_frames, left_frames]
for row, d_frames in enumerate(dirs):
    for col, f_img in enumerate(d_frames):
        grid_sheet.paste(f_img, (col * W, row * H))

grid_sheet.save(f"{TARGET_DIR}/personaje_walk_grid.png")
grid_prev = grid_sheet.resize((W * 4 * 8, H * 4 * 8), Image.NEAREST)
grid_prev.save(f"{TARGET_DIR}/personaje_walk_preview_8x.png")
grid_prev.save(f"{BRAIN}/personaje_redesign_preview_8x.png")

# Overwrite base direction sprites
down_frames[0].save(f"{TARGET_DIR}/personaje_down.png")
up_frames[0].save(f"{TARGET_DIR}/personaje_up.png")
right_frames[0].save(f"{TARGET_DIR}/personaje_right.png")
left_frames[0].save(f"{TARGET_DIR}/personaje_left.png")

# Horizontal 4-dir strip
strip_4dir = Image.new('RGBA', (W * 4, H), (0, 0, 0, 0))
for i, f in enumerate([down_frames[0], up_frames[0], right_frames[0], left_frames[0]]):
    strip_4dir.paste(f, (i * W, 0))
strip_4dir.save(f"{TARGET_DIR}/personaje_spritesheet.png")

# Update ASE with tags
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

# Animated Combo GIF (6x upscale)
combo = []
for i in range(4):
    c_img = Image.new('RGBA', (W * 2, H * 2), (240, 242, 245, 255))
    c_img.paste(down_frames[i], (0, 0), down_frames[i])
    c_img.paste(up_frames[i], (W, 0), up_frames[i])
    c_img.paste(right_frames[i], (0, H), right_frames[i])
    c_img.paste(left_frames[i], (W, H), left_frames[i])
    c_up = c_img.resize((W * 2 * 6, H * 2 * 6), Image.NEAREST)
    combo.append(c_up.convert('RGB').quantize(colors=64, method=2))

combo[0].save(
    f"{TARGET_DIR}/walk_all_demo.gif",
    save_all=True, append_images=combo[1:],
    loop=0, duration=140, optimize=False
)
combo[0].save(
    f"{BRAIN}/walk_redesign_demo.gif",
    save_all=True, append_images=combo[1:],
    loop=0, duration=140, optimize=False
)

print("✓ Rediseño profesional completado.")

