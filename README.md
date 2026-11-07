# MCP LibreSprite — Servidor MCP Independiente de Pixel Art y Animación 2D

Servidor MCP autónomo para conectar cualquier IA con **LibreSprite** y crear Pixel Art con calidad senior.

## 🚀 Características
- **Multicapa nativa (`.ase`/`.aseprite`)**: Generación de proyectos con capas separadas (Background, Personaje, Ropa, Sombras, FX) que se abren directamente en LibreSprite.
- **Geometría limpia**:
  - Algoritmo de **Bresenham Clean** sin escalones dobles accidentales (*doubles*).
  - **Curvas cuadráticas de Bézier** rasterizadas a nivel de píxel.
  - Matrices **ASCII** para diseño y control visual total.
- **Colorimetría Pro (Hue-Shifting)**: Rampas de color orgánicas automáticas y acceso a paletas consagradas (`endesga32`, `dawnbringer32`, `sweetie16`, `pico8`).
- **Dithering ordenado**: Patrón **Bayer 4x4** y **Checker** para degradados suaves de estilo retro.
- **Exportación completa**: Exporta simultáneamente proyecto `.ase` editable, `.gif` animado, spritesheet horizontal `.png` y metadatos `.json` compatibles con Godot, Unity y navegadores.

## 📦 Estructura del MCP
```text
mcp libresprite/
├── server.py         # Servidor MCP ejecutable (stdio y sse/http)
├── run_mcp.sh        # Script lanzador listo para enlazar
├── ase_format.py     # Encoder binario nativo oficial .ase / .aseprite
├── draw_engine.py    # Motor de dibujo de precisión (Bézier, Bresenham, Dithering)
├── palettes.py       # Paletas retro y algoritmo de Hue-Shifting
├── requirements.txt  # Dependencias (mcp, Pillow)
└── knowledge/        # Guía técnica y artística para IAs
```

## 🛠️ Configuración en Clientes MCP (Claude Desktop, Cursor, Antigravity, etc.)

Añade el servidor a tu archivo de configuración MCP (`mcp_config.json` o `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "libresprite": {
      "command": "/home/cachy/Descargas/mcp libresprite/run_mcp.sh",
      "args": []
    }
  }
}
```

## 💻 Uso directo en consola
```bash
# Modo Stdio estándar (para IAs)
./run_mcp.sh

# Modo Servidor HTTP / SSE en el puerto 8766
./run_mcp.sh --http --port 8766
```
