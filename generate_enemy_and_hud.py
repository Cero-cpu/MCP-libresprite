#!/usr/bin/env python3
"""
Top-Down Enemy (Bouncing Slime) & HUD Assets Generator
Grid: 24x24 px for Slime (4 frames: Idle, Squash, Jump, Land)
HUD: Hearts (Full, Half, Empty) and Collectibles (Gem, Key)
"""
import sys, os
from PIL import Image, ImageDraw

sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')
from ase_format import save_ase_multilayer

TARGET_DIR = "/home/cachy/Descargas/juego top danw"
BRAIN = "/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0"

_   = (0, 0, 0, 0)
OL  = (18, 22, 40, 255)       # Outline deep navy
SH  = (20, 25, 35, 70)        # Ground shadow

# Slime Palette (Translucent Azure / Cyan Jelly)
SL0 = (20, 60, 110, 255)      # Deep base shadow
SL1 = (35, 110, 180, 255)     # Shadow
SL2 = (55, 175, 235, 255)     # Mid base
SL3 = (110, 225, 255, 255)    # Highlight
SL4 = (215, 250, 255, 255)    # Specular glint
EYE = (15, 20, 35, 255)       # Pupil
GL  = (255, 255, 255, 255)

W, H = 24, 24

# ------------------------------------------------------------------------------
# SLIME ANIMATION (24x24 per frame, 4 frames)
# ------------------------------------------------------------------------------
def make_slime_frames():
    frames = []

    # Frame 0: Normal Idle (W=16, H=12, centered at X=12, Y=14)
    f0 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d0 = ImageDraw.Draw(f0)
    d0.ellipse([4, 18, 20, 22], fill=SH) # Shadow
    d0.ellipse([5, 8, 19, 19], fill=SL2) # Slime body
    d0.ellipse([7, 6, 17, 18], fill=SL2)
    # Shading
    d0.ellipse([5, 13, 19, 19], fill=SL1)
    d0.ellipse([7, 15, 17, 19], fill=SL0)
    # Highlights & Glints
    d0.ellipse([8, 7, 14, 11], fill=SL3)
    d0.point([(9, 8), (10, 8), (9, 9)], fill=SL4)
    # Eyes
    d0.rectangle([8, 11, 9, 13], fill=EYE)
    d0.point([(8, 11)], fill=GL)
    d0.rectangle([14, 11, 15, 13], fill=EYE)
    d0.point([(14, 11)], fill=GL)
    # Cute little blush
    d0.point([(7, 14)], fill=(40, 140, 210, 255))
    d0.point([(16, 14)], fill=(40, 140, 210, 255))
    # Outline
    d0.arc([5, 7, 19, 19], 0, 360, fill=OL, width=1)
    frames.append(f0)

    # Frame 1: Squash (Wider and flatter, preparing to bounce: W=18, H=9)
    f1 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(f1)
    d1.ellipse([3, 18, 21, 23], fill=SH) # Shadow widens
    d1.ellipse([3, 11, 21, 20], fill=SL2) # Flattened body
    d1.ellipse([4, 15, 20, 20], fill=SL1)
    d1.ellipse([6, 16, 18, 20], fill=SL0)
    d1.ellipse([7, 11, 17, 14], fill=SL3)
    d1.point([(8, 12), (9, 12)], fill=SL4)
    # Squashed eyes (horizontal)
    d1.rectangle([7, 14, 9, 15], fill=EYE)
    d1.point([(7, 14)], fill=GL)
    d1.rectangle([14, 14, 16, 15], fill=EYE)
    d1.point([(14, 14)], fill=GL)
    d1.arc([3, 11, 21, 20], 0, 360, fill=OL, width=1)
    frames.append(f1)

    # Frame 2: Jump Stretch (Airborne, elongated: W=12, H=15, Y rises)
    f2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(f2)
    d2.ellipse([7, 19, 17, 22], fill=SH) # Shadow shrinks on ground
    d2.ellipse([6, 3, 18, 16], fill=SL2) # Stretched slime body
    d2.ellipse([7, 11, 17, 16], fill=SL1)
    d2.ellipse([8, 13, 16, 16], fill=SL0)
    d2.ellipse([8, 4, 16, 8], fill=SL3)
    d2.point([(9, 5), (10, 5)], fill=SL4)
    # Excited wide eyes in air
    d2.rectangle([8, 7, 10, 10], fill=EYE)
    d2.point([(8, 7)], fill=GL)
    d2.rectangle([14, 7, 16, 10], fill=EYE)
    d2.point([(14, 7)], fill=GL)
    d2.arc([6, 3, 18, 16], 0, 360, fill=OL, width=1)
    frames.append(f2)

    # Frame 3: Land / Bounce impact (Returning to base shape with ripple)
    f3 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(f3)
    d3.ellipse([4, 18, 20, 22], fill=SH)
    d3.ellipse([4, 9, 20, 19], fill=SL2)
    d3.ellipse([5, 14, 19, 19], fill=SL1)
    d3.ellipse([7, 15, 17, 19], fill=SL0)
    d3.ellipse([7, 8, 15, 12], fill=SL3)
    d3.point([(9, 9), (10, 9)], fill=SL4)
    d3.rectangle([8, 12, 9, 14], fill=EYE)
    d3.point([(8, 12)], fill=GL)
    d3.rectangle([14, 12, 15, 14], fill=EYE)
    d3.point([(14, 12)], fill=GL)
    d3.arc([4, 9, 20, 19], 0, 360, fill=OL, width=1)
    frames.append(f3)

    return frames

