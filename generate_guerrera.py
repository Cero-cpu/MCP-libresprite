#!/usr/bin/env python3
"""
Dark Fantasy Female Warrior Knight — Pixel Art Generator
4-frame idle animation, 128x128 per frame, spritesheet 512x128
Layers: BG / Cape / Legs / Body / Arms / Head / Sword / Rune_FX
"""
import sys, os, math, struct, zlib
sys.path.insert(0, '/home/cachy/Descargas/mcp libresprite')

from PIL import Image, ImageDraw

# ─── DIMENSIONS ───────────────────────────────────────────────────────────────
W, H       = 128, 128
FRAMES     = 4
OUT        = '/home/cachy/Escritorio'
BRAIN      = '/home/cachy/.gemini/antigravity/brain/df3e9207-a8f7-45d7-8607-4894fe749ff0'

# ─── PALETTE ──────────────────────────────────────────────────────────────────
BG         = (128, 128, 128, 255)   # neutral grey bg

# Obsidian armor
AD3        = (10,  8,  20, 255)   # darkest shadow
AD2        = (20, 16,  38, 255)
AD1        = (32, 26,  58, 255)
AM         = (46, 38,  80, 255)   # mid
AL1        = (65, 54, 108, 255)   # highlight
AL2        = (95, 80, 148, 255)   # bright highlight
ARIM       = (130,110,180, 255)   # rim light

# Purple runes / glow
RD         = ( 80, 20, 120, 255)
RM         = (148, 55, 210, 255)
RL         = (210,130, 255, 255)
RGLOW      = (220,170, 255, 160)

# Crimson cape
CD3        = ( 55,  8,  8, 255)
CD2        = ( 95, 14, 14, 255)
CM         = (158, 24, 24, 255)
CL         = (210, 48, 48, 255)
CRIM       = (235, 88, 88, 255)

# Skin
SKND       = (155, 95, 70, 255)
SKNM       = (205,148,112, 255)
SKNL       = (238,195,160, 255)

# Hair (raven + purple sheen)
HD         = ( 14,  7, 24, 255)
HM         = ( 25, 14, 42, 255)
HL         = ( 50, 28, 78, 255)
HSHI       = ( 95, 55,140, 255)

# Ethereal sword
SC         = (230,245,255, 255)   # core white
SL1        = (165,215,252, 255)
SL2        = (105,172,235, 255)
SD1        = ( 65,132,205, 255)

# Face
EYEC       = (155, 50, 225, 255)
EYEHI      = (255,220,255, 255)
LIPC       = (158, 36, 36, 255)

OL         = (  5,  3, 10, 255)   # outline

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def rune(draw, cx, cy, style='dot', col=RM, bright=RL):
    if style == 'dot':
        draw.ellipse([cx-2,cy-2,cx+2,cy+2], fill=col)
        draw.point([(cx,cy)], fill=bright)
    elif style == 'star':
        for a in range(0,360,45):
            r = math.radians(a)
            draw.line([(cx,cy),(cx+int(5*math.cos(r)),cy+int(5*math.sin(r)))], fill=col, width=1)
        draw.ellipse([cx-2,cy-2,cx+2,cy+2], fill=bright)
    elif style == 'cross':
        draw.line([(cx-4,cy),(cx+4,cy)], fill=col, width=1)
        draw.line([(cx,cy-4),(cx,cy+4)], fill=col, width=1)
        draw.point([(cx,cy)], fill=bright)
    elif style == 'diamond':
        draw.polygon([(cx,cy-4),(cx+3,cy),(cx,cy+4),(cx-3,cy)], fill=col)
        draw.point([(cx,cy)], fill=bright)
    elif style == 'omega':
        draw.arc([cx-5,cy-5,cx+5,cy+3], 200, 340, fill=col, width=1)
        draw.line([(cx-5,cy+1),(cx-3,cy+5)], fill=col, width=1)
        draw.line([(cx+3,cy+1),(cx+5,cy+5)], fill=col, width=1)
        draw.point([(cx,cy-1)], fill=bright)

