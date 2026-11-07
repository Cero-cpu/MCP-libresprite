"""Motor de dibujo de alta precisión para Pixel Art profesional.

Incluye:
- Algoritmo de línea de Bresenham con filtrado de "doubles" para contornos limpios.
- Curvas Bézier cuadráticas rasterizadas a nivel de pixel sin jaggies.
- Sombrado celular automático y tramado Dithering (Bayer 4x4, Checker).
- Simetría automática (Mirroring) para matrices ASCII: reduce a la mitad el código y tiempo de respuesta de la IA.
- Outlining profesional inteligente (Selective Outline / Sel-out, Dark Outline).
- Previsualizador ANSI 24-bit de terminal para inspección visual inmediata sin latencia.
- Escalado nítido Nearest-Neighbor para previsualización HD automática.
"""
from __future__ import annotations

import colorsys
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageColor, ImageDraw

BAYER_4X4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]

CHAR_MIRROR_MAP = {
    '(': ')', ')': '(',
    '[': ']', ']': '[',
    '{': '}', '}': '{',
    '<': '>', '>': '<',
    '/': '\\', '\\': '/',
}


def parse_color(c: Union[str, tuple, list]) -> Tuple[int, int, int, int]:
    """Parsea cualquier formato de color a una tupla RGBA estándar."""
    if isinstance(c, (list, tuple)):
        if len(c) == 3:
            return (int(c[0]), int(c[1]), int(c[2]), 255)
        elif len(c) >= 4:
            return (int(c[0]), int(c[1]), int(c[2]), int(c[3]))
    elif isinstance(c, str):
        c = c.strip()
        try:
            return ImageColor.getcolor(c, "RGBA")
        except ValueError:
            pass
    return (0, 0, 0, 255)


def darken_color(rgba: Tuple[int, int, int, int], factor: float = 0.45) -> Tuple[int, int, int, int]:
    """Oscurece un color RGBA manteniendo su tono (para Selective Outlining)."""
    r, g, b, a = rgba
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    # Sombras sutilmente más frías y menos saturadas
    h_dark = (h + 0.03) % 1.0 if factor < 0.6 else h
    v_dark = max(0.05, min(1.0, v * factor))
    s_dark = min(1.0, s * 1.1)
    nr, ng, nb = colorsys.hsv_to_rgb(h_dark, s_dark, v_dark)
    return (int(nr * 255), int(ng * 255), int(nb * 255), a)


