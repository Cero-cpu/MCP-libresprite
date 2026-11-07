"""Encoder nativo de archivos .ase / .aseprite (formato Aseprite/LibreSprite).

Soporta:
- Múltiples capas independientes (Background, Lineart, Shading, Highlights, etc.)
- Múltiples fotogramas con duración precisa por frame
- Cels comprimidos zlib transparentes
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path
from typing import List, Tuple, Union
from PIL import Image


def encode_ase_multilayer(
    layers_data: List[Tuple[str, List[Image.Image]]],  # [(layer_name, [frame0, frame1, ...])]
    duration_ms: int = 100,
) -> bytes:
    """Codifica un archivo .ase completo con múltiples capas y fotogramas."""
    if not layers_data:
        raise ValueError("layers_data cannot be empty")

    num_layers = len(layers_data)
    num_frames = len(layers_data[0][1])
    w, h = layers_data[0][1][0].size

    # Chunks de capas (0x2004) en el primer fotograma
    layer_chunks = []
    for layer_idx, (name, _) in enumerate(layers_data):
        encoded_name = name.encode("utf-8")
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

    frame_bytes_list = []

    for f_idx in range(num_frames):
        chunks = []
        if f_idx == 0:
            chunks.extend(layer_chunks)

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
        32,
        1,
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
) -> Path:
    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = encode_ase_multilayer(layers_data, duration_ms)
    p.write_bytes(data)
    return p


def encode_ase(
    frames: List[Image.Image],
    duration_ms: int = 100,
    layer_name: str = "Layer 1",
) -> bytes:
    """Wrapper monocapa para compatibilidad directa."""
    return encode_ase_multilayer([(layer_name, frames)], duration_ms)


def save_ase(
    filepath: Union[str, Path],
    frames: List[Image.Image],
    duration_ms: int = 100,
    layer_name: str = "Layer 1",
) -> Path:
    return save_ase_multilayer(filepath, [(layer_name, frames)], duration_ms)