slime_frames = make_slime_frames()

# Save Slime Spritesheet (96x24 px)
slime_sheet = Image.new('RGBA', (W * 4, H), (0, 0, 0, 0))
for i, f in enumerate(slime_frames):
    slime_sheet.paste(f, (i * W, 0))
slime_sheet.save(f"{TARGET_DIR}/slime_sheet.png")

# Save Slime GIF (130ms / frame)
slime_gif = [f.resize((W * 6, H * 6), Image.NEAREST).convert('RGB').quantize(colors=32, method=2) for f in slime_frames]
slime_gif[0].save(
    f"{TARGET_DIR}/slime.gif",
    save_all=True, append_images=slime_gif[1:],
    loop=0, duration=130, optimize=False
)
slime_gif[0].save(
    f"{BRAIN}/slime.gif",
    save_all=True, append_images=slime_gif[1:],
    loop=0, duration=130, optimize=False
)

# Save Slime ASE with Tags
save_ase_multilayer(
    filepath=f"{TARGET_DIR}/slime.ase",
    layers_data=[("Slime_Bounce", slime_frames)],
    duration_ms=130,
    tags=[{"name": "Bounce", "from": 0, "to": 3, "anim_direction": 0, "color": (50, 180, 240)}]
)

# ------------------------------------------------------------------------------
# HUD ASSETS (Hearts, Coin, Gem, Key)
# ------------------------------------------------------------------------------
# 16x16 icon format
IC_S = 16

