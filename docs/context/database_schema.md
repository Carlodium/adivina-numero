# Database Schema

## Tabla: `scores`

Almacena las puntuaciones de los jugadores para el juego "Adivina el Número".

| Columna      | Tipo (Postgres/SQLite) | Descripción                                             |
| ------------ | ---------------------- | ------------------------------------------------------- |
| `id`         | SERIAL / INTEGER PK    | Identificador único del registro.                       |
| `name`       | TEXT                   | Nombre del jugador (max 16 caracteres).                 |
| `attempts`   | INTEGER                | Número de intentos realizados para ganar.               |
| `created_at` | TIMESTAMP              | Fecha y hora del registro (Default: CURRENT_TIMESTAMP). |
| `device`     | TEXT                   | Tipo de dispositivo: 'Mobile' o 'Desktop'.              |

## Notas de Implementación

- La aplicación detecta automáticamente el entorno (Render vs Local) para conectar a PostgreSQL o SQLite.
- Se incluye una función `init_db()` que crea la tabla si no existe y maneja migraciones básicas (como añadir la columna `device` si falta).
