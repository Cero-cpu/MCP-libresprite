"""Adaptador de LibreSprite para AI Bridge (Nivel Senior Pixel Artist).

Permite:
- Dibujo de Pixel Art con precisión matemática (Bresenham clean, curvas Bézier, matrices ASCII).
- Animaciones con multicapa real (.ase) para edición profesional en LibreSprite.
- Paletas consagradas (DB32, Endesga32, Sweetie16, Pico8) y generación automática de rampas con Hue-Shifting.
- Dithering ordenado (Bayer 4x4, Checker).
- Exportación automática a .ase, .gif, spritesheet PNG y metadata JSON.
"""
from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from PIL import Image, ImageDraw

from core.adapter import BaseAdapter, BridgeError, dumps
from core.desktop import graphical_env

from .ase_format import encode_ase_multilayer, save_ase, save_ase_multilayer
from .draw_engine import (
    apply_dither_gradient,
    bezier_curve_pixels,
    bresenham_clean_line,
    parse_color,
    render_ascii_matrix,
)
from .palettes import PALETTES, create_hue_shifted_ramp

LIBRESPRITE_BIN = "/usr/bin/libresprite"


def _draw_advanced_commands(img: Image.Image, ops: list[dict]) -> None:
    draw = ImageDraw.Draw(img)
    for op in ops:
        kind = op.get("type", "pixel")
        color = parse_color(op.get("color", "#000000"))

        if kind == "pixel":
            x, y = int(op.get("x", 0)), int(op.get("y", 0))
            if 0 <= x < img.width and 0 <= y < img.height:
                img.putpixel((x, y), color)

        elif kind == "pixels":
            for pt in op.get("points", []):
                px = int(pt[0] if isinstance(pt, (list, tuple)) else pt.get("x", 0))
                py = int(pt[1] if isinstance(pt, (list, tuple)) else pt.get("y", 0))
                pt_col = parse_color(pt[2] if isinstance(pt, (list, tuple)) and len(pt) > 2 else pt.get("color", color))
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), pt_col)

        elif kind == "rect":
            x, y = int(op.get("x", 0)), int(op.get("y", 0))
            w, h = int(op.get("w", op.get("width", 1))), int(op.get("h", op.get("height", 1)))
            outline = parse_color(op["outline"]) if "outline" in op else None
            fill = color if op.get("fill", True) else None
            draw.rectangle([x, y, x + w - 1, y + h - 1], fill=fill, outline=outline)

        elif kind == "line":
            x1, y1 = int(op.get("x1", 0)), int(op.get("y1", 0))
            x2, y2 = int(op.get("x2", 0)), int(op.get("y2", 0))
            clean = op.get("clean", True)
            if clean:
                for px, py in bresenham_clean_line(x1, y1, x2, y2):
                    if 0 <= px < img.width and 0 <= py < img.height:
                        img.putpixel((px, py), color)
            else:
                draw.line([x1, y1, x2, y2], fill=color, width=int(op.get("width", 1)))

        elif kind == "curve":
            p0 = (int(op.get("x0", 0)), int(op.get("y0", 0)))
            p1 = (int(op.get("cx", 0)), int(op.get("cy", 0))) # control point
            p2 = (int(op.get("x1", 0)), int(op.get("y1", 0)))
            for px, py in bezier_curve_pixels(p0, p1, p2, steps=int(op.get("steps", 24))):
                if 0 <= px < img.width and 0 <= py < img.height:
                    img.putpixel((px, py), color)

        elif kind in ("circle", "ellipse"):
            x, y = int(op.get("x", 0)), int(op.get("y", 0))
            w = int(op.get("w", op.get("width", op.get("radius", 1) * 2)))
            h = int(op.get("h", op.get("height", w)))
            outline = parse_color(op["outline"]) if "outline" in op else None
            fill = color if op.get("fill", True) else None
            draw.ellipse([x, y, x + w - 1, y + h - 1], fill=fill, outline=outline)

        elif kind == "fill":
            x, y = op.get("x"), op.get("y")
            if x is None or y is None:
                draw.rectangle([0, 0, img.width - 1, img.height - 1], fill=color)
            else:
                ImageDraw.floodfill(img, (int(x), int(y)), color)

        elif kind == "dither":
            x, y = int(op.get("x", 0)), int(op.get("y", 0))
            w, h = int(op.get("w", op.get("width", img.width))), int(op.get("h", op.get("height", img.height)))
            c1 = parse_color(op.get("color1", color))
            c2 = parse_color(op.get("color2", [0, 0, 0, 0]))
            direction = op.get("direction", "vertical")
            pattern = op.get("pattern", "bayer")
            apply_dither_gradient(img, x, y, w, h, c1, c2, direction=direction, pattern=pattern)

        elif kind == "matrix":
            # ASCII art pixel matrix
            mx, my = int(op.get("x", 0)), int(op.get("y", 0))
            render_ascii_matrix(img, mx, my, op.get("matrix", []), op.get("palette", {}))