def make_heart(mode="full"):
    im = Image.new('RGBA', (IC_S, IC_S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Heart coordinates (centered in 16x16)
    # Red tones
    R_DARK = (150, 20, 35, 255)
    R_BASE = (225, 40, 55, 255)
    R_LIGHT = (255, 110, 125, 255)
    R_GLINT = (255, 210, 220, 255)
    EMPTY_BG = (45, 30, 40, 200)

    # Base Heart Polygon
    poly = [(8, 14), (2, 7), (2, 4), (5, 2), (8, 4), (11, 2), (14, 4), (14, 7)]
    
    if mode == "empty":
        d.polygon(poly, fill=EMPTY_BG, outline=OL)
    elif mode == "full":
        d.polygon(poly, fill=R_BASE)
        # Shading
        d.polygon([(8, 14), (2, 7), (4, 11), (8, 13)], fill=R_DARK)
        # Highlights
        d.point([(4, 4), (5, 3), (6, 4)], fill=R_LIGHT)
        d.point([(5, 4)], fill=R_GLINT)
        d.polygon(poly, outline=OL)
    elif mode == "half":
        d.polygon(poly, fill=EMPTY_BG)
        # Left half full
        d.polygon([(8, 14), (2, 7), (2, 4), (5, 2), (8, 4), (8, 14)], fill=R_BASE)
        d.polygon([(8, 14), (2, 7), (4, 11), (8, 13)], fill=R_DARK)
        d.point([(5, 4)], fill=R_GLINT)
        d.polygon(poly, outline=OL)
        d.line([(8, 4), (8, 14)], fill=OL)
    return im

def make_coin():
    im = Image.new('RGBA', (IC_S, IC_S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    G_DARK = (180, 120, 20, 255)
    G_MID = (245, 190, 40, 255)
    G_LIGHT = (255, 235, 120, 255)
    d.ellipse([3, 3, 12, 12], fill=G_MID)
    d.arc([3, 3, 12, 12], 90, 270, fill=G_DARK, width=1)
    d.arc([3, 3, 12, 12], 270, 90, fill=G_LIGHT, width=1)
    d.point([(6, 6), (7, 6), (6, 7)], fill=G_LIGHT)
    d.ellipse([3, 3, 12, 12], outline=OL)
    return im

def make_key():
    im = Image.new('RGBA', (IC_S, IC_S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    G_MID = (245, 190, 40, 255)
    G_DARK = (180, 120, 20, 255)
    # Ring
    d.ellipse([3, 3, 9, 9], outline=OL, fill=G_MID)
    d.point([(6, 6)], fill=(0, 0, 0, 0))
    # Shaft & teeth
    d.line([(8, 8), (13, 13)], fill=G_MID, width=2)
    d.point([(11, 13), (13, 11)], fill=G_DARK)
    d.line([(8, 9), (13, 14)], fill=OL, width=1)
    return im

h_full = make_heart("full")
h_half = make_heart("half")
h_empty = make_heart("empty")
coin = make_coin()
key = make_key()

# Save individual HUD icons
h_full.save(f"{TARGET_DIR}/hud_corazon_lleno.png")
h_half.save(f"{TARGET_DIR}/hud_corazon_medio.png")
h_empty.save(f"{TARGET_DIR}/hud_corazon_vacio.png")
coin.save(f"{TARGET_DIR}/hud_moneda.png")
key.save(f"{TARGET_DIR}/hud_llave.png")

# HUD Spritesheet (80x16 px)
hud_sheet = Image.new('RGBA', (IC_S * 5, IC_S), (0, 0, 0, 0))
icons = [h_full, h_half, h_empty, coin, key]
for i, ic in enumerate(icons):
    hud_sheet.paste(ic, (i * IC_S, 0))

hud_sheet.save(f"{TARGET_DIR}/hud_sheet.png")
hud_prev = hud_sheet.resize((IC_S * 5 * 6, IC_S * 6), Image.NEAREST)
hud_prev.save(f"{TARGET_DIR}/hud_preview_6x.png")
hud_prev.save(f"{BRAIN}/hud_preview_6x.png")

# Save HUD ASE
save_ase_multilayer(
    filepath=f"{TARGET_DIR}/hud.ase",
    layers_data=[("HUD_Icons", icons)],
    duration_ms=100
)

# ------------------------------------------------------------------------------
# MOCK PLAYABLE SCREENSHOT (Demo Game Screen with HUD, Hero, Slime, Map)
# ------------------------------------------------------------------------------
# 288x192 px demo map with live gameplay overlay
from generate_tileset import map_img
demo_screen = map_img.copy()

# Add Slime on grass (tile 7, 4)
slime_sprite = slime_frames[0]
demo_screen.paste(slime_sprite, (7 * 24, 4 * 24), slime_sprite)

# Draw HUD overlay at top-left
# 3 Hearts (2 Full, 1 Half)
demo_screen.paste(h_full, (8, 8), h_full)
demo_screen.paste(h_full, (26, 8), h_full)
demo_screen.paste(h_half, (44, 8), h_half)

# Coin counter (Coin icon + 25)
demo_screen.paste(coin, (70, 8), coin)
# Key icon
demo_screen.paste(key, (100, 8), key)

demo_screen.save(f"{TARGET_DIR}/pantalla_juego_demo.png")
demo_prev = demo_screen.resize((288 * 3, 192 * 3), Image.NEAREST)
demo_prev.save(f"{TARGET_DIR}/pantalla_juego_preview_3x.png")
demo_prev.save(f"{BRAIN}/pantalla_juego_preview_3x.png")

print("✓ Slime animado, HUD completo y Pantalla Demo generados exitosamente.")

