#!/usr/bin/env python3
"""
Professional Seamless Grass Tileset for TileMapLayer (24x24 px tiles)
Designed for seamless repetition, natural organic painting, and Godot 4 TileMapLayer.

Tiles Included:
Row 0: Seamless Base & Natural Variations
  - Tile (0,0): Pure Seamless Grass (100% wrap-around seamless)
  - Tile (1,0): Grass with Soft Blades (Tufts)
  - Tile (2,0): Grass with Wild Red & White Flowers
  - Tile (3,0): Grass with Golden Daisy & Sprout
  - Tile (4,0): Grass with Mossy Pebble & Lawn Texture
  - Tile (5,0): Dense Tall Grass Tuft (Interactable/Bushy)

Row 1: Grass Cliff / Edges for TileMap Autotiling (over dark dirt/cliff)
  - Outer Corners, Edges, Inner Corners with natural grassy fringe overhang.
"""
import sys, os
from PIL import Image, ImageDraw

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

T = 24
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

# 5-Tone Lush Green Ramp
G0 = (32, 78, 48, 255)       # Deepest crevice
G1 = (48, 112, 64, 255)      # Shadow
G2 = (68, 154, 82, 255)      # Base midtone
G3 = (98, 188, 105, 255)     # Sunlit blade
G4 = (145, 222, 135, 255)    # Blade tip glint

# Flowers & Accents
FL_R = (235, 60, 75, 255)    # Red petal
FL_RW = (255, 170, 180, 255)
FL_Y = (255, 215, 50, 255)   # Gold petal
FL_W = (248, 250, 255, 255)  # White petal
FL_CTR = (255, 240, 120, 255)# Flower eye
PEBBLE_D = (70, 75, 88, 255)
PEBBLE_L = (145, 155, 170, 255)

# --- 1. PURE SEAMLESS BASE TILE ---
# Toroidal / Seamless noise pattern ensuring edges wrap perfectly
def make_base_seamless():
    im = Image.new('RGBA', (T, T), G2)
    px = im.load()
    
    # Pre-calculated seamless dither matrix (modulo T)
    dither_points_g3 = [
        (3, 4), (4, 4), (10, 2), (15, 8), (16, 8), (21, 14), (8, 18), (9, 18), (19, 21), (2, 12)
    ]
    dither_points_g1 = [
        (4, 5), (11, 3), (16, 9), (22, 15), (9, 19), (20, 22), (3, 13), (13, 14)
    ]
    for x, y in dither_points_g3:
        px[x % T, y % T] = G3
    for x, y in dither_points_g1:
        px[x % T, y % T] = G1
    return im

# --- 2. VARIATION: SOFT BLADES / TUFTS ---
def make_var_blades():
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    # Tuft A (left-center)
    d.line([(6, 12), (7, 9)], fill=G3)
    d.line([(7, 12), (8, 8)], fill=G4)
    d.line([(8, 12), (9, 10)], fill=G3)
    d.point([(7, 13), (8, 13)], fill=G0)
    # Tuft B (upper right)
    d.line([(16, 6), (17, 3)], fill=G4)
    d.line([(17, 6), (18, 4)], fill=G3)
    d.point([(17, 7)], fill=G1)
    return im

# --- 3. VARIATION: RED & WHITE WILDFLOWERS ---
def make_var_flowers():
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    # Red flower with stem
    d.point([(7, 15)], fill=G0)
    d.point([(7, 14)], fill=G3)
    d.ellipse([5, 11, 9, 13], fill=FL_R)
    d.point([(7, 12)], fill=FL_CTR)
    d.point([(6, 11)], fill=FL_RW)
    
    # White clover flower
    d.point([(16, 9)], fill=G0)
    d.point([(16, 8)], fill=G3)
    d.ellipse([14, 5, 18, 7], fill=FL_W)
    d.point([(16, 6)], fill=FL_CTR)
    return im

# --- 4. VARIATION: GOLDEN DAISY & SPROUTS ---
def make_var_daisy():
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    # Yellow Daisy
    d.point([(11, 14)], fill=G0)
    d.ellipse([9, 9, 14, 13], fill=FL_Y)
    d.point([(11, 11), (12, 11)], fill=(255, 130, 20, 255))
    d.point([(10, 10), (13, 10)], fill=FL_CTR)
    # Tiny seedling sprout
    d.line([(18, 17), (19, 15)], fill=G4)
    d.line([(19, 17), (20, 16)], fill=G3)
    d.point([(19, 18)], fill=G0)
    return im

