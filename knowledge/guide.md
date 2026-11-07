# LibreSprite — guía profesional de Pixel Art y Animación para la IA

Usa LibreSprite como un pixel artist senior y animador 2D. Una tarea completada es un sprite o animación con una paleta coherente, silueta clara, buen contraste, proporciones intencionales y frames fluidos.

## 1. Principios del Pixel Art Profesional
- **Resolución & Escala**:
  - Iconos / Items: 16×16 o 24×24 px.
  - Personajes / Enemigos: 24×24, 32×32 o 48×48 px.
  - Retratos / Jefes: 64×64 o 96×96 px.
  - Fondos / Escenarios: 128×72, 256×144 o 320×180 px.
- **Paleta de Color Restringida**:
  - Limita los colores a 4–8 tonos por material/personaje.
  - Usa *hue-shifting*: sombras más frías (azuladas/púrpuras), luces más cálidas (amarillentas/doradas).
  - Nunca uses sombras negras puras (#000000) ni luces blancas puras (#ffffff) salvo para reflejos extremos o contornos.
- **Líneas y Silueta (Lineart)**:
  - Evita "jaggies" (píxeles huérfanos que rompen las diagonales suaves).
  - Evita "doubles" (píxeles adyacentes innecesarios en curvas).
  - La silueta debe ser reconocible incluso en blanco y negro.

## 2. Animación (Principios Clave)
- **Framerate común**: 100 ms a 150 ms por frame (8–10 FPS para estilo retro; 12 FPS para mayor fluidez).
- **Idle (Reposo)**: 4 a 6 frames (respiración, sutil movimiento de ropa/pelo, flexión de rodillas).
- **Walk / Run (Caminar/Correr)**: 4 a 8 frames en bucle (contacto, amortiguación, pase, impulso).
- **Attack (Ataque)**: Anticipación (1-2 frames lentos) -> Golpe rápido (1 frame de smear/impacto) -> Recuperación (2 frames).

## 3. Flujo de Trabajo con las Herramientas
1. `libresprite_status`: Verifica si LibreSprite está instalado y si la GUI está abierta.
2. `libresprite_create_sprite`: Crea o dibuja un sprite individual pixel por pixel, con operaciones geométricas (rectángulos, elipses, líneas, dithering) y paletas profesionales (DB32, Sweetie 16, Pico-8, etc.).
3. `libresprite_create_animation`: Genera animaciones completas con fotogramas secuenciales, exportando directamente a `.ase` (para abrir en LibreSprite) y `.gif` o `.png` (spritesheet) para usar en motores como Godot.
4. `libresprite_export_sheet`: Empaqueta animaciones o archivos `.ase` en hojas de spritesheets con metadata JSON compatible con Godot y motores 2D.
5. `libresprite_open`: Abre el archivo en el editor gráfico de LibreSprite para que el usuario pueda visualizarlo, retocarlo y reproducirlo en su interfaz.

