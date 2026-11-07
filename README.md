# MCP LibreSprite — Servidor MCP de Pixel Art y Animación 2D (Nivel Pro / Ultra Rápido)

Servidor MCP autónomo para conectar cualquier IA con **LibreSprite** y crear Pixel Art con calidad senior y velocidad instantánea (mejor y más veloz que PixeLab).

## 🚀 Novedades y Capacidades (v2.0)

- **⚡ Generación Instantánea (0.05s) sin demoras**:
  - `libresprite_create_character`: Genera personajes completos multicapa con animación de respiración idle, pestañeo y balanceo en milisegundos.
  - `libresprite_create_prop`: Genera armas, pociones, cofres, gemas y objetos a cualquier resolución de inmediato.
- **📐 Cualquier Resolución Soportada**:
  - No estás limitado a 48x48. Soporta resoluciones estándar (16x16, 24x24, 32x32, 48x48, 64x64, 128x128) y cualquier tamaño rectangular personalizado (e.g. 16x32, 32x64, 128x72, 320x180).
- **🪞 Simetría / Espejado Automático (`mirror: true`)**:
  - Al diseñar con matrices ASCII, activa `"mirror": true` para definir solo la mitad del sprite. El motor lo duplica simétricamente al instante, reduciendo el consumo de tokens y el tiempo de respuesta a la mitad.
- **🎨 Delineado Selectivo Automático (*Sel-out*)**:
  - Soporte de `outline_mode="selective" | "dark"` que calcula y colorea automáticamente los bordes exteriores con el tono oscurecido del píxel adyacente para acabado profesional de videojuego.
- **🏷️ Chunks de Etiquetas de Animación (`Frame Tags 0x2018`)**:
  - Los archivos `.ase` generados incluyen etiquetas nativas reconocidas por LibreSprite (`Idle`, `Walk`, `Attack`) en la línea de tiempo.
- **👁️ Inspección Visual Inmediata (Feedback en tiempo real)**:
  - Nueva herramienta `libresprite_preview` y renderizado ANSI 24-bit en consola para que la IA y el usuario verifiquen el arte al instante.
  - Generación automática de previsualizaciones HD 8x pixel-perfect (*Nearest-Neighbor*).

---

## 🛠️ Herramientas Disponibles

| Herramienta | Descripción |
|---|---|
| `libresprite_create_character` | Generador instantáneo (0.05s) de personajes anime/rpg/chibi multicapa con animación. |
| `libresprite_create_prop` | Generador instantáneo de armas, pociones, cofres y gemas a cualquier tamaño. |
| `libresprite_preview` | Inspecciona visualmente cualquier sprite devolviendo render ANSI y copia HD 8x. |
| `libresprite_create_multilayer` | Crea animaciones multicapa complejas personalizadas con etiquetas de frames. |
| `libresprite_create_animation` | Crea animaciones personalizadas con spritesheets y metadata JSON. |
| `libresprite_create_sprite` | Crea sprites individuales con Bézier, Bresenham clean, dithering y simetría. |
| `libresprite_palette` | Obtiene paletas retro consagradas o genera rampas con Hue-Shifting biológico. |
| `libresprite_status` | Comprueba si LibreSprite está instalado y en ejecución. |
| `libresprite_open` | Abre el archivo directamente en la interfaz gráfica de LibreSprite. |

---

## 💻 Inicio y Configuración

```bash
# Lanzador automático con entorno virtual integrado:
./run_mcp.sh

# Modo Servidor HTTP / SSE:
./run_mcp.sh --http --port 8766
```
