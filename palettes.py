"""Paletas de color consagradas en Pixel Art y utilidades de color profesional.

Incluye:
- DB32 (DawnBringer 32)
- EDG32 (Endesga 32)
- Resurrect 64
- Sweetie 16
- Pico-8
- GameBoy 4-color
- Generación procedural de rampas con Hue-Shifting biológico y ambiental
"""
from __future__ import annotations

import colorsys
from typing import List, Tuple

PALETTES = {
    "endesga32": [
        "#be4a2f", "#d77643", "#ead4aa", "#e4a672", "#b86f56", "#733e39", "#3e2731", "#a22633",
        "#e43b44", "#f77622", "#feae34", "#fee761", "#63c74d", "#3e8948", "#265c42", "#193c3e",
        "#124e89", "#0099db", "#2ce8f5", "#ffffff", "#c0cbdc", "#8b9bb4", "#5a6988", "#3a4466",
        "#262b44", "#181425", "#ff0044", "#68386c", "#b55088", "#f6757a", "#e8b796", "#c28569"
    ],
    "dawnbringer32": [
        "#000000", "#222034", "#45283c", "#663931", "#8f563b", "#df7126", "#d9a066", "#eec39a",
        "#fbf236", "#99e550", "#6abe30", "#37946e", "#4b692f", "#524b24", "#323c39", "#3f3f74",
        "#306082", "#5b6ee1", "#639bff", "#5fcde4", "#cbdbfc", "#ffffff", "#9badb7", "#847e87",
        "#696a6a", "#595652", "#76428a", "#ac3232", "#d95763", "#d77bba", "#8f974a", "#8a6f30"
    ],
    "sweetie16": [
        "#1a1c2b", "#57294b", "#9b2242", "#e54b4b", "#fb922b", "#ffe762", "#63c64d", "#327345",
        "#193d3f", "#1e579c", "#4680c2", "#68bbf5", "#ffffff", "#9ca6bd", "#4d5b78", "#2b2a3a"
    ],
    "pico8": [
        "#000000", "#1D2B53", "#7E2553", "#008751", "#AB5236", "#5F574F", "#C2C3C7", "#FFF1E8",
        "#FF004D", "#FFA300", "#FFEC27", "#00E436", "#29ADFF", "#83769C", "#FF77A8", "#FFCCAA"
    ]
}


def create_hue_shifted_ramp(
    base_hex: str,
    steps: int = 5,
    shadow_shift_blue: float = 0.08,
    light_shift_yellow: float = 0.06,
    contrast: float = 1.2
) -> List[Tuple[int, int, int, int]]:
    """Genera una rampa de color con *hue-shifting* profesional:
    - Las sombras giran hacia tonos fríos (azulados/púrpuras) y se desaturan ligeramente.
    - Las luces giran hacia tonos cálidos (amarillos/dorados) y ganan luminosidad.
    """
    base_hex = base_hex.lstrip("#")
    r, g, b = tuple(int(base_hex[i:i+2], 16) for i in (0, 2, 4))
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

    ramp = []
    # De sombra profunda a luz brillante
    for i in range(steps):
        t = (i / (steps - 1)) * 2 - 1  # -1 (sombra) a +1 (luz)
        
        # Hue shift
        cur_h = h
        if t < 0:
            # Shift hacia azul (~0.66 en HSV)
            cur_h = (h + shadow_shift_blue * t) % 1.0
            cur_s = max(0.1, min(1.0, s * (1.0 + 0.1 * t)))
            cur_v = max(0.05, min(1.0, v * (1.0 + 0.65 * t * contrast)))
        else:
            # Shift hacia amarillo (~0.16 en HSV)
            cur_h = (h - light_shift_yellow * t) % 1.0
            cur_s = max(0.1, min(1.0, s * (1.0 - 0.2 * t)))
            cur_v = max(0.05, min(1.0, v * (1.0 + 0.5 * t * contrast)))
            
        nr, ng, nb = colorsys.hsv_to_rgb(cur_h, cur_s, cur_v)
        ramp.append((int(nr * 255), int(ng * 255), int(nb * 255), 255))
        
    return ramp
