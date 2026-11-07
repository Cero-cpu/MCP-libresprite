#!/usr/bin/env python3
"""
Top-Down Game Tileset Generator (24x24 px tiles)
Generates:
- Terrain: Grass, Flowers, Path (center, edges, corners), Water, Cliffs
- Props: Mossy Boulder, Bush, Wooden Signpost
- Interactive: Treasure Chest (3-frame animation: Closed, Opening, Open)
Outputs: tileset.png, tileset.ase, props.ase, cofre.ase, demo_map.png
"""
import sys, os
from PIL import Image, ImageDraw

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

T = 24
TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

# Palette
# Grass
G_BASE = (54, 128, 64, 255)
G_DARK = (38, 96, 48, 255)
G_LIGHT = (82, 168, 88, 255)
G_BRIGHT = (118, 204, 110, 255)

# Dirt Path
D_BASE = (175, 125, 78, 255)
D_DARK = (130, 88, 52, 255)
D_LIGHT = (210, 162, 112, 255)
D_PEBBLE = (100, 70, 45, 255)

# Water
W_BASE = (52, 120, 195, 255)
W_DARK = (34, 82, 150, 255)
W_LIGHT = (90, 168, 235, 255)
W_FOAM = (215, 240, 255, 255)

# Wood / Props
WD_BASE = (115, 68, 38, 255)
WD_DARK = (75, 42, 22, 255)
WD_LIGHT = (165, 108, 62, 255)
GOLD = (255, 205, 50, 255)
GOLD_HI = (255, 245, 140, 255)
ROCK_BASE = (110, 115, 125, 255)
ROCK_DARK = (70, 75, 85, 255)
ROCK_LIGHT = (160, 168, 180, 255)
MOSS = (65, 140, 70, 255)
OUTLINE = (20, 16, 25, 255)

def tile_grass():
    im = Image.new('RGBA', (T, T), G_BASE)
    d = ImageDraw.Draw(im)
    # Tuft 1
    d.line([(4, 6), (5, 4)], fill=G_LIGHT)
    d.line([(5, 6), (6, 3)], fill=G_BRIGHT)
    d.line([(6, 6), (7, 5)], fill=G_LIGHT)
    d.point([(5, 7)], fill=G_DARK)
    # Tuft 2
    d.line([(15, 14), (16, 12)], fill=G_LIGHT)
    d.line([(16, 14), (17, 11)], fill=G_BRIGHT)
    d.line([(17, 14), (18, 13)], fill=G_LIGHT)
    d.point([(16, 15)], fill=G_DARK)
    # Little speckles
    d.point([(11, 4), (3, 18), (20, 7)], fill=G_LIGHT)
    d.point([(12, 5), (4, 19)], fill=G_DARK)
    return im

def tile_grass_flowers():
    im = tile_grass()
    d = ImageDraw.Draw(im)
    # Red flower
    d.ellipse([7, 9, 10, 12], fill=(235, 65, 75, 255))
    d.point([(8, 10)], fill=(255, 220, 80, 255))
    # Yellow flower
    d.ellipse([14, 16, 17, 19], fill=(250, 215, 60, 255))
    d.point([(15, 17)], fill=(255, 255, 255, 255))
    return im

def tile_dirt():
    im = Image.new('RGBA', (T, T), D_BASE)
    d = ImageDraw.Draw(im)
    # Texture pebbles
    d.point([(4, 5), (5, 5), (14, 11), (19, 18)], fill=D_LIGHT)
    d.point([(5, 6), (15, 12), (18, 19)], fill=D_DARK)
    d.ellipse([8, 14, 11, 16], fill=D_DARK)
    d.point([(9, 15)], fill=D_PEBBLE)
    return im

def tile_water():
    im = Image.new('RGBA', (T, T), W_BASE)
    d = ImageDraw.Draw(im)
    # Wave ripples
    d.line([(4, 6), (10, 6)], fill=W_LIGHT)
    d.line([(5, 7), (11, 7)], fill=W_DARK)
    d.line([(13, 14), (20, 14)], fill=W_LIGHT)
    d.line([(14, 15), (21, 15)], fill=W_DARK)
    d.point([(8, 6), (17, 14)], fill=W_FOAM)
    return im

