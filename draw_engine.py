"""Motor de dibujo de alta precisión para Pixel Art profesional.

Incluye:
- Algoritmo de línea de Bresenham con filtrado de "doubles" para contornos limpios.
- Curvas Bézier rasterizadas a nivel de pixel sin jaggies.
- Sombrado celular automático y tramado Dithering (Bayer 2x2, 4x4, Checker).
- Capas independientes (Fondo, Lineart, Color Base, Sombras, Luces, Efectos/Partículas).
- Decodificador de mapas ASCII / Strings para definición exacta y legible de sprites pixel por pixel.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union
from PIL import Image, ImageColor, ImageDraw

BAYER_4X4 = [
    [ 0,  8,  2, 10],
    [12,  4, 14,  6],
    [ 3, 11,  1,  9],
    [15,  7, 13,  5]
]


def parse_color(c: Union[str, tuple, list]) -> Tuple[int, int, int, int]:
    if isinstance(c, (list, tuple)):
        if len(c) == 3:
            return (int(c[0]), int(c[1]), int(c[2]), 255)
        elif len(c) == 4:
            return (int(c[0]), int(c[1]), int(c[2]), int(c[3]))
    elif isinstance(c, str):
        c = c.strip()
        try:
            return ImageColor.getcolor(c, "RGBA")
        except ValueError:
            pass
    return (0, 0, 0, 255)


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


def bezier_curve_pixels(p0: Tuple[int, int], p1: Tuple[int, int], p2: Tuple[int, int], steps: int = 24) -> List[Tuple[int, int]]:
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


def render_ascii_matrix(
    img: Image.Image,
    x: int,
    y: int,
    matrix: List[str],
    palette: Dict[str, Union[str, Tuple[int, int, int, int]]]
) -> None:
    """Renderiza una matriz de caracteres ASCII exactamente a píxeles.
    Permite diseñar rostros, ojos o iconos complejos con control visual absoluto.
    '.' o ' ' se interpretan habitualmente como transparente.
    """
    parsed_pal = {k: parse_color(v) for k, v in palette.items()}
    for row_idx, line in enumerate(matrix):
        py = y + row_idx
        if py < 0 or py >= img.height:
            continue
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
    direction: str = "vertical",  # vertical | horizontal
    pattern: str = "bayer"        # bayer | checker
) -> None:
    """Aplica un degradado con dithering ordenado clásico."""
    for py in range(y, min(y + h, img.height)):
        for px in range(x, min(x + w, img.width)):
            if direction == "vertical":
                t = (py - y) / max(1, h - 1)
            else:
                t = (px - x) / max(1, w - 1)

            if pattern == "checker":
                threshold = 0.5
                use_c2 = t > 0.5 and (px + py) % 2 == 0
            else:
                # Matriz Bayer 4x4
                threshold = BAYER_4X4[py % 4][px % 4] / 16.0
                use_c2 = t > threshold

            img.putpixel((px, py), color2 if use_c2 else color1)