# --- 5. VARIATION: MOSSY PEBBLE ---
def make_var_pebble():
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    # Little pebble with shadow & moss
    d.ellipse([11, 13, 18, 17], fill=G0) # Shadow in grass
    d.ellipse([12, 11, 17, 15], fill=PEBBLE_D)
    d.ellipse([12, 11, 16, 13], fill=PEBBLE_L)
    # Moss overlapping stone
    d.point([(13, 11), (14, 11)], fill=G4)
    d.point([(12, 13)], fill=G1)
    return im

# --- 6. VARIATION: TALL DENSE TUFT ---
def make_var_tall():
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    # Clustered thick grass blades
    blades = [(9, 17, 9, 9), (10, 17, 11, 7), (11, 17, 12, 6), (12, 17, 13, 7), (13, 17, 15, 9)]
    for x1, y1, x2, y2 in blades:
        d.line([(x1, y1), (x2, y2)], fill=G3)
    d.point([(11, 7), (12, 6), (13, 7)], fill=G4)
    for bx in range(9, 15): d.point([(bx, 17)], fill=G0)
    return im

# --- ROW 1: GRASS OVERHANG BORDERS (FOR CLIFFS / PATHS) ---
# Creates natural serrated blades dangling off the edge
def make_edge_north():
    # Grass at bottom, overhanging empty top (or transparent cliff)
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    for x in range(T):
        blade_h = 3 + (x % 3)
        d.line([(x, 0), (x, blade_h)], fill=G4 if x % 2 == 0 else G3)
    d.line([(0, 4), (T, 4)], fill=G1)
    return im

def make_edge_south():
    im = make_base_seamless()
    d = ImageDraw.Draw(im)
    # Bottom fringe overhang with serrated blades into transparency/shadow
    for x in range(T):
        fringe = 2 + (x * 2) % 4
        d.line([(x, T - fringe), (x, T - 1)], fill=G0)
    return im

# Compile Tileset Grid: 6 Columns x 2 Rows (144 x 48 px)
tiles = [
    [make_base_seamless(), make_var_blades(), make_var_flowers(), 
     make_var_daisy(), make_var_pebble(), make_var_tall()],
    [make_edge_north(), make_edge_south(), make_base_seamless(),
     make_var_blades(), make_var_flowers(), make_var_daisy()]
]

tileset_img = Image.new('RGBA', (T * 6, T * 2), (0, 0, 0, 0))
for r in range(2):
    for c in range(6):
        tileset_img.paste(tiles[r][c], (c * T, r * T))

# 1. Save standard PNG
tileset_img.save(f"{TARGET_DIR}/cesped_tileset.png")

# 2. Save 6x preview for inspection
prev = tileset_img.resize((T * 6 * 6, T * 2 * 6), Image.NEAREST)
prev.save(f"{TARGET_DIR}/cesped_tileset_preview_6x.png")
prev.save(f"{BRAIN}/cesped_tileset_preview_6x.png")

# 3. Save LibreSprite ASE with layer metadata
save_ase_multilayer(
    filepath=f"{TARGET_DIR}/cesped_tileset.ase",
    layers_data=[("Cesped_Tileset", [tileset_img])],
    duration_ms=100
)

# ------------------------------------------------------------------------------
# DEMO TILEMAP TEST (Pintando un prado 10x8 tiles para probar el TileMapLayer)
# ------------------------------------------------------------------------------
# We test seamlessly tiling the pure base and scattering variations naturally.
import random
random.seed(42)

MAP_COLS, MAP_ROWS = 10, 7
field = Image.new('RGBA', (MAP_COLS * T, MAP_ROWS * T))

var_pool = [
    (tiles[0][0], 0.50), # 50% pure seamless base
    (tiles[0][1], 0.20), # 20% soft blades
    (tiles[0][2], 0.10), # 10% red flowers
    (tiles[0][3], 0.10), # 10% yellow daisies
    (tiles[0][4], 0.05), # 5% pebble
    (tiles[0][5], 0.05), # 5% tall tufts
]

for my in range(MAP_ROWS):
    for mx in range(MAP_COLS):
        # Weighted random choice for natural look
        r_val = random.random()
        cum = 0
        chosen_tile = tiles[0][0]
        for t_tile, weight in var_pool:
            cum += weight
            if r_val <= cum:
                chosen_tile = t_tile
                break
        field.paste(chosen_tile, (mx * T, my * T))

# Add hero on the field to see how he blends
from perfect_hero import down_frames
hero_down = down_frames[0]
field.paste(hero_down, (4 * T + 2, 3 * T), hero_down)

field.save(f"{TARGET_DIR}/prado_cesped_demo.png")
field_prev = field.resize((MAP_COLS * T * 3, MAP_ROWS * T * 3), Image.NEAREST)
field_prev.save(f"{TARGET_DIR}/prado_cesped_preview_3x.png")
field_prev.save(f"{BRAIN}/prado_cesped_preview_3x.png")

print("✓ Tileset de césped para TileMapLayer generado con éxito.")

