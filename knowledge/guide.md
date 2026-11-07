# LibreSprite — Guía de Pixel Art y Animación de Ultra Alto Rendimiento para la IA

Usa LibreSprite como un pixel artist senior y animador 2D. Una tarea completada es un sprite o animación con paleta coherente, silueta clara, buen contraste, proporciones armónicas y frames fluidos.

## ⚡ Regla de Oro: Velocidad y Calidad (Mejor que PixeLab)
Para evitar que la IA se quede "working... working..." escribiendo miles de caracteres a ciegas o cometiendo errores anatómicos:
1. **Para Héroes Top-Down en 4 Direcciones**: Usa `libresprite_create_topdown_hero`. Genera en **0.06 segundos** un protagonista completo en sus 4 direcciones (Down, Up, Right, Left) con ciclo de caminata (16 frames), tags para LibreSprite y anatomía 100% sellada (sin huecos ni extremidades flotantes).
2. **Para Tilesets y Terrenos**: Usa `libresprite_create_tileset`. Crea suelos 100% seamless para `TileMapLayer` con variaciones orgánicas (flores, briznas, guijarros) y bordes de remate.
3. **Para Personajes Frontales**: Usa `libresprite_create_character` para personajes estáticos o idle (16x16 hasta 128x128).
4. **Para Objetos/Armas**: Usa `libresprite_create_prop` (pociones, cofres, gemas, espadas).
5. **Autocorrección Anatómica**: El motor ahora ejecuta automáticamente `fix_anatomical_gaps` y `clean_stray_pixels` para sellar cualquier hueco accidental entre cuello, torso y piernas.
6. **Inspección Visual Real (Multimodal)**: Todas las herramientas devuelven `preview_image_path`. Usa `read_file` sobre ese archivo para que la IA vea el sprite con sus ojos neuronales y aplique auto-crítica antes de finalizar.

## 1. Resoluciones Recomendadas
- **16×16 o 24×24**: Iconos, items, props, pociones, espadas o personajes estilo retro (Pico-8 / GameBoy).
- **32×32**: Estándar dorado RPG retro (Chrono Trigger, Final Fantasy VI, Celeste).
- **48×48**: Detalle alto anime / aventura (Castlevania, Mega Man X).
- **64×64 o mayor**: Retratos detallados, jefes o personajes de alta definición.
- **Tamaños libres**: Puedes usar rectángulos como 16×32 (personajes esbeltos) o 128×72 / 320×180 (escenarios/fondos).

## 2. Paletas y Color
- Utiliza **Hue-Shifting**: Sombras frías azuladas/violáceas y luces cálidas amarillentas/doradas.
- Activa `outline_mode="selective"` para que los bordes oscuros se calculen armónicamente en vez de usar negro puro plano.