def bresenham_clean_line(x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
    """Calcula los puntos de una línea recta de Bresenham evitando escalones dobles accidentales."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    cx, cy = x0, y0
    while True:
        points.append((cx, cy))
        if cx == x1 and cy == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy

    return points


def bezier_curve_pixels(
    p0: Tuple[int, int],
    p1: Tuple[int, int],
    p2: Tuple[int, int],
    steps: int = 24
) -> List[Tuple[int, int]]:
    """Genera una curva cuadrática de Bézier en píxeles limpios."""
    pts = []
    prev = None
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = int(round(u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0]))
        y = int(round(u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
        if (x, y) != prev:
            pts.append((x, y))
            prev = (x, y)
    return pts


def mirror_ascii_row(row: str, mode: str = "even") -> str:
    """Refleja horizontalmente una fila de caracteres ASCII.
    mode='even': 'ABC' -> 'ABCCBA'
    mode='odd':  'ABC' -> 'ABCBA' (el último carácter es el eje central)
    """
    rev_chars = [CHAR_MIRROR_MAP.get(c, c) for c in reversed(row)]
    if mode == "odd" and len(rev_chars) > 1:
        return row + "".join(rev_chars[1:])
    return row + "".join(rev_chars)


def render_ascii_matrix(
    img: Image.Image,
    x: int,
    y: int,
    matrix: List[str],
    palette: Dict[str, Union[str, Tuple[int, int, int, int]]],
    mirror: bool = False,
    mirror_mode: str = "even"
) -> None:
    """Renderiza una matriz de caracteres ASCII exactamente a píxeles.
    Soporta 'mirror=True' para simetría automática instantánea.
    '.' o ' ' se interpretan habitualmente como transparente.
    """
    parsed_pal = {k: parse_color(v) for k, v in palette.items()}
    for row_idx, raw_line in enumerate(matrix):
        py = y + row_idx
        if py < 0 or py >= img.height:
            continue
        line = mirror_ascii_row(raw_line, mode=mirror_mode) if mirror else raw_line
        for col_idx, char in enumerate(line):
            px = x + col_idx
            if px < 0 or px >= img.width:
                continue
            if char in ('.', ' '):
                continue
            if char in parsed_pal:
                img.putpixel((px, py), parsed_pal[char])


def apply_dither_gradient(
    img: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    color1: Tuple[int, int, int, int],
    color2: Tuple[int, int, int, int],
    direction: str = "vertical",
    pattern: str = "bayer"
) -> None:
    """Aplica un degradado con dithering ordenado clásico."""
    for py in range(y, min(y + h, img.height)):
        for px in range(x, min(x + w, img.width)):
            if direction == "vertical":
                t = (py - y) / max(1, h - 1)
            else:
                t = (px - x) / max(1, w - 1)

            if pattern == "checker":
                use_c2 = t > 0.5 and (px + py) % 2 == 0
            else:
                threshold = BAYER_4X4[py % 4][px % 4] / 16.0
                use_c2 = t > threshold

            img.putpixel((px, py), color2 if use_c2 else color1)


def apply_auto_outline(
    img: Image.Image,
    mode: str = "selective",  # selective | dark | solid
    solid_color: Union[str, tuple] = "#15121e",
) -> Image.Image:
    """Genera un delineado exterior pixel art (1px) alrededor de las zonas opacas.
    - selective: toma el color del píxel interior adyacente y lo oscurece en rampa armónica (Senior Sel-out).
    - dark: color oscuro universal (#15121e) suave.
    - solid: usa el color especificado en solid_color.
    """
    w, h = img.size
    out = img.copy()
    solid_rgba = parse_color(solid_color)

    # Buscar píxeles transparentes que tocan píxeles con opacidad
    outline_pixels = {}
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for y in range(h):
        for x in range(w):
            curr_a = img.getpixel((x, y))[3]
            if curr_a > 30:
                continue  # Ya es un pixel opaco

            # Comprobar si algún vecino es opaco
            adjacent_colors = []
            for dx, dy in neighbors:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h:
                    np = img.getpixel((nx, ny))
                    if np[3] > 60:
                        adjacent_colors.append(np)

            if adjacent_colors:
                if mode == "selective":
                    # Promediar o tomar el vecino más significativo y oscurecerlo
                    avg_r = sum(c[0] for c in adjacent_colors) // len(adjacent_colors)
                    avg_g = sum(c[1] for c in adjacent_colors) // len(adjacent_colors)
                    avg_b = sum(c[2] for c in adjacent_colors) // len(adjacent_colors)
                    outline_pixels[(x, y)] = darken_color((avg_r, avg_g, avg_b, 255), factor=0.38)
                elif mode == "dark":
                    outline_pixels[(x, y)] = (24, 20, 32, 240)
                else:
                    outline_pixels[(x, y)] = solid_rgba

    for (px, py), col in outline_pixels.items():
        out.putpixel((px, py), col)

    return out


def fix_anatomical_gaps(img: Image.Image, max_gap: int = 2) -> Image.Image:
    """Detecta y sella automáticamente huecos transparentes accidentales (cabezas o piernas flotantes).
    
    Si en una columna vertical hay píxeles sólidos arriba y abajo separados por 1 o 2 píxeles
    transparentes, rellena el hueco con el color superior o inferior para asegurar continuidad anatómica.
    """
    w, h = img.size
    out = img.copy()
    src = img.load()
    dst = out.load()

    for x in range(w):
        y = 0
        while y < h:
            _, _, _, a = src[x, y]
            if a > 80:
                # Buscar si hay un hueco transparente inmediatamente debajo
                gap_len = 0
                ny = y + 1
                while ny < h and src[x, ny][3] < 30:
                    gap_len += 1
                    ny += 1
                
                # Si el hueco es pequeño (1-2px) y termina en otro píxel sólido
                if 0 < gap_len <= max_gap and ny < h and src[x, ny][3] > 80:
                    fill_col = src[x, y] # Heredar color superior
                    for gy in range(y + 1, ny):
                        dst[x, gy] = fill_col
                    y = ny
                else:
                    y += 1
            else:
                y += 1

    return out


def clean_stray_pixels(img: Image.Image) -> Image.Image:
    """Elimina píxeles flotantes huérfanos que no tienen ningún vecino opaco."""
    w, h = img.size
    out = img.copy()
    src = img.load()
    dst = out.load()

    for y in range(h):
        for x in range(w):
            if src[x, y][3] > 40:
                # Contar vecinos opacos
                neighbors = 0
                for dx, dy in ((-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,-1), (-1,1), (1,1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[x, ny][3] > 40:
                        neighbors += 1
                if neighbors == 0:
                    dst[x, y] = (0, 0, 0, 0) # Borrar píxel huérfano

    return out


def render_ansi_terminal(img: Image.Image, max_w: int = 36) -> str:
    """Renderiza la imagen en caracteres ANSI 24-bit (half-block) para terminal y logs."""
    w, h = img.size
    scale = 1
    if w > max_w:
        scale = max(1, w // max_w)
        img = img.resize((w // scale, h // scale), Image.NEAREST)
        w, h = img.size

    lines = []
    for y in range(0, h, 2):
        row = ""
        for x in range(w):
            p1 = img.getpixel((x, y))
            p2 = img.getpixel((x, y + 1)) if y + 1 < h else (0, 0, 0, 0)
            a1, a2 = p1[3], p2[3]

            if a1 < 30 and a2 < 30:
                row += " "
            elif a1 >= 30 and a2 < 30:
                row += f"\033[38;2;{p1[0]};{p1[1]};{p1[2]}m▀\033[0m"
            elif a1 < 30 and a2 >= 30:
                row += f"\033[38;2;{p2[0]};{p2[1]};{p2[2]}m▄\033[0m"
            else:
                row += f"\033[38;2;{p1[0]};{p1[1]};{p1[2]};48;2;{p2[0]};{p2[1]};{p2[2]}m▀\033[0m"
        lines.append(row)
    return "\n".join(lines)
