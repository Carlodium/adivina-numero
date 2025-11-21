# Carlodium Arcade - Project Overview

## Descripción

Carlodium Arcade es una plataforma web de minijuegos desarrollada en Python (Flask) y JavaScript. Actualmente cuenta con un juego principal: "Adivina el Número", y una estructura escalable para añadir más títulos en el futuro.

## Estructura del Proyecto

- **Backend:** Flask (Python). Maneja rutas, lógica de base de datos y API de rankings.
- **Frontend:** HTML5, CSS3 (Vanilla), JavaScript. Diseño responsive y animado.
- **Base de Datos:** PostgreSQL (Producción en Render) / SQLite (Desarrollo local).

## Rutas Principales

- `/`: **Hub / Portada**. Muestra el catálogo de juegos disponibles con un diseño de tarjetas interactivas.
- `/adivina`: **Juego "Adivina el Número"**. La lógica del juego, formulario de puntuación y ranking.
- `/api/rankings/<period>`: **API JSON**. Devuelve los mejores puntajes filtrados por periodo (global, mensual, semanal).

## Características Clave

- **Sistema de Ranking:** Persistente, con filtros temporales y detección de dispositivo.
- **Diseño Premium:** Animaciones CSS, modo oscuro/claro con switch personalizado, efectos de partículas (confeti, estrellas).
- **Responsive:** Adaptado perfectamente a móviles y escritorio.
