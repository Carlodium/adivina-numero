# 🛠️ Guía para Desarrolladores

Esta guía es para aquellos que quieran descargar el código, ejecutarlo en su propio ordenador y entender cómo funciona la gestión de datos localmente.

## 🚀 Instalación y Ejecución Local

1.  **Clonar el repositorio:**

    ```bash
    git clone https://github.com/Carlodium/adivina-numero.git
    cd adivina-numero
    ```

2.  **Crear un entorno virtual (opcional pero recomendado):**

    ```bash
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate
    ```

3.  **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar el juego:**
    ```bash
    python app.py
    ```
    El juego estará disponible en `http://127.0.0.1:5000`.

---

## 🗄️ Gestión de Base de Datos Local (SQLite)

Cuando ejecutas el juego en local, se crea automáticamente un archivo `scores.db` (SQLite) para guardar las puntuaciones. Esto es independiente de la base de datos global de producción.

Hemos incluido un script para que puedas gestionar tus puntuaciones locales fácilmente.

### Uso del script `manage_db.py`

Este script te permite ver y borrar puntuaciones de tu base de datos local.

1.  Abre una terminal en la carpeta del proyecto.
2.  Ejecuta:
    ```bash
    python manage_db.py
    ```
3.  Verás un menú con las siguientes opciones:
    - **1. Ver todas las puntuaciones:** Lista todos los jugadores y sus intentos.
    - **2. Borrar TODAS las puntuaciones:** Limpia la base de datos local por completo.
    - **3. Borrar una puntuación específica:** Te pedirá el nombre del jugador para borrar solo ese registro.

### Nota sobre Producción

En la versión desplegada en Render, utilizamos **PostgreSQL**. El script `manage_db.py` está diseñado para trabajar con SQLite por defecto en local, pero el código del juego (`app.py`) detecta automáticamente si está en Render para conectarse a la base de datos correcta.
