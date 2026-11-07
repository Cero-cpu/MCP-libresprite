"""Encoder nativo de archivos .ase / .aseprite (formato Aseprite/LibreSprite).

Soporta:
- Múltiples capas independientes (Background, Lineart, Shading, Highlights, etc.)
- Múltiples fotogramas con duración precisa por frame
- Cels comprimidos zlib transparentes
- Chunks de etiquetas de animación (0x2018 Frame Tags: Idle, Walk, Attack, etc.)
- Cualquier resolución arbitraria de lienzo (16x16, 24x24, 32x32, 48x48, 64x64, 128x128, etc.)
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image


def _build_tags_chunk(tags: List[Dict[str, Any]]) -> bytes:
    """Construye el chunk 0x2018 (Frame Tags) de Aseprite."""
    if not tags:
        return b""
    payload = struct.pack("<H8s", len(tags), b"\x00" * 8)
    for t in tags:
        name_bytes = str(t.get("name", "Tag")).encode("utf-8")
        from_frame = int(t.get("from", 0))
        to_frame = int(t.get("to", 0))
        direction = int(t.get("direction", 0))  # 0=Forward, 1=Reverse, 2=Ping-pong
        c = t.get("color", (120, 160, 255))
        tag_data = struct.pack(
            "<HHBH6sBBBBH",
            from_frame,
            to_frame,
            direction,
            0,  # repeat (0 = infinito)
            b"\x00" * 6,
            int(c[0]), int(c[1]), int(c[2]), 0,
            len(name_bytes),
        ) + name_bytes
        payload += tag_data
    chunk_size = 6 + len(payload)
    return struct.pack("<IH", chunk_size, 0x2018) + payload


def encode_ase_multilayer(
    layers_data: List[Tuple[str, List[Image.Image]]],  # [(layer_name, [frame0, frame1, ...])]
    duration_ms: int = 100,
    tags: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    """Codifica un archivo .ase completo con múltiples capas, fotogramas y etiquetas."""
    if not layers_data:
        raise ValueError("layers_data cannot be empty")

    num_layers = len(layers_data)
    num_frames = len(layers_data[0][1])
    w, h = layers_data[0][1][0].size

    # Chunks de capas (0x2004) en el primer fotograma
    layer_chunks = []
    for layer_idx, (name, _) in enumerate(layers_data):
        encoded_name = str(name).encode("utf-8")
        ldata = struct.pack(
            "<HHHHHHB3sH",
            1 | 2,  # visible + editable
            0,      # normal layer
            0,      # child level
            0, 0,   # width/height
            0,      # normal blend
            255,    # opacity
            b"\x00\x00\x00",
            len(encoded_name),
        ) + encoded_name
        lsize = 6 + len(ldata)
        layer_chunks.append(struct.pack("<IH", lsize, 0x2004) + ldata)

    tags_chunk = _build_tags_chunk(tags) if tags else b""

    frame_bytes_list = []

    for f_idx in range(num_frames):
        chunks = []
        if f_idx == 0:
            chunks.extend(layer_chunks)
            if tags_chunk:
                chunks.append(tags_chunk)

        for layer_idx, (_, f_imgs) in enumerate(layers_data):
            img = f_imgs[f_idx].convert("RGBA")
            if img.size != (w, h):
                img = img.resize((w, h), Image.NEAREST)

            raw_pixels = img.tobytes()
            compressed = zlib.compress(raw_pixels)

            # Cel Chunk (0x2005)
            cel_header = struct.pack("<HhhBH7sHH", layer_idx, 0, 0, 255, 2, b"\x00" * 7, w, h)
            cel_data = cel_header + compressed
            cel_size = 6 + len(cel_data)
            cel_chunk = struct.pack("<IH", cel_size, 0x2005) + cel_data
            chunks.append(cel_chunk)

        num_chunks = len(chunks)
        chunks_payload = b"".join(chunks)
        frame_header_size = 16
        total_frame_size = frame_header_size + len(chunks_payload)

        frame_header = struct.pack(
            "<IHHH2sI",
            total_frame_size,
            0xF1FA,
            num_chunks,
            duration_ms,
            b"\x00\x00",
            0,
        )
        frame_bytes_list.append(frame_header + chunks_payload)

    all_frames_payload = b"".join(frame_bytes_list)
    total_file_size = 128 + len(all_frames_payload)

    header = struct.pack(
        "<IHH HHH I HII B3sH BB hh HH 84s",
        total_file_size,
        0xA5E0,
        num_frames,
        w,
        h,
        32,  # 32 bpp (RGBA)
        1,   # flags
        duration_ms,
        0, 0,
        0,
        b"\x00\x00\x00",
        0,
        0, 0,
        0, 0,
        16, 16,
        b"\x00" * 84,
    )

    return header + all_frames_payload


def save_ase_multilayer(
    filepath: Union[str, Path],
    layers_data: List[Tuple[str, List[Image.Image]]],
    duration_ms: int = 100,
    tags: Optional[List[Dict[str, Any]]] = None,
) -> Path:
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = encode_ase_multilayer(layers_data, duration_ms, tags=tags)
    p.write_bytes(data)
    return p


def encode_ase(
    frames: List[Image.Image],
    duration_ms: int = 100,
    layer_name: str = "Layer 1",
    tags: Optional[List[Dict[str, Any]]] = None,
) -> bytes:
    """Wrapper monocapa para compatibilidad directa."""
    return encode_ase_multilayer([(layer_name, frames)], duration_ms, tags=tags)


def save_ase(
    filepath: Union[str, Path],
    frames: List[Image.Image],
    duration_ms: int = 100,
    layer_name: str = "Layer 1",
    tags: Optional[List[Dict[str, Any]]] = None,
) -> Path:
    return save_ase_multilayer(filepath, [(layer_name, frames)], duration_ms, tags=tags)
