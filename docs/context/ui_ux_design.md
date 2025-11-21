# UI/UX Design System

## Estética General

- **Tema:** Espacial / Futurista.
- **Paleta de Colores:**
  - Fondo Oscuro: `#0f172a` (Slate 900) con gradientes.
  - Acento: `#6366f1` (Indigo) y `#a855f7` (Purple).
  - Texto: Blanco / Gris claro (`#94a3b8`).
  - Modo Claro: Disponible mediante toggle, usa tonos blancos y azules suaves.

## Componentes Destacados

### 1. Fondo Estelar (Dark Mode)

- Implementado con CSS puro usando múltiples capas de `box-shadow` para crear estrellas de diferentes tamaños (1px, 1.5px, 2px) y opacidades.
- Animación de desplazamiento lento para dar profundidad.

### 2. Switch de Tema (Toggle)

- **Diseño XL:** Tamaño aumentado para facilitar interacción táctil.
- **Animación:** La "bola" del switch contiene iconos de Sol y Luna que rotan y se transforman (scale/opacity) al cambiar.
- **Posición:** Centrado en la parte superior en móviles para evitar solapamientos.

### 3. Hub de Juegos (Portada)

- **Grid Layout:** Tarjetas responsivas.
- **Efecto Hover:** Las tarjetas se elevan, el borde brilla y aparece un overlay con descripción y botón de jugar.
- **Glassmorphism:** Uso de fondos semitransparentes y `backdrop-filter: blur`.

### 4. Ranking

- **Iconos de Dispositivo:** Se muestra 📱 o 💻 según la plataforma del jugador.
- **Filtros:** Botones tipo "píldora" para cambiar entre vista Global, Mensual y Semanal sin recargar la página (AJAX/Fetch).
