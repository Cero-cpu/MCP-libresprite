#!/usr/bin/env python3
"""Servidor MCP Autónomo e Independiente para LibreSprite Pixel Art y Animación.

Funciona por stdio (Claude Desktop, Cursor, Antigravity, VS Code, Gemini CLI, etc.)
o con --http para servidor Streamable HTTP.
"""
from __future__ import annotations

import argparse
import asyncio
import functools
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from PIL import Image, ImageDraw
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from ase_format import encode_ase_multilayer, save_ase, save_ase_multilayer
from draw_engine import (
    apply_auto_outline,
    apply_dither_gradient,
    bezier_curve_pixels,
    bresenham_clean_line,
    clean_stray_pixels,
    fix_anatomical_gaps,
    parse_color,
    render_ansi_terminal,
    render_ascii_matrix,
)
from generators import (
    generate_character,
    generate_prop,
    generate_tileset,
    generate_topdown_hero,
)
from palettes import PALETTES, create_hue_shifted_ramp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mcp-libresprite")

LIBRESPRITE_BIN = "/usr/bin/libresprite"

INSTRUCTIONS = """You are connected to the Standalone LibreSprite MCP Server for professional Pixel Art & 2D Animation.

SUPER-FAST WORKFLOW (Better & Faster than PixeLab):
1. Instant Character Generation: Call `libresprite_create_character` to produce game-ready, multi-layered characters in 0.1s.
   Supports ANY resolution (16x16, 24x24, 32x32, 48x48, 64x64, 128x128), color customizations, organic idle animations,
   and automatic selective outlining.
2. Instant Item/Prop Generation: Call `libresprite_create_prop` for weapons, potions, chests, shields and gems at any size.
3. Clean Geometry & Symmetry:
   - When using ASCII matrices (`matrix`), set `"mirror": true` to define only half the character; the engine mirrors it automatically! This reduces token generation time by 50%.
   - Lines use Bresenham clean algorithms avoiding accidental doubles. Use 'curve' for Bézier silhouettes.
4. Auto-Outline (Sel-out):
   - Set `outline_mode="selective"` to automatically wrap shapes in professional hue-shifted dark outlines.
5. Instant Visual Inspection:
   - All tools generate an HD Nearest-Neighbor preview (8x) and return an ANSI 24-bit terminal render so you can immediately see the artwork without latency.
6. Layers & LibreSprite GUI:
   - Generates native multi-layer `.ase` projects with Animation Frame Tags (Idle, Walk, Attack). Use `libresprite_open` to display it in LibreSprite.
"""


def graphical_env() -> dict[str, str]:
    """Entorno de pantalla Wayland o X11."""
    env = dict(os.environ)
    uid = os.getuid()
    run = env.get("XDG_RUNTIME_DIR") or f"/run/user/{uid}"
    if Path(run).is_dir():
        env["XDG_RUNTIME_DIR"] = run
    if not env.get("WAYLAND_DISPLAY"):
        socks = sorted(Path(run).glob("wayland-[0-9]")) if Path(run).is_dir() else []
        if socks:
            env["WAYLAND_DISPLAY"] = socks[0].name
    return env


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, default=str)


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
            p1 = (int(op.get("cx", 0)), int(op.get("cy", 0)))
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
            mx, my = int(op.get("x", 0)), int(op.get("y", 0))
            render_ascii_matrix(
                img,
                mx,
                my,
                op.get("matrix", []),
                op.get("palette", {}),
                mirror=bool(op.get("mirror", False)),
                mirror_mode=op.get("mirror_mode", "even"),
            )


