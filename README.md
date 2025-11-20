# Adivina el Número - Web App

Este es un juego interactivo de "Adivina el Número" construido con Python y Flask.

## 🎮 Cómo jugar

El juego pensará un número aleatorio entre 1 y 100. Tu objetivo es adivinarlo con el menor número de intentos posible. El juego te dará pistas:

- "Más alto" si te has quedado corto.
- "Más bajo" si te has pasado.

## 🚀 Instalación Local

1.  Clona el repositorio.
2.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3.  Ejecuta la aplicación:
    ```bash
    python app.py
    ```
4.  Abre tu navegador en `http://127.0.0.1:5000`.

## 🌐 Despliegue

Este proyecto está configurado para desplegarse en **Render**.
Consulta el archivo `deployment.md` para ver la guía paso a paso.

## 🛠 Tecnologías

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3 (Diseño Responsive)
- **Despliegue**: Gunicorn, Render

## 📂 Estructura

- `app.py`: Lógica del servidor.
- `templates/index.html`: Interfaz de usuario.
- `static/style.css`: Estilos visuales.
- `requirements.txt`: Lista de librerías necesarias.
- `Procfile`: Configuración para Render.