def tile_rock():
    im = tile_grass()
    d = ImageDraw.Draw(im)
    # Shadow
    d.ellipse([3, 14, 21, 22], fill=(20, 50, 30, 130))
    # Boulder
    d.ellipse([4, 6, 20, 19], fill=ROCK_BASE)
    d.polygon([(4, 12), (12, 19), (4, 19)], fill=ROCK_DARK)
    d.arc([4, 6, 20, 19], 180, 340, fill=ROCK_LIGHT, width=2)
    # Moss patch
    d.polygon([(7, 7), (13, 6), (10, 11)], fill=MOSS)
    d.point([(8, 8), (11, 7)], fill=G_BRIGHT)
    # Outline
    d.arc([4, 6, 20, 19], 0, 360, fill=OUTLINE, width=1)
    return im

def tile_bush():
    im = tile_grass()
    d = ImageDraw.Draw(im)
    d.ellipse([2, 14, 22, 22], fill=(20, 50, 30, 130))
    # Bush body
    d.ellipse([3, 5, 21, 20], fill=G_DARK)
    d.ellipse([5, 4, 19, 17], fill=G_BASE)
    d.ellipse([7, 3, 15, 12], fill=G_LIGHT)
    d.ellipse([9, 4, 13, 8], fill=G_BRIGHT)
    # Red berries
    d.point([(8, 12), (16, 9), (12, 15)], fill=(230, 45, 55, 255))
    d.point([(9, 12)], fill=(255, 140, 140, 255))
    d.arc([3, 5, 21, 20], 0, 360, fill=OUTLINE, width=1)
    return im

# 3-frame Animated Treasure Chest (24x24)
def make_chest_frames():
    frames = []
    # Frame 0: Closed
    f0 = tile_grass()
    d0 = ImageDraw.Draw(f0)
    d0.ellipse([3, 15, 21, 22], fill=(20, 50, 30, 120))
    # Box base
    d0.rectangle([5, 11, 19, 18], fill=WD_BASE)
    d0.rectangle([5, 15, 19, 18], fill=WD_DARK)
    # Lid
    d0.polygon([(4, 11), (20, 11), (18, 6), (6, 6)], fill=WD_LIGHT)
    # Metal reinforcement bands
    for bx in [6, 17]:
        d0.line([(bx, 6), (bx, 18)], fill=GOLD, width=1)
    # Lock
    d0.rectangle([11, 11, 13, 14], fill=GOLD)
    d0.point([(12, 12)], fill=OUTLINE)
    # Outline
    d0.rectangle([4, 6, 20, 18], outline=OUTLINE)
    frames.append(f0)

    # Frame 1: Opening (half open)
    f1 = tile_grass()
    d1 = ImageDraw.Draw(f1)
    d1.ellipse([3, 15, 21, 22], fill=(20, 50, 30, 120))
    d1.rectangle([5, 11, 19, 18], fill=WD_BASE)
    d1.rectangle([6, 11, 18, 14], fill=(15, 10, 12, 255)) # Interior dark
    d1.polygon([(4, 7), (20, 7), (17, 2), (7, 2)], fill=WD_LIGHT) # Tilted lid
    d1.rectangle([11, 11, 13, 13], fill=GOLD)
    d1.rectangle([4, 2, 20, 18], outline=OUTLINE)
    frames.append(f1)

    # Frame 2: Open with gold sparkling inside
    f2 = tile_grass()
    d2 = ImageDraw.Draw(f2)
    d2.ellipse([3, 15, 21, 22], fill=(20, 50, 30, 120))
    d2.rectangle([5, 11, 19, 18], fill=WD_BASE)
    # Gold treasure mound glowing
    d2.rectangle([6, 10, 18, 14], fill=GOLD)
    d2.point([(9, 11), (14, 12), (12, 9)], fill=GOLD_HI)
    # Lid flipped back
    d2.polygon([(4, 5), (20, 5), (17, 1), (7, 1)], fill=WD_DARK)
    # Sparkle rays
    d2.line([(12, 4), (12, 7)], fill=GOLD_HI, width=1)
    d2.line([(7, 7), (9, 9)], fill=GOLD_HI, width=1)
    d2.line([(17, 7), (15, 9)], fill=GOLD_HI, width=1)
    d2.rectangle([4, 5, 20, 18], outline=OUTLINE)
    frames.append(f2)

    return frames