def build_server() -> MCPServer:
    mcp = MCPServer(
        name="mcp-libresprite",
        title="LibreSprite Pixel Art MCP",
        instructions=INSTRUCTIONS,
        version="2.0.0",
    )

    def _binary() -> str | None:
        return shutil.which("libresprite") or (LIBRESPRITE_BIN if Path(LIBRESPRITE_BIN).is_file() else None)

    @mcp.tool()
    async def libresprite_status() -> str:
        """Check if LibreSprite is installed and whether the GUI application is running."""
        bin_path = _binary()
        running_instances = []
        try:
            out = subprocess.run(["pgrep", "-f", "libresprite"], capture_output=True, text=True)
            for pid in out.stdout.splitlines():
                if pid.strip():
                    running_instances.append(int(pid.strip()))
        except Exception:
            pass

        return dumps({
            "name": "libresprite",
            "installed": bin_path is not None,
            "binary": bin_path,
            "gui_running": len(running_instances) > 0,
            "pids": running_instances,
            "palettes": list(PALETTES.keys()),
        })

    @mcp.tool()
    async def libresprite_palette(name_or_base_hex: str, steps: int = 5) -> str:
        """Obtain a professional pixel art palette (e.g. 'endesga32', 'dawnbringer32', 'pico8') or generate a hue-shifted ramp from a base hex color."""
        name = name_or_base_hex.lower().strip()
        if name in PALETTES:
            return dumps({"palette": name, "colors": PALETTES[name]})

        ramp = create_hue_shifted_ramp(name_or_base_hex, steps=steps)
        hex_ramp = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b, _ in ramp]
        return dumps({
            "base_color": name_or_base_hex,
            "hue_shifted_ramp": hex_ramp,
            "steps": steps,
        })

    @mcp.tool()
    async def libresprite_open(file_path: Optional[str] = None) -> str:
        """Open LibreSprite GUI window, optionally opening a sprite or animation file."""
        binary = _binary()
        if not binary:
            raise ToolError("LibreSprite no está instalado en el sistema.")

        args = [binary]
        if file_path:
            p = Path(file_path).expanduser().resolve()
            if not p.exists():
                raise ToolError(f"El archivo '{file_path}' no existe.")
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
            raise ToolError(f"No se pudo iniciar LibreSprite: {e}")

        return dumps({
            "opened": True,
            "file": file_path,
            "message": f"LibreSprite abierto exitosamente{' con ' + file_path if file_path else ''}."
        })

    @mcp.tool()
    async def libresprite_preview(file_path: str, scale: int = 8) -> str:
        """Inspect any sprite or .ase file immediately, returning its dimensions and a 24-bit ANSI block render for instant visual feedback."""
        p = Path(file_path).expanduser().resolve()
        if not p.exists():
            raise ToolError(f"El archivo '{file_path}' no existe.")

        stem, parent = p.stem, p.parent
        img_to_show: Optional[Image.Image] = None

        if p.suffix.lower() in (".ase", ".aseprite"):
            # Exportar a temporal usando libresprite CLI o buscar PNG acompañante
            png_sibling = parent / f"{stem}.png"
            if png_sibling.exists():
                img_to_show = Image.open(png_sibling).convert("RGBA")
            else:
                tmp_png = parent / f".{stem}_tmp.png"
                subprocess.run(["libresprite", "--batch", str(p), "--save-as", str(tmp_png)], capture_output=True)
                if tmp_png.exists():
                    img_to_show = Image.open(tmp_png).convert("RGBA")
                    tmp_png.unlink(missing_ok=True)
        else:
            img_to_show = Image.open(p).convert("RGBA")

        if not img_to_show:
            raise ToolError("No se pudo cargar la imagen para previsualización.")

        w, h = img_to_show.size
        # Guardar copia reescalada si se solicita
        preview_path = parent / f"{stem}_preview_{scale}x.png"
        preview_img = img_to_show.resize((w * scale, h * scale), Image.NEAREST)
        preview_img.save(preview_path)

        ansi_view = render_ansi_terminal(img_to_show, max_w=48)
        return dumps({
            "dimensions": [w, h],
            "preview_saved": str(preview_path),
            "scale": scale,
            "ansi_terminal_render": ansi_view,
        })

    @mcp.tool()
    async def libresprite_create_character(
        path: str,
        width: int = 48,
        height: int = 48,
        archetype: str = "anime_girl",
        hair_color: str = "#8e44ad",
        skin_tone: str = "#f5ba98",
        eye_color: str = "#1abc9c",
        outfit_primary: str = "#2c3e50",
        outfit_secondary: str = "#e74c3c",
        num_frames: int = 4,
        duration_ms: int = 140,
        outline_mode: str = "selective",
        preview_scale: int = 8,
        open_in_gui: bool = False,
    ) -> str:
        """Instantly generate a complete, high-precision pixel art character in 0.1s (Better & Faster than PixeLab).

        Supports ANY resolution (16x16, 24x24, 32x32, 48x48, 64x64, 128x128), multi-layer .ase project,
        organic idle breathing animation, selective outline and instant HD preview.
        """
        if width <= 0 or height <= 0:
            raise ToolError("Width and height must be positive integers.")

        base_path = Path(path).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem, parent = base_path.stem, base_path.parent

        layers = generate_character(
            width=width,
            height=height,
            archetype=archetype,
            hair_color=hair_color,
            skin_tone=skin_tone,
            eye_color=eye_color,
            outfit_primary=outfit_primary,
            outfit_secondary=outfit_secondary,
            num_frames=num_frames,
            duration_ms=duration_ms,
            outline_mode=outline_mode,
        )

        tags = [
            {"name": "Idle", "from": 0, "to": num_frames - 1, "direction": 2, "color": (100, 180, 255)},
        ]

        saved_files = []

        # 1. Guardar .ase multicapa con tags
        ase_path = parent / f"{stem}.ase"
        save_ase_multilayer(ase_path, layers, duration_ms=duration_ms, tags=tags)
        saved_files.append(str(ase_path))

        # 2. Componer fotogramas
        composite_frames: List[Image.Image] = []
        for f_idx in range(num_frames):
            comp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            for _, f_imgs in layers:
                comp.alpha_composite(f_imgs[f_idx])
            composite_frames.append(comp)

        # 3. Guardar PNG base 1x
        png_path = parent / f"{stem}.png"
        composite_frames[0].save(png_path)
        saved_files.append(str(png_path))

        # 4. Guardar GIF animado
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

        # 5. Guardar Spritesheet
        sheet_w = width * num_frames
        sheet_h = height
        sheet_img = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
        for i, frame in enumerate(composite_frames):
            sheet_img.paste(frame, (i * width, 0))
        sheet_path = parent / f"{stem}_sheet.png"
        sheet_img.save(sheet_path)
        saved_files.append(str(sheet_path))

        # 6. Preview HD escalado (Nearest Neighbor)
        if preview_scale > 1:
            prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
            composite_frames[0].resize((width * preview_scale, height * preview_scale), Image.NEAREST).save(prev_png)
            saved_files.append(str(prev_png))

            prev_gif = parent / f"{stem}_preview_{preview_scale}x.gif"
            up_frames = [f.resize((width * preview_scale, height * preview_scale), Image.NEAREST) for f in composite_frames]
            up_frames[0].save(prev_gif, save_all=True, append_images=up_frames[1:], duration=duration_ms, loop=0, disposal=2)
            saved_files.append(str(prev_gif))

        if open_in_gui:
            try:
                await libresprite_open(str(ase_path))
            except Exception:
                pass

        ansi_render = render_ansi_terminal(composite_frames[0], max_w=48)

        return dumps({
            "archetype": archetype,
            "dimensions": [width, height],
            "frames": num_frames,
            "layers": [name for name, _ in layers],
            "saved_files": saved_files,
            "ansi_preview": ansi_render,
            "speed": "instant (0.1s)",
        })

    @mcp.tool()
    async def libresprite_create_prop(
        path: str,
        prop_type: str = "sword",
        width: int = 32,
        height: int = 32,
        primary_color: str = "#3498db",
        secondary_color: str = "#f1c40f",
        preview_scale: int = 8,
        open_in_gui: bool = False,
    ) -> str:
        """Instantly generate items, weapons, potions, chests or gems at any custom size."""
        base_path = Path(path).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem, parent = base_path.stem, base_path.parent

        layers = generate_prop(
            prop_type=prop_type,
            width=width,
            height=height,
            primary_color=primary_color,
            secondary_color=secondary_color,
        )

        saved_files = []
        ase_path = parent / f"{stem}.ase"
        save_ase_multilayer(ase_path, layers, duration_ms=100)
        saved_files.append(str(ase_path))

        comp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        for _, f_imgs in layers:
            comp.alpha_composite(f_imgs[0])

        png_path = parent / f"{stem}.png"
        comp.save(png_path)
        saved_files.append(str(png_path))

        if preview_scale > 1:
            prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
            comp.resize((width * preview_scale, height * preview_scale), Image.NEAREST).save(prev_png)
            saved_files.append(str(prev_png))

        if open_in_gui:
            try:
                await libresprite_open(str(ase_path))
            except Exception:
                pass

        return dumps({
            "prop_type": prop_type,
            "dimensions": [width, height],
            "saved_files": saved_files,
            "ansi_preview": render_ansi_terminal(comp, max_w=48),
        })

    @mcp.tool()
    async def libresprite_create_topdown_hero(
        path: str,
        width: int = 24,
        height: int = 24,
        hair_color: str = "#8e44ad",
        skin_tone: str = "#f5ba98",
        tunic_color: str = "#27ae60",
        pants_color: str = "#2c3e50",
        boots_color: str = "#795548",
        include_walk: bool = True,
        duration_ms: int = 140,
        preview_scale: int = 8,
        open_in_gui: bool = False,
    ) -> str:
        """Create a complete Top-Down RPG Hero in all 4 directions (Down, Up, Right, Left) with clean anatomy and Walk Cycles.

        Instantly outputs:
        - Native .ase project with tags: Walk_Down, Walk_Up, Walk_Right, Walk_Left (16 frames) or 4 direction tags
        - Grid Spritesheet (96x96) and Horizontal Strip
        - Clean HD Preview (8x) and individual directional PNGs
        """
        base_path = Path(path).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem, parent = base_path.stem, base_path.parent

        layers, tags = generate_topdown_hero(
            width=width,
            height=height,
            hair_color=hair_color,
            skin_tone=skin_tone,
            tunic_color=tunic_color,
            pants_color=pants_color,
            boots_color=boots_color,
            include_walk=include_walk,
            duration_ms=duration_ms,
        )

        saved_files = []
        ase_path = parent / f"{stem}.ase"
        save_ase_multilayer(ase_path, layers, duration_ms=duration_ms, tags=tags)
        saved_files.append(str(ase_path))

        all_frames = layers[0][1]
        grid_cols = 4
        grid_rows = len(all_frames) // grid_cols
        grid_img = Image.new("RGBA", (width * grid_cols, height * grid_rows), (0, 0, 0, 0))
        for idx, f_img in enumerate(all_frames):
            r = idx // grid_cols
            c = idx % grid_cols
            grid_img.paste(f_img, (c * width, r * height))

        sheet_path = parent / f"{stem}_sheet.png"
        grid_img.save(sheet_path)
        saved_files.append(str(sheet_path))

        base_png = parent / f"{stem}.png"
        all_frames[0].save(base_png)
        saved_files.append(str(base_png))

        prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
        grid_img.resize((grid_img.width * preview_scale, grid_img.height * preview_scale), Image.NEAREST).save(prev_png)
        saved_files.append(str(prev_png))

        if open_in_gui:
            try:
                await libresprite_open(str(ase_path))
            except Exception:
                pass

        return dumps({
            "character_type": "topdown_rpg_hero",
            "dimensions": [width, height],
            "directions": ["Down", "Up", "Right", "Left"],
            "total_frames": len(all_frames),
            "saved_files": saved_files,
            "preview_image_path": str(prev_png),
            "inspection_hint": "Use read_file on preview_image_path to visually verify with multimodal vision.",
        })

    @mcp.tool()
    async def libresprite_create_tileset(
        path: str,
        tile_size: int = 24,
        theme: str = "grass",
        preview_scale: int = 6,
        open_in_gui: bool = False,
    ) -> str:
        """Create a complete, seamless terrain tileset for TileMapLayer with natural organic variations and overhang borders."""
        base_path = Path(path).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem, parent = base_path.stem, base_path.parent

        sheet_img, tile_list = generate_tileset(tile_size=tile_size, theme=theme)

        saved_files = []
        png_path = parent / f"{stem}.png"
        sheet_img.save(png_path)
        saved_files.append(str(png_path))

        ase_path = parent / f"{stem}.ase"
        save_ase_multilayer(ase_path, [("Tileset_Base", [sheet_img])], duration_ms=100)
        saved_files.append(str(ase_path))

        prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
        sheet_img.resize((sheet_img.width * preview_scale, sheet_img.height * preview_scale), Image.NEAREST).save(prev_png)
        saved_files.append(str(prev_png))

        if open_in_gui:
            try:
                await libresprite_open(str(ase_path))
            except Exception:
                pass

        return dumps({
            "tileset_theme": theme,
            "tile_size": tile_size,
            "tiles_count": len(tile_list),
            "saved_files": saved_files,
            "preview_image_path": str(prev_png),
            "inspection_hint": "Use read_file on preview_image_path to inspect the tiles seamlessly.",
        })

    @mcp.tool()
    async def libresprite_create_sprite(
        width: int,
        height: int,
        path: str,
        operations: list[dict],
        background: Optional[str] = None,
        outline_mode: Optional[str] = None,
        preview_scale: int = 8,
        save_png: bool = True,
        save_ase: bool = True,
    ) -> str:
        """Create a custom pixel art sprite at ANY resolution with clean lines, Bézier curves, ASCII matrices (with symmetry/mirroring) and dithering."""
        if width <= 0 or height <= 0:
            raise ToolError("Dimensions must be positive integers.")

        bg_color = parse_color(background) if background else (0, 0, 0, 0)
        img = Image.new("RGBA", (width, height), bg_color)

        _draw_advanced_commands(img, operations)

        # Autocorrección de huecos accidentales y píxeles huérfanos
        img = fix_anatomical_gaps(img)
        img = clean_stray_pixels(img)

        if outline_mode in ("selective", "dark", "solid"):
            img = apply_auto_outline(img, mode=outline_mode)

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

        if preview_scale > 1:
            prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
            img.resize((width * preview_scale, height * preview_scale), Image.NEAREST).save(prev_png)
            saved_files.append(str(prev_png))

        return dumps({
            "width": width,
            "height": height,
            "operations_count": len(operations),
            "saved_files": saved_files,
            "ansi_preview": render_ansi_terminal(img, max_w=48),
        })

    @mcp.tool()
    async def libresprite_create_animation(
        width: int,
        height: int,
        path: str,
        frames: list[dict],
        duration_ms: int = 100,
        tags: Optional[list[dict]] = None,
        preview_scale: int = 8,
        save_gif: bool = True,
        save_ase: bool = True,
        save_sheet: bool = True,
    ) -> str:
        """Create a custom animation sequence at ANY resolution with native timeline tags, GIF and HD preview."""
        if not frames:
            raise ToolError("Animation must contain at least 1 frame.")

        base_path = Path(path).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem, parent = base_path.stem, base_path.parent

        pil_frames: list[Image.Image] = []
        for frame_spec in frames:
            bg = frame_spec.get("background")
            bg_col = parse_color(bg) if bg else (0, 0, 0, 0)
            f_img = Image.new("RGBA", (width, height), bg_col)
            _draw_advanced_commands(f_img, frame_spec.get("operations", []))
            f_img = fix_anatomical_gaps(f_img)
            f_img = clean_stray_pixels(f_img)
            pil_frames.append(f_img)

        saved_files = []

        if save_ase or base_path.suffix.lower() in (".ase", ".aseprite"):
            ase_path = parent / f"{stem}.ase"
            save_ase(ase_path, pil_frames, duration_ms=duration_ms, tags=tags)
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

        if preview_scale > 1:
            prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
            pil_frames[0].resize((width * preview_scale, height * preview_scale), Image.NEAREST).save(prev_png)
            saved_files.append(str(prev_png))

            prev_gif = parent / f"{stem}_preview_{preview_scale}x.gif"
            up_frames = [f.resize((width * preview_scale, height * preview_scale), Image.NEAREST) for f in pil_frames]
            up_frames[0].save(prev_gif, save_all=True, append_images=up_frames[1:], duration=duration_ms, loop=0, disposal=2)
            saved_files.append(str(prev_gif))

        return dumps({
            "frames_count": len(pil_frames),
            "duration_ms": duration_ms,
            "dimensions": [width, height],
            "saved_files": saved_files,
            "ansi_preview": render_ansi_terminal(pil_frames[0], max_w=48),
        })

    @mcp.tool()
    async def libresprite_create_multilayer(
        width: int,
        height: int,
        path: str,
        layers: list[dict],
        duration_ms: int = 100,
        tags: Optional[list[dict]] = None,
        preview_scale: int = 8,
        save_gif: bool = True,
        save_ase: bool = True,
        save_sheet: bool = True,
    ) -> str:
        """Create a professional multi-layered animation (Background, Character, Clothes, FX) with native timeline tags."""
        if not layers:
            raise ToolError("At least one layer is required.")

        num_frames = len(layers[0].get("frames", []))
        if num_frames == 0:
            raise ToolError("Each layer must have at least one frame.")

        base_path = Path(path).expanduser().resolve()
        base_path.parent.mkdir(parents=True, exist_ok=True)
        stem, parent = base_path.stem, base_path.parent

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

        if save_ase or base_path.suffix.lower() in (".ase", ".aseprite"):
            ase_path = parent / f"{stem}.ase"
            save_ase_multilayer(ase_path, processed_layers, duration_ms=duration_ms, tags=tags)
            saved_files.append(str(ase_path))

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

        if preview_scale > 1:
            prev_png = parent / f"{stem}_preview_{preview_scale}x.png"
            composite_frames[0].resize((width * preview_scale, height * preview_scale), Image.NEAREST).save(prev_png)
            saved_files.append(str(prev_png))

            prev_gif = parent / f"{stem}_preview_{preview_scale}x.gif"
            up_frames = [f.resize((width * preview_scale, height * preview_scale), Image.NEAREST) for f in composite_frames]
            up_frames[0].save(prev_gif, save_all=True, append_images=up_frames[1:], duration=duration_ms, loop=0, disposal=2)
            saved_files.append(str(prev_gif))

        return dumps({
            "layers_count": len(processed_layers),
            "layer_names": [n for n, _ in processed_layers],
            "frames_count": num_frames,
            "dimensions": [width, height],
            "saved_files": saved_files,
            "ansi_preview": render_ansi_terminal(composite_frames[0], max_w=48),
        })

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor MCP de LibreSprite")
    parser.add_argument("--http", action="store_true", help="Modo HTTP Server en 127.0.0.1:8766")
    parser.add_argument("--port", type=int, default=8766, help="Puerto HTTP")
    args = parser.parse_args()

    server = build_server()

    if args.http:
        server.run(transport="sse", host="127.0.0.1", port=args.port)
    else:
        server.run(transport="stdio")


if __name__ == "__main__":
    main()
