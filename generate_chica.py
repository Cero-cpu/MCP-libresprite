#!/usr/bin/env python3
"""Generador de Pixel Art de Alta Calidad - Versión Masterpiece
Chica anime/RPG con proporciones chibi armoniosas, melena completa y rica paleta.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import sys

sys.path.insert(0, "/home/cachy/Descargas/mcp libresprite")
from ase_format import save_ase_multilayer
from draw_engine import render_ascii_matrix, parse_color

WIDTH = 48
HEIGHT = 48
DURATION = 140

PALETTE = {
    '.': (0, 0, 0, 0),
    ' ': (0, 0, 0, 0),

    # Sombra Suelo
    's': (25, 18, 38, 70),
    'S': (20, 14, 30, 130),

    # Piel
    '0': "#fff0e5",
    '1': "#fedbc2",
    '2': "#f4b994",
    '3': "#d18b6e",
    '4': "#99574d",
    'b': "#f0657a",
    'm': "#b8354c",

    # Ojos
    'w': "#ffffff",
    'c': "#38ef7d",
    'e': "#11998e",
    'E': "#0b5351",
    'k': "#1d152b",
    'B': "#593b70",

    # Pelo
    'H': "#ebd6ff",
    'h': "#af7be8",
    'j': "#7c4bb8",
    'J': "#4f2b82",
    'o': "#261545",

    # Ropa: Blusa
    'W': "#ffffff",
    'G': "#d8deea",
    'g': "#9aa3bd",

    # Ropa: Chaqueta Índigo
    'U': "#556fb5",
    'u': "#35487d",
    'v': "#202a4d",
    'V': "#13182b",

    # Lazo carmesí
    'r': "#ff4d6d",
    'R': "#c9184a",
    'z': "#590d22",

    # Falda plisada
    'K': "#434e6b",
    'y': "#2a3247",
    'Y': "#181d2b",

    # Medias y Botas
    'T': "#38364a",
    't': "#222030",
    'l': "#9c6644",
    'L': "#7f4f24",
    'p': "#4a2810",
    'P': "#241306",

    # Accesorios dorados
    'd': "#ffde59",
    'D': "#c99a2c",
}

def create_layer_frames():
    def make_shadow():
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(f)
        d.ellipse([15, 42, 33, 45], fill=(25, 18, 38, 80))
        d.ellipse([18, 43, 30, 44], fill=(20, 14, 30, 140))
        return f

    def make_hair_back(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0
        sway = 1 if f_idx == 2 else (-1 if f_idx == 3 else 0)

        # Melena llena, suave y tupida que cae por detrás de los hombros y espalda
        hair_back_matrix = [
            # y=8..27 (20 filas)
            "      oooJJjjjjjjJJooo      ",  # 8
            "    ooJJjhhhhhhhhhhjJJoo    ",  # 9
            "   oJJjhhhhhhhhhhhhhhjJJo   ",  # 10
            "  oJjhhhhhhhhhhhhhhhhhhjJo  ",  # 11
            "  oJjhhhhhhhhhhhhhhhhhhjJo  ",  # 12
            "  oJJjhhhhhhhhhhhhhhhhjJJo  ",  # 13
            "  ooJJjjhhhhhhhhhhhhjjJJoo  ",  # 14
            "   oJJJjjjjjjjjjjjjjjJJJo   ",  # 15
            "   oJJJJJJJJJJJJJJJJJJJJo   ",  # 16
            "   oJJJJJJJJJJJJJJJJJJJJo   ",  # 17
            "   oJJJJJJJJJJJJJJJJJJJJo   ",  # 18
            "   oJJJJJJJJJJJJJJJJJJJJo   ",  # 19
            "   oJJJJJJJJJJJJJJJJJJJJo   ",  # 20
            "   ooJJJJJJJJJJJJJJJJJJoo   ",  # 21
            "    oJJJJJJJJJJJJJJJJJJo    ",  # 22
            "    oJJJjjjjjjjjjjjjJJJo    ",  # 23
            "     oJJJ          JJJo     ",  # 24 puntas divididas
            "     oJJj          jJJo     ",  # 25
            "      oJJ          JJo      ",  # 26
            "       oo          oo       ",  # 27
        ]
        render_ascii_matrix(f, 12 + (sway if f_idx in (2, 3) else 0), 8 + dy, hair_back_matrix, PALETTE)
        return f

    def make_body_skin(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0

        # Rostro ovalado lindo
        rostro = [
            # y=9..17
            "    11122222    ",  # 9
            "  111112222222  ",  # 10
            " 11111122222223 ",  # 11
            " 11111122222223 ",  # 12
            " 11111122222223 ",  # 13
            "  111112222223  ",  # 14
            "   2111222223   ",  # 15
            "    32222223    ",  # 16
            "      3223      ",  # 17 mentón
        ]
        render_ascii_matrix(f, 16, 9 + dy, rostro, PALETTE)

        # Cuello
        cuello = [
            "  3223  ",  # 17
            "  3223  ",  # 18
            " 432234 ",  # 19
        ]
        render_ascii_matrix(f, 20, 17 + dy, cuello, PALETTE)

        # Manos descansando tiernamente al frente
        manos = [
            " 1223 ",  # 23
            "  34  ",  # 24
        ]
        render_ascii_matrix(f, 21, 23 + dy, manos, PALETTE)

        # Piernas piel sobre las medias (y=28..29)
        piernas_piel = [
            " 3223 3223 ",  # 28
            " 4334 4334 ",  # 29
        ]
        render_ascii_matrix(f, 18, 28, piernas_piel, PALETTE)

        return f

    def make_face_features(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0
        blink = (f_idx == 3)

        # Cejas
        f.putpixel((19, 10 + dy), parse_color(PALETTE['B']))
        f.putpixel((20, 10 + dy), parse_color(PALETTE['B']))
        f.putpixel((21, 11 + dy), parse_color(PALETTE['B']))

        f.putpixel((26, 11 + dy), parse_color(PALETTE['B']))
        f.putpixel((27, 10 + dy), parse_color(PALETTE['B']))
        f.putpixel((28, 10 + dy), parse_color(PALETTE['B']))

        if blink:
            f.putpixel((18, 13 + dy), parse_color(PALETTE['k']))
            f.putpixel((19, 12 + dy), parse_color(PALETTE['k']))
            f.putpixel((20, 12 + dy), parse_color(PALETTE['k']))
            f.putpixel((21, 13 + dy), parse_color(PALETTE['k']))

            f.putpixel((26, 13 + dy), parse_color(PALETTE['k']))
            f.putpixel((27, 12 + dy), parse_color(PALETTE['k']))
            f.putpixel((28, 12 + dy), parse_color(PALETTE['k']))
            f.putpixel((29, 13 + dy), parse_color(PALETTE['k']))
        else:
            ojo_izq = [
                " kk ",  # 11 pestaña
                "kEkw",  # 12 borde, sombra, brillo
                "keew",  # 13 iris, brillo
                " EEE",  # 14 base
            ]
            render_ascii_matrix(f, 18, 11 + dy, ojo_izq, PALETTE)

            ojo_der = [
                " kk ",  # 11
                "wkEk",  # 12
                "wcee",  # 13
                "EEE ",  # 14
            ]
            render_ascii_matrix(f, 26, 11 + dy, ojo_der, PALETTE)

        # Rubor degradado
        f.putpixel((17, 14 + dy), parse_color(PALETTE['b']))
        f.putpixel((18, 14 + dy), parse_color(PALETTE['b']))
        f.putpixel((18, 15 + dy), parse_color(PALETTE['3']))

        f.putpixel((29, 14 + dy), parse_color(PALETTE['b']))
        f.putpixel((30, 14 + dy), parse_color(PALETTE['b']))
        f.putpixel((29, 15 + dy), parse_color(PALETTE['3']))

        # Nariz y Sonrisa
        f.putpixel((24, 14 + dy), parse_color(PALETTE['3']))
        f.putpixel((23, 16 + dy), parse_color(PALETTE['m']))
        f.putpixel((24, 16 + dy), parse_color(PALETTE['m']))

        return f

    def make_clothes_base(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0

        # 1. Medias ajustadas (más proporcionadas y juntas: espacio de 1px entre piernas) y=30..37
        medias = [
            # y=30..37 (8 filas)
            " TTtt TTtt ",  # 30
            " TTtt TTtt ",  # 31
            " TTtt TTtt ",  # 32 rodilla
            " TTtt TTtt ",  # 33
            " TTtt TTtt ",  # 34 pantorrilla
            " TTtt TTtt ",  # 35
            " TTtt TTtt ",  # 36
            " TTtt TTtt ",  # 37 tobillo
        ]
        render_ascii_matrix(f, 18, 30, medias, PALETTE)

        # 2. Botines elegantes con tacón y puntera y=38..43
        botas = [
            # y=38..43 (6 filas)
            " LLpp LLpp ",  # 38
            "lLLpp lLLpp",  # 39
            "lLLpp lLLpp",  # 40
            "lLLPp lLLPp",  # 41
            "lLLPp lLLPp",  # 42
            "PPPP  PPPP ",  # 43 suela
        ]
        render_ascii_matrix(f, 18, 38, botas, PALETTE)

        # 3. Falda plisada acampanada con pliegues definidos (y=23+dy..29)
        falda = [
            # y=23..29
            "  YYYYYYYYYY  ",  # 23 cintura
            " YyyKyyKyyKyY ",  # 24
            " YyKKyyKKyKKy ",  # 25
            "YyyKKyyKKyyKKy",  # 26
            "YyKKKyyKKKyKKy",  # 27
            "YyyKKyyKKyyKKy",  # 28 vuelo
            "YYYYYYYYYYYYYY",  # 29 ribete
        ]
        render_ascii_matrix(f, 17, 23 + dy, falda, PALETTE)

        # 4. Camisa blanca central (y=19+dy..23+dy)
        camisa = [
            "   WWWW   ",  # 19
            "  WWGGWW  ",  # 20
            "  WWGGWW  ",  # 21
            "   gggg   ",  # 22
        ]
        render_ascii_matrix(f, 19, 19 + dy, camisa, PALETTE)

        return f

    def make_clothes_details(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0

        # Chaqueta y mangas que enmarcan la silueta sin dejar agujeros
        chaqueta = [
            # y=18..24 (7 filas)
            "  vuu      uuv  ",  # 18 hombros
            " VuuuuW  WuuuuV ",  # 19
            " Vuuuu    uuuuV ",  # 20
            " Vuuu      uuuV ",  # 21
            "  Vuu      uuV  ",  # 22
            "   Vu      uV   ",  # 23 puños de manga
            "    V      V    ",  # 24
        ]
        render_ascii_matrix(f, 16, 18 + dy, chaqueta, PALETTE)

        # Cuello blanco marinero
        cuello = [
            " W    W ",  # 18
            "WW GG WW",  # 19
            " g    g ",  # 20
        ]
        render_ascii_matrix(f, 20, 18 + dy, cuello, PALETTE)

        # Corbata / lazo rojo
        lazo = [
            " rzr ",  # 20
            "rzRzr",  # 21
            " zRz ",  # 22
            " r r ",  # 23 lazos
            " z z ",  # 24
        ]
        render_ascii_matrix(f, 21, 20 + dy, lazo, PALETTE)

        # Broche dorado y hebillas
        f.putpixel((23, 21 + dy), parse_color(PALETTE['d']))
        f.putpixel((20, 40), parse_color(PALETTE['d']))
        f.putpixel((26, 40), parse_color(PALETTE['d']))

        return f

    def make_hair_front(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0

        # Cabeza y flequillo
        pelo_cabeza = [
            # y=4..13
            "       ooooooo        ",  # 4
            "    ooohhHHhhhooo     ",  # 5
            "   oohhhHHHHhhhhoo    ",  # 6
            "  oohhhhhhhhhhhhhhoo  ",  # 7
            " oohhhhhhhhhhhhhhhhoo ",  # 8
            "oohhhjhhhhhhhhhhhhjhho",  # 9
            "ojhhhjjhhjjhhhhjjhjjho",  # 10
            "ojhhj  jj  jhjj  jhhjo",  # 11
            "ojhj        j     jhjo",  # 12
            "oj                 jjo",  # 13
        ]
        render_ascii_matrix(f, 13, 4 + dy, pelo_cabeza, PALETTE)

        # Mechones frontales que caen suavemente sobre el pecho
        mechon_izq = [
            "ojh",  # 14
            "ojh",  # 15
            " ojh", # 16
            "  oj", # 17
            "  oj", # 18
            "   o", # 19
        ]
        render_ascii_matrix(f, 13, 14 + dy, mechon_izq, PALETTE)

        mechon_der = [
            "hjo",  # 14
            "hjo",  # 15
            "hjo ", # 16
            "jo  ", # 17
            "jo  ", # 18
            "o   ", # 19
        ]
        render_ascii_matrix(f, 31, 14 + dy, mechon_der, PALETTE)

        # Pasador / horquilla de estrella dorada en el pelo
        pasador = [
            " d D ",  # 6
            "dDdDd",  # 7
            " D d ",  # 8
        ]
        render_ascii_matrix(f, 28, 6 + dy, pasador, PALETTE)

        return f

    def make_highlights(f_idx):
        f = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        dy = -1 if f_idx in (1, 2) else 0

        halo = [(18, 6+dy), (19, 6+dy), (20, 5+dy), (21, 5+dy), (22, 5+dy), (23, 6+dy), (24, 6+dy)]
        for hx, hy in halo:
            f.putpixel((hx, hy), parse_color(PALETTE['H']))

        f.putpixel((20, 39), (255, 255, 255, 210))
        f.putpixel((26, 39), (255, 255, 255, 210))

        return f

    layers = [
        ("Shadow_Ground", [make_shadow() for _ in range(4)]),
        ("Hair_Back", [make_hair_back(i) for i in range(4)]),
        ("Body_Skin", [make_body_skin(i) for i in range(4)]),
        ("Face_Features", [make_face_features(i) for i in range(4)]),
        ("Clothes_Base", [make_clothes_base(i) for i in range(4)]),
        ("Clothes_Details", [make_clothes_details(i) for i in range(4)]),
        ("Hair_Front", [make_hair_front(i) for i in range(4)]),
        ("Highlights_FX", [make_highlights(i) for i in range(4)]),
    ]
    return layers

def main():
    desktop_dir = Path("/home/cachy/Escritorio")
    desktop_dir.mkdir(parents=True, exist_ok=True)

    ase_path = desktop_dir / "chica_pixelart.ase"
    gif_path = desktop_dir / "chica_pixelart.gif"
    png_path = desktop_dir / "chica_pixelart.png"
    preview_path = desktop_dir / "chica_pixelart_preview_8x.png"
    preview_gif_path = desktop_dir / "chica_pixelart_preview_8x.gif"
    sheet_path = desktop_dir / "chica_pixelart_sheet.png"

    print("🎨 Renderizando capas maestras...")
    layers = create_layer_frames()

    print(f"💾 Guardando .ase multicapa: {ase_path}")
    save_ase_multilayer(ase_path, layers, duration_ms=DURATION)

    num_frames = 4
    composite_frames = []
    for f_idx in range(num_frames):
        comp = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        for _, f_imgs in layers:
            comp.alpha_composite(f_imgs[f_idx])
        composite_frames.append(comp)

    composite_frames[0].save(png_path)
    composite_frames[0].save(
        gif_path,
        save_all=True,
        append_images=composite_frames[1:],
        duration=DURATION,
        loop=0,
        disposal=2
    )

    sheet = Image.new("RGBA", (WIDTH * num_frames, HEIGHT), (0, 0, 0, 0))
    for i, frame in enumerate(composite_frames):
        sheet.paste(frame, (i * WIDTH, 0))
    sheet.save(sheet_path)

    scale = 8
    preview = composite_frames[0].resize((WIDTH * scale, HEIGHT * scale), Image.NEAREST)
    preview.save(preview_path)

    upscaled_frames = [f.resize((WIDTH * scale, HEIGHT * scale), Image.NEAREST) for f in composite_frames]
    upscaled_frames[0].save(
        preview_gif_path,
        save_all=True,
        append_images=upscaled_frames[1:],
        duration=DURATION,
        loop=0,
        disposal=2
    )
    print("✨ Exportación final completada!")

if __name__ == "__main__":
    main()
