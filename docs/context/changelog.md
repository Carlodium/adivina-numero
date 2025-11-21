# Changelog

## [Unreleased] - 2025-11-21

### Added

- **Carlodium Arcade Hub:** Nueva página de inicio (`/`) con diseño de tarjetas para seleccionar juegos.
- **Device Detection:** El sistema ahora detecta si el usuario juega desde Móvil o PC y lo guarda en la base de datos.
- **Ranking Icons:** Se muestran iconos (📱/💻) en la tabla de puntuaciones.
- **Back Navigation:** Botón para volver del juego al Hub principal.

### Changed

- **Rutas:** El juego "Adivina el Número" se movió de `/` a `/adivina`.
- **UI Switch:** Rediseño completo del interruptor de tema (tamaño XL, animaciones de iconos Sol/Luna).
- **Background:** Mejora significativa en la densidad y realismo de las estrellas en modo oscuro.
- **Mobile Layout:** Ajustes de espaciado y posición del switch para evitar solapamientos en pantallas pequeñas.

### Fixed

- **Database:** Migración automática para añadir la columna `device` sin perder datos previos.
- **Ranking Filters:** Corrección en la lógica JS para renderizar correctamente los iconos de dispositivo al filtrar por fecha.
