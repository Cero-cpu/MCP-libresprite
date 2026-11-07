"""Generadores Procedurales de Alta Calidad para LibreSprite (Nivel PixeLab Senior).

Permite a la IA generar personajes, enemigos, props y armas en milisegundos
a cualquier resolución (16x16, 24x24, 32x32, 48x48, 64x64...) con:
- Capas independientes nativas para LibreSprite (.ase).
- Animación Idle orgánica (respiración, cabello, parpadeo).
- Outlining selectivo automático (Sel-out).
- Tags nativos de animación (Idle, Action).
- Exportación simultánea: .ase, .gif, .png y preview HD 8x.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageDraw

from ase_format import save_ase_multilayer
from draw_engine import apply_auto_outline, parse_color, render_ascii_matrix
from palettes import PALETTES, create_hue_shifted_ramp


def _build_ramp(base_hex: str, count: int = 5) -> List[Tuple[int, int, int, int]]:
    return create_hue_shifted_ramp(base_hex, steps=count)


def generate_character(
    width: int = 48,
    height: int = 48,
    archetype: str = "anime_girl",   # anime_girl | warrior | mage | rogue | chibi
    hair_color: str = "#8e44ad",     # hex o nombre de color
    skin_tone: str = "#f5ba98",      # hex base
    eye_color: str = "#1abc9c",      # hex base
    outfit_primary: str = "#2c3e50", # hex base
    outfit_secondary: str = "#e74c3c", # hex base
    num_frames: int = 4,
    duration_ms: int = 140,
    outline_mode: str = "selective", # selective | dark | none
) -> List[Tuple[str, List[Image.Image]]]:
    """Genera un personaje pixel art completo multicapa con animación."""
    w, h = width, height

    # 1. Rampas de color con Hue-Shifting
    hair_ramp = _build_ramp(hair_color, 5)
    skin_ramp = _build_ramp(skin_tone, 5)
    outfit_ramp = _build_ramp(outfit_primary, 5)
    accent_ramp = _build_ramp(outfit_secondary, 5)
    eye_c = parse_color(eye_color)

    pal = {
        # Piel
        "s0": skin_ramp[4],  # highlight
        "s1": skin_ramp[3],  # base
        "s2": skin_ramp[2],  # mid shadow
        "s3": skin_ramp[1],  # deep shadow
        "blush": (240, 100, 120, 255),
        "lip": (180, 50, 70, 255),

        # Pelo
        "h0": hair_ramp[4],  # shine
        "h1": hair_ramp[3],  # light
        "h2": hair_ramp[2],  # base
        "h3": hair_ramp[1],  # shadow
        "h4": hair_ramp[0],  # outline

        # Ropa principal
        "u0": outfit_ramp[4],
        "u1": outfit_ramp[3],
        "u2": outfit_ramp[2],
        "u3": outfit_ramp[1],
        "u4": outfit_ramp[0],

        # Acento (lazo, capa, gema)
        "r0": accent_ramp[4],
        "r1": accent_ramp[3],
        "r2": accent_ramp[1],

        # Neutros
        "white": (255, 255, 255, 255),
        "dark": (20, 16, 28, 255),
        "gold": (255, 220, 80, 255),
        "boot": (100, 65, 45, 255),
        "boot_dark": (60, 35, 20, 255),
    }

    # Proporciones dinámicas según resolución
    scale_y = h / 48.0
    scale_x = w / 48.0

    head_y = int(6 * scale_y)
    head_h = int(12 * scale_y)
    torso_y = head_y + head_h
    torso_h = int(10 * scale_y)
    skirt_y = torso_y + torso_h
    skirt_h = int(8 * scale_y)
    legs_y = skirt_y + skirt_h
    legs_h = max(4, h - legs_y - int(4 * scale_y))
    center_x = w // 2

    # Construcción de las capas
    shadow_frames = []
    hair_back_frames = []
    body_frames = []
    face_frames = []
    clothes_frames = []
    hair_front_frames = []
    fx_frames = []

    for f_idx in range(num_frames):
        # Fase sinusoidal continua: fluidez garantizada para CUALQUIER número de frames (2, 4, 6, 8, 12, 24...)
        phase = (f_idx / max(1, num_frames)) * 2 * math.pi
        dy = round(-math.sin(phase) * max(1, int(1.2 * scale_y)))
        sway = round(math.sin(phase) * max(1, int(1.0 * scale_x)))
        blink = (f_idx == max(1, num_frames - 1)) or (num_frames >= 8 and f_idx == num_frames // 2)

        # CAPA 1: SOMBRA DE SUELO
        s_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        sw_w = int(w * 0.4)
        sw_h = max(2, int(h * 0.08))
        sw_y = h - sw_h - 2
        s_draw.ellipse([center_x - sw_w // 2, sw_y, center_x + sw_w // 2, sw_y + sw_h], fill=(20, 14, 30, 90))
        s_draw.ellipse([center_x - sw_w // 4, sw_y + 1, center_x + sw_w // 4, sw_y + sw_h - 1], fill=(15, 10, 22, 130))
        shadow_frames.append(s_img)

        # CAPA 2: PELO TRASERO
        hb_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        hb_draw = ImageDraw.Draw(hb_img)
        # Cabello posterior con forma de cascada
        hair_w = int(18 * scale_x)
        top_y = head_y + 2 + dy
        bottom_y = min(h - 6, legs_y + int(4 * scale_y) + dy)
        hb_draw.ellipse([center_x - hair_w // 2 + sway, top_y, center_x + hair_w // 2 + sway, bottom_y], fill=pal["h2"])
        hb_draw.ellipse([center_x - hair_w // 2 + 1 + sway, top_y + 2, center_x + hair_w // 2 - 1 + sway, bottom_y - 2], fill=pal["h1"])
        hair_back_frames.append(hb_img)

        # CAPA 3: CUERPO Y PIEL
        b_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(b_img)

        # Piernas y medias
        leg_w = max(2, int(3 * scale_x))
        gap = max(1, int(1 * scale_x))
        l1_x = center_x - leg_w - gap
        l2_x = center_x + gap

        # Medias oscuras
        b_draw.rectangle([l1_x, legs_y, l1_x + leg_w - 1, legs_y + legs_h - 3], fill=pal["dark"])
        b_draw.rectangle([l2_x, legs_y, l2_x + leg_w - 1, legs_y + legs_h - 3], fill=pal["dark"])

        # Botas
        b_draw.rectangle([l1_x - 1, legs_y + legs_h - 3, l1_x + leg_w, legs_y + legs_h], fill=pal["boot"])
        b_draw.rectangle([l2_x, legs_y + legs_h - 3, l2_x + leg_w + 1, legs_y + legs_h], fill=pal["boot"])

        # Piel de muslo visible
        b_draw.rectangle([l1_x, skirt_y + skirt_h - 2, l1_x + leg_w - 1, legs_y], fill=pal["s1"])
        b_draw.rectangle([l2_x, skirt_y + skirt_h - 2, l2_x + leg_w - 1, legs_y], fill=pal["s1"])

        # Rostro base
        face_rx = int(7 * scale_x)
        face_ry = int(6 * scale_y)
        face_cy = head_y + face_ry + dy
        b_draw.ellipse([center_x - face_rx, face_cy - face_ry, center_x + face_rx, face_cy + face_ry], fill=pal["s1"])

        # Cuello
        neck_w = max(2, int(4 * scale_x))
        b_draw.rectangle([center_x - neck_w // 2, face_cy + face_ry - 2, center_x + neck_w // 2, torso_y + dy + 2], fill=pal["s2"])

        body_frames.append(b_img)

        # CAPA 4: ROSTRO Y EXPRESIÓN
        f_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        eye_y = face_cy - 1
        eye_spacing = max(3, int(4 * scale_x))
        e1_x = center_x - eye_spacing
        e2_x = center_x + eye_spacing - 1

        if blink:
            # Parpadeo
            for px in range(e1_x - 1, e1_x + 2):
                f_img.putpixel((px, eye_y), pal["dark"])
            for px in range(e2_x - 1, e2_x + 2):
                f_img.putpixel((px, eye_y), pal["dark"])
        else:
            # Pestañas y ojos
            f_img.putpixel((e1_x - 1, eye_y - 1), pal["dark"])
            f_img.putpixel((e1_x, eye_y - 1), pal["dark"])
            f_img.putpixel((e1_x + 1, eye_y - 1), pal["dark"])
            f_img.putpixel((e2_x - 1, eye_y - 1), pal["dark"])
            f_img.putpixel((e2_x, eye_y - 1), pal["dark"])
            f_img.putpixel((e2_x + 1, eye_y - 1), pal["dark"])

            # Pupila + Iris
            f_img.putpixel((e1_x, eye_y), eye_c)
            f_img.putpixel((e1_x, eye_y + 1), eye_c)
            f_img.putpixel((e2_x, eye_y), eye_c)
            f_img.putpixel((e2_x, eye_y + 1), eye_c)

            # Brillo blanco
            f_img.putpixel((e1_x - 1, eye_y), pal["white"])
            f_img.putpixel((e2_x - 1, eye_y), pal["white"])

        # Rubor kawaii
        f_img.putpixel((e1_x - 2, eye_y + 2), pal["blush"])
        f_img.putpixel((e1_x - 1, eye_y + 2), pal["blush"])
        f_img.putpixel((e2_x + 1, eye_y + 2), pal["blush"])
        f_img.putpixel((e2_x + 2, eye_y + 2), pal["blush"])

        # Boquita
        f_img.putpixel((center_x, eye_y + 3), pal["lip"])

        face_frames.append(f_img)

        # CAPA 5: ROPA
        c_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(c_img)

        # Camisa / Torso
        torso_w = int(10 * scale_x)
        c_draw.rectangle([center_x - torso_w // 2, torso_y + dy, center_x + torso_w // 2, skirt_y + dy], fill=pal["u1"])

        # Cuello blanco y lazo
        c_draw.polygon([
            (center_x - torso_w // 3, torso_y + dy),
            (center_x, torso_y + dy + int(4 * scale_y)),
            (center_x + torso_w // 3, torso_y + dy)
        ], fill=pal["white"])
        # Lazo acento
        c_draw.ellipse([center_x - 2, torso_y + dy + 2, center_x + 2, torso_y + dy + 5], fill=pal["r1"])

        # Falda plisada
        skirt_top_w = torso_w
        skirt_bot_w = int(16 * scale_x)
        c_draw.polygon([
            (center_x - skirt_top_w // 2, skirt_y + dy),
            (center_x + skirt_top_w // 2, skirt_y + dy),
            (center_x + skirt_bot_w // 2, skirt_y + skirt_h + dy),
            (center_x - skirt_bot_w // 2, skirt_y + skirt_h + dy),
        ], fill=pal["u2"])

        # Pliegues de la falda
        for px in range(center_x - skirt_bot_w // 2 + 2, center_x + skirt_bot_w // 2, max(2, int(3 * scale_x))):
            c_draw.line([(px, skirt_y + dy + 1), (px, skirt_y + skirt_h + dy)], fill=pal["u3"])

        # Brazos a los lados
        arm_w = max(2, int(3 * scale_x))
        c_draw.rectangle([center_x - torso_w // 2 - arm_w + 1, torso_y + dy, center_x - torso_w // 2, torso_y + torso_h + dy], fill=pal["u1"])
        c_draw.rectangle([center_x + torso_w // 2, torso_y + dy, center_x + torso_w // 2 + arm_w - 1, torso_y + torso_h + dy], fill=pal["u1"])

        # Manitos piel
        c_draw.rectangle([center_x - torso_w // 2 - arm_w + 1, torso_y + torso_h + dy, center_x - torso_w // 2, torso_y + torso_h + dy + 2], fill=pal["s1"])
        c_draw.rectangle([center_x + torso_w // 2, torso_y + torso_h + dy, center_x + torso_w // 2 + arm_w - 1, torso_y + torso_h + dy + 2], fill=pal["s1"])

        clothes_frames.append(c_img)

        # CAPA 6: PELO DELANTERO
        hf_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        hf_draw = ImageDraw.Draw(hf_img)

        # Corona de la cabeza
        crown_rx = int(8 * scale_x)
        crown_ry = int(7 * scale_y)
        hf_draw.ellipse([center_x - crown_rx, head_y + dy, center_x + crown_rx, head_y + crown_ry * 2 + dy], fill=pal["h2"])

        # Mechones frontales / Flequillo
        bangs_y = head_y + crown_ry + dy
        hf_draw.polygon([
            (center_x - crown_rx + 1, bangs_y),
            (center_x - crown_rx + 3, bangs_y + int(4 * scale_y)),
            (center_x - 1, bangs_y),
            (center_x + 1, bangs_y + int(3 * scale_y)),
            (center_x + crown_rx - 1, bangs_y),
        ], fill=pal["h1"])

        # Mechones laterales largos
        side_w = max(2, int(3 * scale_x))
        side_len = int(12 * scale_y)
        hf_draw.rectangle([center_x - crown_rx, bangs_y - 2, center_x - crown_rx + side_w, bangs_y + side_len], fill=pal["h2"])
        hf_draw.rectangle([center_x + crown_rx - side_w, bangs_y - 2, center_x + crown_rx, bangs_y + side_len], fill=pal["h2"])

        # Horquilla dorada
        hf_draw.ellipse([center_x + crown_rx - 4, head_y + dy + 3, center_x + crown_rx - 1, head_y + dy + 6], fill=pal["gold"])

        hair_front_frames.append(hf_img)

        # CAPA 7: HIGHLIGHTS Y BRILLOS
        fx_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        # Angel ring de pelo
        for hx in range(center_x - int(4 * scale_x), center_x + int(4 * scale_x)):
            fx_img.putpixel((hx, head_y + dy + 2), pal["h0"])
        fx_frames.append(fx_img)

    # Si se pide outline selectivo, procesar capas clave
    if outline_mode in ("selective", "dark"):
        for i in range(num_frames):
            clothes_frames[i] = apply_auto_outline(clothes_frames[i], mode=outline_mode)
            hair_front_frames[i] = apply_auto_outline(hair_front_frames[i], mode=outline_mode)

    layers = [
        ("Shadow", shadow_frames),
        ("Hair_Back", hair_back_frames),
        ("Body_Skin", body_frames),
        ("Face_Features", face_frames),
        ("Clothes", clothes_frames),
        ("Hair_Front", hair_front_frames),
        ("Highlights_FX", fx_frames),
    ]

    return layers


def generate_prop(
    prop_type: str = "sword",       # sword | potion | chest | shield | staff | gem
    width: int = 32,
    height: int = 32,
    primary_color: str = "#3498db",
    secondary_color: str = "#f1c40f",
    num_frames: int = 1,
) -> List[Tuple[str, List[Image.Image]]]:
    """Genera items, armas, pociones y props de alta calidad pixel art a cualquier resolución."""
    w, h = width, height
    c1_ramp = _build_ramp(primary_color, 5)
    c2_ramp = _build_ramp(secondary_color, 5)

    frames_base = []
    frames_fx = []

    for f_idx in range(num_frames):
        b_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        f_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(b_img)
        f_draw = ImageDraw.Draw(f_img)

        cx, cy = w // 2, h // 2

        if prop_type == "potion":
            # Frasco de poción con líquido y tapón
            b_draw.ellipse([cx - w//4, cy - h//6, cx + w//4, cy + h//3], fill=(220, 240, 255, 120), outline=(50, 70, 100, 200))
            b_draw.rectangle([cx - w//8, cy - h//3, cx + w//8, cy - h//6], fill=(220, 240, 255, 120))
            # Corcho
            b_draw.rectangle([cx - w//10, cy - h//3 - 2, cx + w//10, cy - h//3], fill=(160, 110, 70, 255))
            # Líquido mágico
            b_draw.ellipse([cx - w//5, cy, cx + w//5, cy + h//4], fill=c1_ramp[2])
            # Burbujas / Brillo
            f_draw.ellipse([cx - w//8, cy - h//12, cx - w//10, cy - h//16], fill=(255, 255, 255, 220))

        elif prop_type == "sword":
            # Espada diagonal épica
            p0 = (int(w * 0.2), int(h * 0.8))  # empuñadura
            p1 = (int(w * 0.8), int(h * 0.2))  # punta
            # Hoja
            b_draw.line([p0, p1], fill=c1_ramp[3], width=max(2, w // 12))
            b_draw.line([p0, p1], fill=c1_ramp[4], width=1)
            # Guarda
            gx0, gy0 = p0[0] - w//8, p0[1] - h//8
            gx1, gy1 = p0[0] + w//8, p0[1] + h//8
            b_draw.line([(p0[0] - 3, p0[1] + 3), (p0[0] + 3, p0[1] - 3)], fill=c2_ramp[3], width=3)
            # Brillo en punta
            f_img.putpixel(p1, (255, 255, 255, 255))

        elif prop_type == "chest":
            # Cofre del tesoro
            cw, ch = int(w * 0.7), int(h * 0.5)
            x0, y0 = cx - cw//2, cy - ch//4
            b_draw.rectangle([x0, y0, x0 + cw, y0 + ch], fill=c1_ramp[1], outline=(30, 20, 15, 255))
            # Tapa
            b_draw.arc([x0, y0 - ch//3, x0 + cw, y0 + ch//3], start=180, end=360, fill=c1_ramp[2], width=2)
            # Cerradura dorada
            b_draw.rectangle([cx - 2, y0 + ch//4, cx + 2, y0 + ch//2], fill=c2_ramp[3])

        else:
            # Gema o Cristal elemental
            gw, gh = int(w * 0.5), int(h * 0.6)
            pts = [
                (cx, cy - gh//2),
                (cx + gw//2, cy),
                (cx, cy + gh//2),
                (cx - gw//2, cy)
            ]
            b_draw.polygon(pts, fill=c1_ramp[2], outline=c1_ramp[0])
            f_draw.line([(cx - 1, cy - gh//3), (cx + 1, cy - gh//3)], fill=(255, 255, 255, 230))

        b_img = apply_auto_outline(b_img, mode="selective")
        frames_base.append(b_img)
        frames_fx.append(f_img)

    return [("Prop_Base", frames_base), ("Prop_FX", frames_fx)]


def generate_topdown_hero(
    width: int = 24,
    height: int = 24,
    hair_color: str = "#9b59b6",
    skin_tone: str = "#f5ba98",
    tunic_color: str = "#27ae60",
    pants_color: str = "#2c3e50",
    boots_color: str = "#795548",
    include_walk: bool = True,
    duration_ms: int = 140,
) -> Tuple[List[Tuple[str, List[Image.Image]]], List[Dict[str, Any]]]:
    """Genera un héroe RPG Top-Down profesional en 4 direcciones con anatomía conectada y ciclo de caminata.
    
    Retorna capas independientes y tags nativos de animación:
    - Down / Walk_Down (Frames 0-3)
    - Up / Walk_Up (Frames 4-7)
    - Right / Walk_Right (Frames 8-11)
    - Left / Walk_Left (Frames 12-15)
    """
    from draw_engine import fix_anatomical_gaps
    
    # Construir rampas de color
    h_ramp = _build_ramp(hair_color, 5)
    s_ramp = _build_ramp(skin_tone, 5)
    t_ramp = _build_ramp(tunic_color, 5)
    p_ramp = _build_ramp(pants_color, 4)
    b_ramp = _build_ramp(boots_color, 4)

    OL = (24, 20, 32, 255)
    SH = (20, 20, 30, 75)
    _  = (0, 0, 0, 0)
    WHT = (242, 246, 248, 255)
    GLD = (248, 195, 50, 255)
    EYE = (32, 24, 38, 255)
    GL  = (255, 255, 255, 255)
    BL  = (235, 135, 135, 255)

    def down_frame(step=0):
        bob = -1 if step in (1, 3) else 0
        m = [[_]*width for _ in range(height)]
        # Sombra
        for x in range(6, 18): m[22][x] = SH
        for x in range(8, 16): m[23][x] = SH
        # Piernas / Botas
        ly = 17 + bob
        for x in range(8, 16): m[ly][x] = p_ramp[2]
        m[ly][7] = OL; m[ly][11] = OL; m[ly][12] = OL; m[ly][16] = OL
        if step in (0, 2):
            for y in range(ly+1, ly+5):
                for x in range(7, 11): m[y][x] = b_ramp[2]
                m[y][6] = OL; m[y][11] = OL
                for x in range(13, 17): m[y][x] = b_ramp[2]
                m[y][12] = OL; m[y][17] = OL
            for x in range(7, 11): m[ly+5][x] = OL
            for x in range(13, 17): m[ly+5][x] = OL
        elif step == 1:
            for y in range(ly+1, ly+5):
                for x in range(7, 11): m[y][x] = b_ramp[2]
                m[y][6] = OL; m[y][11] = OL
            for x in range(7, 11): m[ly+5][x] = OL
            for y in range(ly+1, ly+4):
                for x in range(13, 17): m[y][x] = b_ramp[1]
                m[y][12] = OL; m[y][17] = OL
            for x in range(13, 17): m[ly+4][x] = OL
        elif step == 3:
            for y in range(ly+1, ly+4):
                for x in range(7, 11): m[y][x] = b_ramp[1]
                m[y][6] = OL; m[y][11] = OL
            for x in range(7, 11): m[ly+4][x] = OL
            for y in range(ly+1, ly+5):
                for x in range(13, 17): m[y][x] = b_ramp[2]
                m[y][12] = OL; m[y][17] = OL
            for x in range(13, 17): m[ly+5][x] = OL
        # Torso
        ty = 11 + bob
        for x in range(7, 17): m[ty][x] = t_ramp[2]
        m[ty][11] = WHT; m[ty][12] = WHT
        m[ty][6] = OL; m[ty][17] = OL
        for y in (ty+1, ty+2):
            for x in range(6, 18): m[y][x] = t_ramp[2]
            m[y][5] = OL; m[y][18] = OL
        m[ty+1][11] = WHT; m[ty+1][12] = WHT
        for y in (ty+3, ty+4):
            for x in range(7, 17): m[y][x] = t_ramp[2]
            m[y][6] = OL; m[y][17] = OL
        m[ty+3][5] = s_ramp[3]; m[ty+3][4] = OL; m[ty+4][5] = s_ramp[2]; m[ty+4][4] = OL
        m[ty+3][18] = s_ramp[3]; m[ty+3][19] = OL; m[ty+4][18] = s_ramp[2]; m[ty+4][19] = OL
        m[ty+5][5] = OL; m[ty+5][18] = OL
        for x in range(7, 17): m[ty+5][x] = b_ramp[1]
        m[ty+5][6] = OL; m[ty+5][17] = OL
        m[ty+5][11] = GLD; m[ty+5][12] = GLD
        # Cabeza
        hy = 2 + bob
        for x in range(8, 16): m[hy][x] = OL
        for x in range(7, 17): m[hy+1][x] = h_ramp[3]
        m[hy+1][6] = OL; m[hy+1][17] = OL
        for y in range(hy+2, hy+4):
            for x in range(6, 18): m[y][x] = h_ramp[3]
            m[y][5] = OL; m[y][18] = OL
        m[hy+1][10] = h_ramp[4]; m[hy+1][11] = h_ramp[4]
        for y in range(hy+4, hy+9):
            for x in range(6, 18): m[y][x] = s_ramp[3]
            m[y][5] = OL; m[y][18] = OL
        m[hy+4][6] = h_ramp[3]; m[hy+4][7] = h_ramp[3]; m[hy+4][11] = h_ramp[4]; m[hy+4][16] = h_ramp[2]
        m[hy+5][6] = h_ramp[2]; m[hy+5][7] = h_ramp[3]; m[hy+5][16] = h_ramp[1]
        for y in (hy+6, hy+7):
            m[y][8] = EYE; m[y][9] = EYE; m[y][14] = EYE; m[y][15] = EYE
        m[hy+6][8] = GL; m[hy+6][14] = GL
        m[hy+8][7] = BL; m[hy+8][16] = BL
        for x in range(7, 17): m[hy+9][x] = s_ramp[2]
        m[hy+9][6] = OL; m[hy+9][17] = OL
        m[hy+10][6] = _; m[hy+10][7] = OL
        for x in range(8, 16): m[hy+10][x] = s_ramp[1]
        m[hy+10][16] = OL; m[hy+10][17] = _
        return m

    def up_frame(step=0):
        bob = -1 if step in (1, 3) else 0
        m = [[_]*width for _ in range(height)]
        for x in range(6, 18): m[22][x] = SH
        for x in range(8, 16): m[23][x] = SH
        ly = 17 + bob
        for x in range(8, 16): m[ly][x] = p_ramp[2]
        m[ly][7] = OL; m[ly][11] = OL; m[ly][12] = OL; m[ly][16] = OL
        if step in (0, 2):
            for y in range(ly+1, ly+5):
                for x in range(7, 11): m[y][x] = b_ramp[1]
                m[y][6] = OL; m[y][11] = OL
                for x in range(13, 17): m[y][x] = b_ramp[1]
                m[y][12] = OL; m[y][17] = OL
            for x in range(7, 11): m[ly+5][x] = OL
            for x in range(13, 17): m[ly+5][x] = OL
        elif step == 1:
            for y in range(ly+1, ly+4):
                for x in range(7, 11): m[y][x] = b_ramp[2]
                m[y][6] = OL; m[y][11] = OL
            for x in range(7, 11): m[ly+4][x] = OL
            for y in range(ly+1, ly+5):
                for x in range(13, 17): m[y][x] = b_ramp[1]
                m[y][12] = OL; m[y][17] = OL
            for x in range(13, 17): m[ly+5][x] = OL
        elif step == 3:
            for y in range(ly+1, ly+5):
                for x in range(7, 11): m[y][x] = b_ramp[1]
                m[y][6] = OL; m[y][11] = OL
            for x in range(7, 11): m[ly+5][x] = OL
            for y in range(ly+1, ly+4):
                for x in range(13, 17): m[y][x] = b_ramp[2]
                m[y][12] = OL; m[y][17] = OL
            for x in range(13, 17): m[ly+4][x] = OL
        ty = 11 + bob
        for x in range(7, 17): m[ty][x] = t_ramp[1]
        m[ty][6] = OL; m[ty][17] = OL
        for y in (ty+1, ty+2):
            for x in range(6, 18): m[y][x] = t_ramp[1]
            m[y][5] = OL; m[y][18] = OL
        for y in range(ty+1, ty+5):
            for x in range(8, 16): m[y][x] = b_ramp[2]
            m[y][7] = OL; m[y][16] = OL
        m[ty+1][10] = b_ramp[3]; m[ty+1][11] = b_ramp[3]; m[ty+1][12] = b_ramp[3]
        m[ty+2][11] = GLD; m[ty+2][12] = GLD
        for x in range(7, 17): m[ty+5][x] = b_ramp[1]
        m[ty+5][6] = OL; m[ty+5][17] = OL
        hy = 2 + bob
        for x in range(8, 16): m[hy][x] = OL
        for x in range(7, 17): m[hy+1][x] = h_ramp[3]
        m[hy+1][6] = OL; m[hy+1][17] = OL
        for y in range(hy+2, hy+9):
            for x in range(6, 18): m[y][x] = h_ramp[3]
            m[y][5] = OL; m[y][18] = OL
        m[hy+2][10] = h_ramp[4]; m[hy+2][11] = h_ramp[4]
        for x in range(7, 17): m[hy+9][x] = h_ramp[2]
        m[hy+9][6] = OL; m[hy+9][17] = OL
        for x in range(8, 16): m[hy+10][x] = h_ramp[1]
        m[hy+10][7] = OL; m[hy+10][16] = OL
        return m

    def right_frame(step=0):
        bob = -1 if step in (1, 3) else 0
        m = [[_]*width for _ in range(height)]
        for x in range(7, 18): m[22][x] = SH
        for x in range(9, 16): m[23][x] = SH
        ly = 17 + bob
        for x in range(10, 15): m[ly][x] = p_ramp[2]
        m[ly][9] = OL; m[ly][15] = OL
        if step in (0, 2):
            for y in range(ly+1, ly+5):
                for x in range(10, 15): m[y][x] = b_ramp[2]
                m[y][9] = OL; m[y][15] = OL
            for x in range(10, 16): m[ly+5][x] = OL
        elif step == 1:
            for y in range(ly+1, ly+5):
                for x in range(12, 17): m[y][x] = b_ramp[2]
                m[y][11] = OL; m[y][17] = OL
            for x in range(12, 17): m[ly+5][x] = OL
            for y in range(ly+1, ly+4):
                for x in range(8, 12): m[y][x] = b_ramp[1]
                m[y][7] = OL; m[y][12] = OL
            for x in range(8, 12): m[ly+4][x] = OL
        elif step == 3:
            for y in range(ly+1, ly+4):
                for x in range(12, 16): m[y][x] = b_ramp[1]
                m[y][11] = OL; m[y][16] = OL
            for x in range(12, 16): m[ly+4][x] = OL
            for y in range(ly+1, ly+5):
                for x in range(8, 12): m[y][x] = b_ramp[2]
                m[y][7] = OL; m[y][12] = OL
            for x in range(8, 12): m[ly+5][x] = OL
        ty = 11 + bob
        for x in range(8, 16): m[ty][x] = t_ramp[2]
        m[ty][15] = WHT; m[ty][7] = OL; m[ty][16] = OL
        for y in range(ty+1, ty+5):
            m[y][7] = OL; m[y][8] = b_ramp[2]; m[y][9] = b_ramp[2]
            for x in range(10, 16): m[y][x] = t_ramp[2]
            m[y][16] = OL
        arm_x = 12 + (2 if step == 1 else (-1 if step == 3 else 0))
        for y in (ty+1, ty+2):
            m[y][arm_x] = t_ramp[3]
            m[y][arm_x-1] = OL; m[y][arm_x+1] = OL
        m[ty+3][arm_x] = s_ramp[3]; m[ty+3][arm_x-1] = OL; m[ty+3][arm_x+1] = OL
        m[ty+4][arm_x] = OL
        for x in range(9, 16): m[ty+5][x] = b_ramp[1]
        m[ty+5][12] = GLD; m[ty+5][8] = OL; m[ty+5][16] = OL
        hy = 2 + bob
        for x in range(9, 16): m[hy][x] = OL
        for x in range(8, 16): m[hy+1][x] = h_ramp[3]
        m[hy+1][7] = OL; m[hy+1][16] = OL
        for y in range(hy+2, hy+5):
            for x in range(7, 16): m[y][x] = h_ramp[3]
            m[y][6] = OL; m[y][16] = OL
        m[hy+1][12] = h_ramp[4]; m[hy+2][11] = h_ramp[4]
        for y in range(hy+5, hy+9):
            m[y][6] = OL; m[y][7] = h_ramp[2]; m[y][8] = h_ramp[3]
        m[hy+9][7] = OL; m[hy+9][8] = h_ramp[1]; m[hy+10][8] = OL
        for y in range(hy+5, hy+9):
            for x in range(9, 16): m[y][x] = s_ramp[3]
        m[hy+4][13] = h_ramp[3]; m[hy+4][14] = h_ramp[4]; m[hy+4][15] = h_ramp[3]; m[hy+4][16] = OL
        m[hy+5][14] = h_ramp[3]; m[hy+5][15] = h_ramp[2]
        m[hy+6][13] = EYE; m[hy+7][13] = EYE; m[hy+6][13] = GL
        m[hy+8][14] = BL
        m[hy+5][16] = OL; m[hy+6][16] = OL; m[hy+7][16] = OL; m[hy+8][15] = OL
        for x in range(9, 15): m[hy+9][x] = s_ramp[2]
        m[hy+9][15] = OL
        for x in range(9, 14): m[hy+10][x] = s_ramp[1]
        m[hy+10][8] = OL; m[hy+10][14] = OL
        return m

    def m2img(mat):
        im = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        for y in range(height):
            for x in range(width):
                im.putpixel((x, y), mat[y][x])
        return fix_anatomical_gaps(im)

    steps_count = 4 if include_walk else 1
    down_imgs = [m2img(down_frame(i)) for i in range(steps_count)]
    up_imgs = [m2img(up_frame(i)) for i in range(steps_count)]
    right_imgs = [m2img(right_frame(i)) for i in range(steps_count)]
    left_imgs = [im.transpose(Image.FLIP_LEFT_RIGHT) for im in right_imgs]

    all_frames = down_imgs + up_imgs + right_imgs + left_imgs
    
    if include_walk:
        tags = [
            {"name": "Walk_Down",  "from": 0,  "to": 3,  "anim_direction": 0, "color": (80, 200, 100)},
            {"name": "Walk_Up",    "from": 4,  "to": 7,  "anim_direction": 0, "color": (80, 150, 240)},
            {"name": "Walk_Right", "from": 8,  "to": 11, "anim_direction": 0, "color": (240, 180, 60)},
            {"name": "Walk_Left",  "from": 12, "to": 15, "anim_direction": 0, "color": (240, 100, 180)},
        ]
    else:
        tags = [
            {"name": "Down",  "from": 0, "to": 0, "anim_direction": 0, "color": (100, 200, 100)},
            {"name": "Up",    "from": 1, "to": 1, "anim_direction": 0, "color": (100, 150, 240)},
            {"name": "Right", "from": 2, "to": 2, "anim_direction": 0, "color": (240, 180, 80)},
            {"name": "Left",  "from": 3, "to": 3, "anim_direction": 0, "color": (240, 100, 180)},
        ]

    return [("Hero_Main", all_frames)], tags


def generate_tileset(
    tile_size: int = 24,
    theme: str = "grass",
    cols: int = 6,
    rows: int = 2,
) -> Tuple[Image.Image, List[Image.Image]]:
    """Genera un tileset completo y seamless con variaciones orgánicas listo para TileMapLayer."""
    T = tile_size
    G0 = (32, 78, 48, 255)
    G1 = (48, 112, 64, 255)
    G2 = (68, 154, 82, 255)
    G3 = (98, 188, 105, 255)
    G4 = (145, 222, 135, 255)

    def base_tile():
        im = Image.new('RGBA', (T, T), G2)
        px = im.load()
        d_g3 = [(3, 4), (4, 4), (10, 2), (15, 8), (16, 8), (21, 14), (8, 18), (19, 21), (2, 12)]
        d_g1 = [(4, 5), (11, 3), (16, 9), (22, 15), (9, 19), (20, 22), (3, 13), (13, 14)]
        for x, y in d_g3: px[x % T, y % T] = G3
        for x, y in d_g1: px[x % T, y % T] = G1
        return im

    def blades_tile():
        im = base_tile()
        d = ImageDraw.Draw(im)
        d.line([(6, 12), (7, 9)], fill=G3); d.line([(7, 12), (8, 8)], fill=G4); d.line([(8, 12), (9, 10)], fill=G3)
        d.point([(7, 13), (8, 13)], fill=G0)
        d.line([(16, 6), (17, 3)], fill=G4); d.line([(17, 6), (18, 4)], fill=G3)
        d.point([(17, 7)], fill=G1)
        return im

    def flowers_tile():
        im = base_tile()
        d = ImageDraw.Draw(im)
        d.ellipse([5, 11, 9, 13], fill=(235, 60, 75, 255))
        d.point([(7, 12)], fill=(255, 240, 120, 255))
        d.ellipse([14, 5, 18, 7], fill=(248, 250, 255, 255))
        d.point([(16, 6)], fill=(255, 240, 120, 255))
        return im

    def daisy_tile():
        im = base_tile()
        d = ImageDraw.Draw(im)
        d.ellipse([9, 9, 14, 13], fill=(255, 215, 50, 255))
        d.point([(11, 11), (12, 11)], fill=(255, 130, 20, 255))
        d.line([(18, 17), (19, 15)], fill=G4)
        return im

    def pebble_tile():
        im = base_tile()
        d = ImageDraw.Draw(im)
        d.ellipse([11, 13, 18, 17], fill=G0)
        d.ellipse([12, 11, 17, 15], fill=(70, 75, 88, 255))
        d.ellipse([12, 11, 16, 13], fill=(145, 155, 170, 255))
        d.point([(13, 11)], fill=G4)
        return im

    def tall_tile():
        im = base_tile()
        d = ImageDraw.Draw(im)
        for x1, y1, x2, y2 in [(9,17,9,9), (10,17,11,7), (11,17,12,6), (12,17,13,7), (13,17,15,9)]:
            d.line([(x1, y1), (x2, y2)], fill=G3)
        d.point([(11, 7), (12, 6), (13, 7)], fill=G4)
        for bx in range(9, 15): d.point([(bx, 17)], fill=G0)
        return im

    def overhang_north():
        im = base_tile()
        d = ImageDraw.Draw(im)
        for x in range(T):
            d.line([(x, 0), (x, 3 + (x % 3))], fill=G4 if x % 2 == 0 else G3)
        return im

    def overhang_south():
        im = base_tile()
        d = ImageDraw.Draw(im)
        for x in range(T):
            d.line([(x, T - (2 + (x * 2) % 4)), (x, T - 1)], fill=G0)
        return im

    tile_list = [
        base_tile(), blades_tile(), flowers_tile(), daisy_tile(), pebble_tile(), tall_tile(),
        overhang_north(), overhang_south(), base_tile(), blades_tile(), flowers_tile(), daisy_tile()
    ]

    sheet = Image.new('RGBA', (cols * T, rows * T), (0, 0, 0, 0))
    for idx, t_img in enumerate(tile_list[:cols * rows]):
        r = idx // cols
        c = idx % cols
        sheet.paste(t_img, (c * T, r * T))

    return sheet, tile_list