def outline_pass(img):
    """Draw 1-px dark outline around any non-BG pixel."""
    src = img.load()
    out = img.copy()
    opx = out.load()
    bg3 = (128,128,128)
    for y in range(1, H-1):
        for x in range(1, W-1):
            r,g,b,a = src[x,y]
            if (r,g,b) == bg3 or a < 10:
                for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                    nr,ng,nb,na = src[x+dx,y+dy]
                    if (nr,ng,nb) != bg3 and na > 120:
                        opx[x,y] = OL
                        break
    return out

# ─── FRAME GENERATOR ──────────────────────────────────────────────────────────
def draw_frame(fi=0):
    # Breathing & sway offsets per frame
    breath   = [0, -1,  0, -2][fi]        # torso/head rise
    sway     = [0, -2,  0,  2][fi]        # cape bottom sway
    glow_a   = [150, 185, 155, 205][fi]   # sword glow alpha
    blink    = (fi == 3)                   # blink on frame 3

    img  = Image.new('RGBA', (W,H), BG)
    d    = ImageDraw.Draw(img)

    # ── Ground shadow ──
    d.ellipse([46,120,82,127], fill=(15,8,30,110))

    # ── CAPE (behind body) ──
    cy0  = 40 + breath
    cpoly = [
        (58, cy0),
        (70, cy0),
        (76+sway, 78),
        (79+sway, 108),
        (66+sway//2, 122),
        (62+sway//3, 122),
        (49-sway,    108),
        (52-sway,    78),
    ]
    d.polygon(cpoly, fill=CM)
    # Dark left fold
    d.polygon([(58,cy0),(64,cy0+4),(58,78),(50,108),(49-sway,108),(52-sway,78)], fill=CD2)
    # Bright right edge
    d.line([(70,cy0),(76+sway,78),(79+sway,108),(66+sway//2,122)], fill=CL, width=1)
    # Fold lines
    for i,fy in enumerate([cy0+22, cy0+45, cy0+68]):
        fo = sway*(i+1)//4
        d.line([(58,fy),(72+fo,fy+3)], fill=CD3, width=1)
    # Cape rim light
    d.line([(70,cy0),(78+sway,78)], fill=CRIM, width=1)

    # ── LEGS ──
    ly = 88 + breath
    # Left thigh
    d.rectangle([50,ly,62,102], fill=AD2)
    d.rectangle([50,ly,55,102], fill=AD3)
    d.line([(62,ly),(62,102)], fill=AL1, width=1)
    # Right thigh
    d.rectangle([65,ly,77,102], fill=AD2)
    d.rectangle([72,ly,77,102], fill=AD3)
    d.line([(65,ly),(65,102)], fill=AL1, width=1)
    # Left greave
    d.rectangle([50,102,62,117], fill=AD1)
    d.rectangle([57,102,62,117], fill=AM)
    d.line([(57,102),(57,117)], fill=AL1, width=1)
    # Right greave
    d.rectangle([65,102,76,117], fill=AD1)
    d.rectangle([65,102,70,117], fill=AM)
    d.line([(70,102),(70,117)], fill=AL1, width=1)
    # Knee caps
    d.ellipse([49,98,63,106], fill=AM)
    d.ellipse([63,98,77,106], fill=AM)
    d.ellipse([52,100,60,105], fill=AL1)
    d.ellipse([66,100,74,105], fill=AL1)
    rune(d, 56,102, 'dot')
    rune(d, 70,102, 'dot')
    # Boots
    d.rectangle([47,115,63,125], fill=AD2)
    d.rectangle([64,115,80,125], fill=AD2)
    d.rectangle([47,119,65,125], fill=AD3)
    d.rectangle([62,119,81,125], fill=AD3)
    d.line([(47,115),(63,115)], fill=AL1, width=1)
    d.line([(64,115),(80,115)], fill=AL1, width=1)

    # ── BREASTPLATE / TORSO ──
    tx, ty  = 46, 40 + breath
    tw, th  = 36, 50
    # Torso trapezoid
    d.polygon([(tx,ty+4),(tx+tw,ty+4),(tx+tw+2,ty+th),(tx-2,ty+th)], fill=AD1)
    # Right shading
    d.polygon([(tx+tw//2+2,ty+4),(tx+tw,ty+4),(tx+tw+2,ty+th),(tx+tw//2,ty+th)], fill=AD2)
    # Left edge highlight
    d.line([(tx,ty+6),(tx-2,ty+th)], fill=AL1, width=1)
    # Center ridge
    d.line([(64,ty+4),(64,ty+th)], fill=AL2, width=2)
    # Top highlight band
    d.line([(tx+2,ty+6),(tx+tw-2,ty+6)], fill=AL2, width=1)
    # Breastplate rune star (center chest)
    rune(d, 64, ty+16, 'star')
    rune(d, 56, ty+28, 'cross')
    rune(d, 72, ty+28, 'cross')
    rune(d, 60, ty+40, 'diamond')
    rune(d, 68, ty+40, 'diamond')

    # Pauldrons
    # Left
    d.ellipse([32,ty-4,54,ty+18], fill=AM)
    d.ellipse([32,ty-4,48,ty+10], fill=AD1)
    d.arc( [32,ty-4,54,ty+18], 190, 355, fill=AL2, width=1)
    rune(d, 43, ty+6, 'diamond')
    # Right
    d.ellipse([74,ty-4,96,ty+18], fill=AM)
    d.ellipse([80,ty-4,96,ty+10], fill=AD2)
    d.arc( [74,ty-4,96,ty+18], 185, 350, fill=AL2, width=1)
    rune(d, 85, ty+6, 'diamond')

    # Waist/belt
    d.rectangle([tx-2,ty+th-2,tx+tw+4,ty+th+8], fill=AD2)
    d.line([(tx-1,ty+th),(tx+tw+3,ty+th)], fill=AM, width=1)
    # Belt buckle
    d.rectangle([59,ty+th,69,ty+th+8], fill=AM)
    d.rectangle([61,ty+th+1,67,ty+th+7], fill=AL1)
    rune(d, 64, ty+th+4, 'dot')

    # ── ARMS ──
    # Left arm (sword arm)
    lax = 32
    d.rectangle([lax,ty+16,lax+13,ty+42], fill=AD1)
    d.rectangle([lax+9,ty+16,lax+13,ty+42], fill=AD2)
    d.line([(lax,ty+16),(lax,ty+42)], fill=AL1, width=1)
    # Left elbow guard
    d.ellipse([lax-1,ty+36,lax+14,ty+46], fill=AM)
    d.ellipse([lax+2,ty+37,lax+11,ty+44], fill=AL1)
    # Left gauntlet
    d.rectangle([lax-2,ty+44,lax+15,ty+56], fill=AM)
    d.rectangle([lax-2,ty+44,lax+5,ty+56], fill=AD1)
    d.line([(lax-2,ty+54),(lax+15,ty+54)], fill=AL1, width=1)

    # Right arm
    rax = 82
    d.rectangle([rax,ty+16,rax+13,ty+42], fill=AD1)
    d.rectangle([rax,ty+16,rax+4,ty+42], fill=AD2)
    d.line([(rax+13,ty+16),(rax+13,ty+42)], fill=AL1, width=1)
    # Right elbow guard
    d.ellipse([rax-1,ty+36,rax+14,ty+46], fill=AM)
    d.ellipse([rax+3,ty+37,rax+12,ty+44], fill=AL1)
    # Right gauntlet
    d.rectangle([rax,ty+44,rax+15,ty+56], fill=AM)
    d.rectangle([rax+8,ty+44,rax+15,ty+56], fill=AD1)
    d.line([(rax,ty+54),(rax+15,ty+54)], fill=AL1, width=1)
    # Arm runes
    rune(d, lax+6, ty+28, 'dot')
    rune(d, rax+6, ty+28, 'dot')

    # ── HEAD ──
    hx, hy = 52, 10 + breath
    hw, hh = 24, 22

    # Neck
    d.rectangle([60,hy+hh,67,hy+hh+10], fill=SKNM)
    # Gorget
    d.rectangle([56,hy+hh+6,72,hy+hh+14], fill=AD1)
    d.line([(56,hy+hh+6),(72,hy+hh+6)], fill=AL1, width=1)

    # Helmet dome
    d.ellipse([hx-2,hy-6,hx+hw+2,hy+hh], fill=AD1)
    d.ellipse([hx,  hy-7,hx+hw,  hy+hh-6], fill=AM)
    d.ellipse([hx+2,hy-6,hx+hw-2,hy+hh-10], fill=AL1)
    d.arc([hx+4,hy-5,hx+hw-4,hy+4], 200, 340, fill=AL2, width=1)

    # Face opening
    d.rectangle([hx+2,hy+4,hx+hw-2,hy+hh-2], fill=SKNM)
    d.rectangle([hx+2,hy+4,hx+8,hy+hh-2], fill=SKND)   # left shadow
    d.line([(hx+hw-5,hy+6),(hx+hw-5,hy+hh-4)], fill=SKNL, width=1)

    # Eyes (glowing purple)
    ey = hy + 10
    if blink:
        d.line([(hx+4,ey+1),(hx+9,ey+1)], fill=AD2, width=2)
        d.line([(hx+15,ey+1),(hx+20,ey+1)], fill=AD2, width=2)
    else:
        d.rectangle([hx+4, ey,  hx+9, ey+3], fill=EYEC)
        d.rectangle([hx+15,ey,  hx+20,ey+3], fill=EYEC)
        d.point([(hx+6,ey+1),(hx+17,ey+1)], fill=EYEHI)
        # Eye glow halo
        for r in [3,2]:
            a = 60 if r==3 else 100
            d.rectangle([hx+4-r,ey-r,hx+9+r,ey+3+r], outline=(155,50,225,a))
            d.rectangle([hx+15-r,ey-r,hx+20+r,ey+3+r], outline=(155,50,225,a))

    # Nose & lips
    d.point([(64, hy+14)], fill=SKND)
    d.line([(hx+8,hy+17),(hx+16,hy+17)], fill=LIPC, width=1)

    # Cheek guards
    d.rectangle([hx-3,hy+4,hx+3,hy+18], fill=AD2)
    d.rectangle([hx+hw-3,hy+4,hx+hw+3,hy+18], fill=AD2)
    d.line([(hx-3,hy+4),(hx+3,hy+4)], fill=AL1, width=1)
    d.line([(hx+hw-3,hy+4),(hx+hw+3,hy+4)], fill=AL1, width=1)

    # Helmet crest / plume (crimson)
    for i in range(5):
        px2 = hx + hw//2 - 3 + i
        py2 = hy - 7 - (2 if i==2 else 0)
        col = CM if i%2==0 else CL
        d.line([(px2, hy-6),(px2+sway//3, py2-10)], fill=col, width=1)

    # Forehead rune
    rune(d, 64, hy+1, 'omega')

    # Hair strands (behind helmet)
    for i in range(7):
        hpx2 = hx - 2 + i*4
        hlen2 = 10 + (i%3)*4 + abs(sway)
        sw2  = -sway//3
        d.line([(hpx2, hy+hh-3),(hpx2+sw2, hy+hh+hlen2)],
               fill=HM if i%2==0 else HD, width=2)
        if i==3:
            d.line([(hpx2, hy+hh-3),(hpx2+sw2, hy+hh+hlen2)],
                   fill=HSHI, width=1)

    # ── SWORD (held in left hand, blade rising upper-left) ──
    sxb = lax + 7     # base x (at left hand)
    syb = ty + 54     # base y (at left hand)
    sx_tip = sxb - 14
    sy_tip = syb - 60

    # Glow aura behind blade
    for gw in range(5,0,-1):
        ga = glow_a * gw // 14
        d.line([(sxb, syb-6),(sx_tip, sy_tip+6)], fill=(80,160,230,ga), width=gw*2)

    # Blade body (tapers toward tip)
    for t in range(60):
        ratio = t/60
        bx2 = int(sxb + (sx_tip-sxb)*ratio)
        by3 = int(syb-6 + (sy_tip+6-syb+6)*ratio)
        bw2 = max(1,round(2.5*(1-ratio)))
        c   = SC if ratio<0.25 else (SL1 if ratio<0.6 else SL2)
        d.line([(bx2-bw2,by3),(bx2+bw2,by3)], fill=c, width=1)
    # Bright center ridge
    d.line([(sxb,syb-6),(sx_tip,sy_tip+6)], fill=SC, width=1)

    # Rune engravings on blade
    for i in range(4):
        rt = 0.15 + i*0.17
        rx2 = int(sxb+(sx_tip-sxb)*rt)
        ry2 = int(syb-6+(sy_tip+6-syb+6)*rt)
        rune(d, rx2, ry2, 'dot', col=RM, bright=RL)

    # Crossguard
    cgy = syb - 10
    d.rectangle([sxb-15,cgy-2,sxb+16,cgy+2], fill=AM)
    d.rectangle([sxb-13,cgy-1,sxb+14,cgy+1], fill=AL2)
    d.line([(sxb-15,cgy-2),(sxb+16,cgy-2)], fill=ARIM, width=1)
    rune(d, sxb-7, cgy, 'diamond')
    rune(d, sxb+8, cgy, 'diamond')

    # Grip
    d.rectangle([sxb-2,syb-8,sxb+2,syb+2], fill=AD3)
    d.line([(sxb,syb-8),(sxb,syb+2)], fill=AL1, width=1)
    # Pommel
    d.ellipse([sxb-5,syb,sxb+5,syb+10], fill=AM)
    d.ellipse([sxb-3,syb+2,sxb+3,syb+8], fill=AL2)
    rune(d, sxb, syb+5, 'dot')

    # ── OUTLINE PASS ──
    img = outline_pass(img)
    return img

# ─── GENERATE ALL FRAMES ──────────────────────────────────────────────────────
print("Generating 4 frames...")
frames = [draw_frame(i) for i in range(FRAMES)]

# ─── SAVE OUTPUTS ─────────────────────────────────────────────────────────────
# Single PNG (frame 0)
frames[0].save(f'{OUT}/guerrera.png')
print(f"  → guerrera.png")

# Spritesheet 512×128
sheet = Image.new('RGBA', (W*FRAMES, H), BG)
for i,f in enumerate(frames):
    sheet.paste(f, (i*W,0))
sheet.save(f'{OUT}/guerrera_sheet.png')
print(f"  → guerrera_sheet.png  ({W*FRAMES}×{H})")

# GIF animation
gif_p = [f.convert('RGB').quantize(colors=200, method=2) for f in frames]
gif_p[0].save(
    f'{OUT}/guerrera.gif',
    save_all=True, append_images=gif_p[1:],
    loop=0, duration=140, optimize=False
)
print(f"  → guerrera.gif  (140ms/frame)")

# 6× preview of frame 0
preview = frames[0].resize((W*6, H*6), Image.NEAREST)
preview.save(f'{OUT}/guerrera_preview_6x.png')
print(f"  → guerrera_preview_6x.png")

# 4× spritesheet preview
sheet4x = sheet.resize((W*FRAMES*4, H*4), Image.NEAREST)
sheet4x.save(f'{OUT}/guerrera_sheet_preview_4x.png')
print(f"  → guerrera_sheet_preview_4x.png")

# Copy preview to brain dir for display
import shutil
shutil.copy(f'{OUT}/guerrera_preview_6x.png',
            f'{BRAIN}/guerrera_preview_6x.png')
shutil.copy(f'{OUT}/guerrera_sheet_preview_4x.png',
            f'{BRAIN}/guerrera_sheet_preview_4x.png')
print(f"  → previews copied to brain dir")

# ─── ASE FILE ─────────────────────────────────────────────────────────────────
try:
    from ase_format import save_ase_multilayer

    tags = [
        {"name": "Idle_Breathe", "from": 0, "to": 3,
         "anim_direction": 0, "color": (60,180,80)}
    ]
    save_ase_multilayer(
        filepath = f'{OUT}/guerrera.ase',
        layers_data = [("Guerrera_Full", frames)],
        duration_ms = 140,
        tags=tags
    )
    print(f"  → guerrera.ase  (multicapa LibreSprite con tags)")
except Exception as e:
    print(f"  ! ASE save error: {e}")

print("\n✓ Guerrera épica generada en", OUT)