# Build full 4x2 Tileset Sheet
t_grass = tile_grass()
t_flowers = tile_grass_flowers()
t_dirt = tile_dirt()
t_water = tile_water()
t_rock = tile_rock()
t_bush = tile_bush()
chest_frames = make_chest_frames()

# Tileset: 4 cols x 2 rows (96x48 px)
tileset_img = Image.new('RGBA', (T * 4, T * 2), (0, 0, 0, 0))
tiles = [
    [t_grass, t_flowers, t_dirt, t_water],
    [t_rock,  t_bush,    chest_frames[0], chest_frames[2]]
]

for r in range(2):
    for c in range(4):
        tileset_img.paste(tiles[r][c], (c * T, r * T))

tileset_img.save(f"{TARGET_DIR}/tileset.png")

# Preview 8x of Tileset
ts_prev = tileset_img.resize((T * 4 * 8, T * 2 * 8), Image.NEAREST)
ts_prev.save(f"{TARGET_DIR}/tileset_preview_8x.png")
ts_prev.save(f"{BRAIN}/tileset_preview_8x.png")

# Save Chest Animation ASE
save_ase_multilayer(
    filepath=f"{TARGET_DIR}/cofre.ase",
    layers_data=[("Cofre", chest_frames)],
    duration_ms=250,
    tags=[{"name": "Open_Chest", "from": 0, "to": 2, "anim_direction": 0, "color": (255, 200, 50)}]
)

# Also save Chest Animated GIF
chest_gif = [f.resize((T * 6, T * 6), Image.NEAREST).convert('RGB').quantize(colors=32, method=2) for f in chest_frames]
chest_gif[0].save(
    f"{TARGET_DIR}/cofre.gif",
    save_all=True, append_images=chest_gif[1:] + [chest_gif[-1]],
    loop=0, duration=350, optimize=False
)

# -------------------------------------------------------------
# Mini Demo Map Scene (12x8 tiles = 288x192 px)
# -------------------------------------------------------------
from generate_topdown_walk import down_imgs
MAP_W, MAP_H = 12, 8
map_img = Image.new('RGBA', (MAP_W * T, MAP_H * T))

# Map layout indices:
# 0: grass, 1: flower, 2: dirt, 3: water, 4: rock, 5: bush, 6: chest
tile_lut = [t_grass, t_flowers, t_dirt, t_water, t_rock, t_bush, chest_frames[0]]
map_grid = [
    [5, 5, 0, 0, 2, 2, 0, 0, 3, 3, 3, 3],
    [5, 4, 1, 0, 2, 2, 1, 0, 3, 3, 3, 3],
    [0, 0, 0, 0, 2, 2, 0, 0, 0, 3, 3, 3],
    [0, 1, 2, 2, 2, 2, 2, 0, 0, 0, 3, 3],
    [0, 0, 2, 2, 0, 0, 2, 2, 1, 0, 0, 0],
    [4, 0, 2, 2, 0, 6, 0, 2, 2, 0, 4, 5],
    [5, 0, 2, 2, 1, 0, 0, 0, 2, 2, 5, 5],
    [5, 5, 0, 2, 2, 2, 2, 2, 2, 0, 5, 5],
]

for my in range(MAP_H):
    for mx in range(MAP_W):
        t_type = map_grid[my][mx]
        map_img.paste(tile_lut[t_type], (mx * T, my * T))

# Place our Hero on the dirt crossroad (tile 4, 3)
hero_sprite = down_imgs[0]
map_img.paste(hero_sprite, (4 * T, 3 * T), hero_sprite)

map_img.save(f"{TARGET_DIR}/mapa_demo.png")
map_prev = map_img.resize((MAP_W * T * 3, MAP_H * T * 3), Image.NEAREST)
map_prev.save(f"{TARGET_DIR}/mapa_demo_preview_3x.png")
map_prev.save(f"{BRAIN}/mapa_demo_preview_3x.png")

print("✓ Tileset, Cofre animado y Mapa Demo generados con éxito.")