class Adapter(BaseAdapter):
    name = "libresprite"
    title = "LibreSprite"
    description = (
        "Herramienta profesional de Pixel Art y Animación 2D. Diseña sprites con estética senior, "
        "dithering ordenado, curvas Bézier, hue-shifting biológico y multicapa nativa .ase."
    )

    def _binary(self) -> str | None:
        return shutil.which("libresprite") or (LIBRESPRITE_BIN if Path(LIBRESPRITE_BIN).is_file() else None)

    async def status(self) -> dict:
        bin_path = self._binary()
        running_instances = []
        try:
            out = subprocess.run(["pgrep", "-f", "libresprite"], capture_output=True, text=True)
            for pid in out.stdout.splitlines():
                if pid.strip():
                    running_instances.append(int(pid.strip()))
        except Exception:
            pass

        return {
            "name": self.name,
            "title": self.title,
            "installed": bin_path is not None,
            "binary": bin_path,
            "gui_running": len(running_instances) > 0,
            "pids": running_instances,
            "palettes": list(PALETTES.keys()),
        }

    def register_tools(self, mcp) -> None:
        @mcp.tool()
        async def libresprite_status() -> str:
            """Check if LibreSprite is installed and whether the GUI application is running."""
            return dumps(await self.status())

        @mcp.tool()
        async def libresprite_palette(name_or_base_hex: str, steps: int = 5) -> str:
            """Obtain a professional pixel art palette (e.g. 'endesga32', 'dawnbringer32', 'pico8') or generate a hue-shifted ramp from a base hex color."""
            name = name_or_base_hex.lower().strip()
            if name in PALETTES:
                return dumps({"palette": name, "colors": PALETTES[name]})
            
            # Generar rampa procedural con hue-shifting
            ramp = create_hue_shifted_ramp(name_or_base_hex, steps=steps)
            hex_ramp = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, _ in ramp]
            return dumps({
                "base_color": name_or_base_hex,
                "hue_shifted_ramp": hex_ramp,
                "steps": steps
            })

        @mcp.tool()
        async def libresprite_open(file_path: Optional[str] = None) -> str:
            """Open LibreSprite GUI desktop app, optionally opening a sprite or animation file."""
            binary = self._binary()
            if not binary:
                raise BridgeError("LibreSprite no está instalado en el sistema.")

            args = [binary]
            if file_path:
                p = Path(file_path).expanduser().resolve()
                if not p.exists():
                    raise BridgeError(f"El archivo '{file_path}' no existe.")
                args.append(str(p))

            env = graphical_env()
            try:
                subprocess.Popen(
                    args,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except Exception as e:
                raise BridgeError(f"No se pudo iniciar LibreSprite: {e}")

            return dumps({
                "opened": True,
                "file": file_path,
                "message": f"LibreSprite abierto exitosamente{' con ' + file_path if file_path else ''}."
            })

        @mcp.tool()
        async def libresprite_create_sprite(
            width: int,
            height: int,
            path: str,
            operations: list[dict],
            background: Optional[str] = None,
            save_png: bool = True,
            save_ase: bool = True,
        ) -> str:
            """Create a high-precision pixel art sprite with clean lines, Bézier curves, ASCII matrices and dithering.
            
            Args:
                width: Canvas width in pixels.
                height: Canvas height in pixels.
                path: Destination path (.ase, .png).
                operations: Operations list (pixel, pixels, rect, line, curve, circle, dither, matrix, fill).
                background: Background color (default transparent).
                save_png: Save .png copy.
                save_ase: Save native .ase project.
            """
            if width <= 0 or height <= 0:
                raise BridgeError("Dimensions must be positive integers.")

            bg_color = parse_color(background) if background else (0, 0, 0, 0)
            img = Image.new("RGBA", (width, height), bg_color)

            _draw_advanced_commands(img, operations)

            base_path = Path(path).expanduser().resolve()
            base_path.parent.mkdir(parents=True, exist_ok=True)
            stem, parent = base_path.stem, base_path.parent
            saved_files = []

            if save_png or base_path.suffix.lower() == ".png":
                png_path = parent / f"{stem}.png"
                img.save(png_path)
                saved_files.append(str(png_path))

            if save_ase or base_path.suffix.lower() in (".ase", ".aseprite"):
                ase_path = parent / f"{stem}.ase"
                save_ase(ase_path, [img], duration_ms=100)
                saved_files.append(str(ase_path))

            return dumps({
                "width": width,
                "height": height,
                "operations_count": len(operations),
                "saved_files": saved_files,
            })

        @mcp.tool()
        async def libresprite_create_animation(
            width: int,
            height: int,
            path: str,
            frames: list[dict],
            duration_ms: int = 100,
            save_gif: bool = True,
            save_ase: bool = True,
            save_sheet: bool = True,
        ) -> str:
            """Create an animation sequence saving as native .ase project, animated GIF and spritesheet."""
            if not frames:
                raise BridgeError("Animation must contain at least 1 frame.")

            base_path = Path(path).expanduser().resolve()
            base_path.parent.mkdir(parents=True, exist_ok=True)
            stem, parent = base_path.stem, base_path.parent

            pil_frames: list[Image.Image] = []
            for frame_spec in frames:
                bg = frame_spec.get("background")
                bg_col = parse_color(bg) if bg else (0, 0, 0, 0)
                f_img = Image.new("RGBA", (width, height), bg_col)
                _draw_advanced_commands(f_img, frame_spec.get("operations", []))
                pil_frames.append(f_img)

            saved_files = []

            if save_ase or base_path.suffix.lower() in (".ase", ".aseprite"):
                ase_path = parent / f"{stem}.ase"
                save_ase(ase_path, pil_frames, duration_ms=duration_ms)
                saved_files.append(str(ase_path))

            if save_gif:
                gif_path = parent / f"{stem}.gif"
                pil_frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=duration_ms,
                    loop=0,
                    disposal=2,
                )
                saved_files.append(str(gif_path))

            if save_sheet:
                sheet_w = width * len(pil_frames)
                sheet_h = height
                sheet_img = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
                for i, frame in enumerate(pil_frames):
                    sheet_img.paste(frame, (i * width, 0))
                sheet_path = parent / f"{stem}_sheet.png"
                sheet_img.save(sheet_path)
                saved_files.append(str(sheet_path))

                json_meta = {
                    "frames": [
                        {
                            "frame": {"x": i * width, "y": 0, "w": width, "h": height},
                            "duration": duration_ms,
                        }
                        for i in range(len(pil_frames))
                    ],
                    "meta": {
                        "size": {"w": sheet_w, "h": sheet_h},
                        "frame_count": len(pil_frames),
                        "duration_ms": duration_ms,
                    },
                }
                meta_path = parent / f"{stem}_sheet.json"
                meta_path.write_text(dumps(json_meta))
                saved_files.append(str(meta_path))

            return dumps({
                "frames_count": len(pil_frames),
                "duration_ms": duration_ms,
                "dimensions": [width, height],
                "saved_files": saved_files,
            })

        @mcp.tool()
        async def libresprite_create_multilayer(
            width: int,
            height: int,
            path: str,
            layers: list[dict],
            duration_ms: int = 100,
            save_gif: bool = True,
            save_ase: bool = True,
            save_sheet: bool = True,
        ) -> str:
            """Create a professional multi-layered animation (e.g. Background, Body, Clothes, Highlights, FX) saved into a real multi-layer .ase project.
            
            Args:
                width: Width in pixels.
                height: Height in pixels.
                path: Output file path.
                layers: List of layers:
                    [
                      {
                        "name": "Background",
                        "frames": [ {"operations": [...]}, {"operations": [...]} ]
                      },
                      {
                        "name": "Character",
                        "frames": [ {"operations": [...]}, {"operations": [...]} ]
                      }
                    ]
                duration_ms: Frame duration in milliseconds.
            """
            if not layers:
                raise BridgeError("At least one layer is required.")

            num_frames = len(layers[0].get("frames", []))
            if num_frames == 0:
                raise BridgeError("Each layer must have at least one frame.")

            base_path = Path(path).expanduser().resolve()
            base_path.parent.mkdir(parents=True, exist_ok=True)
            stem, parent = base_path.stem, base_path.parent

            # Procesar cada capa
            processed_layers: List[tuple[str, List[Image.Image]]] = []
            for lyr in layers:
                lyr_name = lyr.get("name", "Layer")
                l_frames: List[Image.Image] = []
                for f_idx in range(num_frames):
                    f_spec = lyr["frames"][f_idx]
                    f_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                    _draw_advanced_commands(f_img, f_spec.get("operations", []))
                    l_frames.append(f_img)
                processed_layers.append((lyr_name, l_frames))

            saved_files = []

            # 1. Guardar .ase multicapa nativo
            if save_ase or base_path.suffix.lower() in (".ase", ".aseprite"):
                ase_path = parent / f"{stem}.ase"
                save_ase_multilayer(ase_path, processed_layers, duration_ms=duration_ms)
                saved_files.append(str(ase_path))

            # 2. Generar capas aplanadas compuestas para GIF y Spritesheet
            composite_frames: List[Image.Image] = []
            for f_idx in range(num_frames):
                comp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                for _, lyr_imgs in processed_layers:
                    comp.alpha_composite(lyr_imgs[f_idx])
                composite_frames.append(comp)

            if save_gif:
                gif_path = parent / f"{stem}.gif"
                composite_frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=composite_frames[1:],
                    duration=duration_ms,
                    loop=0,
                    disposal=2,
                )
                saved_files.append(str(gif_path))

            if save_sheet:
                sheet_w = width * num_frames
                sheet_h = height
                sheet_img = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
                for i, frame in enumerate(composite_frames):
                    sheet_img.paste(frame, (i * width, 0))
                sheet_path = parent / f"{stem}_sheet.png"
                sheet_img.save(sheet_path)
                saved_files.append(str(sheet_path))

            return dumps({
                "layers_count": len(processed_layers),
                "layer_names": [n for n, _ in processed_layers],
                "frames_count": num_frames,
                "dimensions": [width, height],
                "saved_files": saved_files,
            })
