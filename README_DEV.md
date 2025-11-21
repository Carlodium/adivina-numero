# 🛠️ Guía para Desarrolladores

Esta guía técnica está dirigida a desarrolladores que quieran contribuir al proyecto, entender su arquitectura o ejecutarlo localmente.

---

## 📋 Tabla de Contenidos

- [Instalación Local](#-instalación-local)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Base de Datos](#️-base-de-datos)
- [Sistema de Autenticación](#-sistema-de-autenticación)
- [API Endpoints](#-api-endpoints)
- [Gestión de Estilos CSS](#-gestión-de-estilos-css)
- [Testing](#-testing)
- [Deployment](#-deployment)

---

## 🚀 Instalación Local

### Requisitos

- Python 3.9+
- pip
- Git

### Pasos

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/Carlodium/adivina-numero.git
   cd adivina-numero
   ```

2. **Crear un entorno virtual:**

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno (opcional):**

   ```bash
   # Crear archivo .env
   SECRET_KEY=your_secret_key_here
   # DATABASE_URL solo se usa en producción
   ```

5. **Ejecutar la aplicación:**
   ```bash
   python app.py
   ```
   Abre `http://127.0.0.1:5000` en tu navegador.

---

## 🏗️ Arquitectura del Proyecto

### Estructura de Archivos

```
adivina-numero/
├── app.py                    # Aplicación Flask principal
├── requirements.txt          # Dependencias
├── manage_db.py             # Script de gestión de BD local
├── static/
│   ├── style.css            # Estilos globales + variables CSS
│   ├── hub.css              # Estilos específicos del Hub
│   ├── game.css             # Estilos del juego
│   └── auth.css             # Estilos de autenticación
├── templates/
│   ├── hub.html             # Página principal (Arcade)
│   ├── game.html            # Juego "Adivina el Número"
│   └── auth.html            # Login/Registro
└── database.db              # SQLite (generado automáticamente)
```

### Flujo de la Aplicación

1. **Hub (`/`)**: Página principal con lista de juegos
2. **Autenticación (`/auth`)**: Login/Registro con tabs
3. **Juego (`/adivina`)**: Lógica del juego + rankings
4. **API (`/api/rankings/<period>`)**: Datos JSON para filtros

---

## 🗄️ Base de Datos

### Esquema

#### Tabla `users`

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabla `scores`

```sql
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    attempts INTEGER NOT NULL,
    device TEXT DEFAULT 'Desktop',
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Gestión Local (SQLite)

Usa el script `manage_db.py` para gestionar puntuaciones locales:

```bash
python manage_db.py
```

**Opciones:**

1. Ver todas las puntuaciones
2. Borrar TODAS las puntuaciones
3. Borrar una puntuación específica

### Producción (PostgreSQL)

En Render, la app detecta automáticamente `DATABASE_URL` y usa PostgreSQL. Las migraciones se ejecutan automáticamente al iniciar.

---

## 🔐 Sistema de Autenticación

### Flujo de Registro

1. Usuario envía `username` y `password` a `/register` (POST)
2. Backend hashea la contraseña con `werkzeug.security.generate_password_hash`
3. Se crea el usuario en la BD
4. Se inicia sesión automáticamente (`session['user_id']`, `session['username']`)

### Flujo de Login

1. Usuario envía credenciales a `/login` (POST)
2. Backend verifica con `check_password_hash`
3. Si es correcto, se establece la sesión

### Modo Invitado

- Los invitados pueden jugar sin registrarse
- Al ganar, el score se guarda en `session['pending_score']`
- Si se registran después, el score se asigna a su cuenta

### Personal Best Logic

- Solo se guarda el **mejor** score de cada usuario
- Si el nuevo score es peor, se rechaza
- Si es mejor, se **actualiza** el registro existente (no se crea uno nuevo)

---

## 📡 API Endpoints

### `GET /`

Renderiza el Hub (página principal)

### `GET /adivina`

Renderiza el juego con rankings y datos del usuario

**Query Params:**

- `saved=1`: Muestra mensaje de score guardado
- `record=true/false`: Indica si fue récord personal
- `guest_score=X`: Score de invitado

**Template Variables:**

- `top_scores`: Top 5 global
- `user_best`: Mejor score del usuario (si está logueado)

### `POST /adivina`

Guarda un score (solo usuarios logueados)

**Form Data:**

- `guardar_score=1`
- `intentos_finales`: Número de intentos
- `device`: 'Mobile' o 'Desktop'

### `GET /api/rankings/<period>`

Devuelve rankings en JSON

**Períodos:**

- `all`: Global
- `monthly`: Último mes
- `weekly`: Última semana

**Response:**

```json
{
  "scores": [
    {
      "name": "Carlos",
      "attempts": 3,
      "device": "Desktop",
      "badges": ["🎯", "💻"]
    }
  ]
}
```

### `POST /register`

Crea una nueva cuenta

**JSON Body:**

```json
{
  "username": "carlos",
  "password": "securepass123"
}
```

### `POST /login`

Inicia sesión

**JSON Body:**

```json
{
  "username": "carlos",
  "password": "securepass123"
}
```

### `GET /logout`

Cierra sesión y redirige al Hub

---

## 🎨 Gestión de Estilos CSS

### Arquitectura CSS

Para evitar conflictos y mejorar mantenibilidad, los estilos están **separados por página**:

- **`style.css`**: Variables CSS globales, reset, componentes compartidos
- **`hub.css`**: Estilos exclusivos del Hub (game cards, animaciones pulse)
- **`game.css`**: Estilos del juego (back button mejorado, history items)
- **`auth.css`**: Estilos de login/registro (tabs, inputs)

### Variables CSS Principales

```css
:root {
  --bg-color: #0f172a;
  --card-bg: rgba(30, 41, 59, 0.8);
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --primary: #6366f1;
  --primary-hover: #4f46e5;
  --accent: #a855f7;
  --border-color: rgba(255, 255, 255, 0.1);
  --input-bg: rgba(255, 255, 255, 0.05);
}
```

### Temas

#### Light Mode

Activado con `.light-mode` en `<body>`. Cambia variables CSS automáticamente.

#### Matrix Mode (Easter Egg)

Activado con Konami Code. Aplica `.matrix-mode` en `<body>`:

```css
body.matrix-mode {
  --bg-color: #0d0208;
  --text-main: #00ff41;
  --primary: #00ff41;
  /* ... */
}
```

---

## 🧪 Testing

### Testing Manual

1. **Autenticación:**

   - Registrar usuario nuevo
   - Login con credenciales correctas/incorrectas
   - Logout

2. **Juego (Usuario Logueado):**

   - Jugar y ganar con score mejor que el actual
   - Jugar y ganar con score peor (verificar que no se guarda)
   - Verificar que solo aparece 1 entrada en el ranking

3. **Juego (Invitado):**

   - Jugar sin login
   - Verificar que aparece CTA de registro
   - Registrarse y verificar que el score se guarda

4. **Rankings:**

   - Cambiar filtros (Global/Mensual/Semanal)
   - Verificar badges correctos

5. **Easter Eggs:**
   - Probar Konami Code (↑↑↓↓←→←→BA)
   - Verificar Matrix Mode persiste en localStorage

---

## 🚀 Deployment

### Render (Producción)

1. **Conectar repositorio GitHub** a Render
2. **Configurar variables de entorno:**
   - `SECRET_KEY`: Clave secreta de Flask
   - `DATABASE_URL`: URL de PostgreSQL (Render lo provee automáticamente)
3. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start Command:**
   ```bash
   gunicorn app:app
   ```

### Inicialización de BD en Producción

La app ejecuta `init_db()` automáticamente al iniciar. Si necesitas forzar la inicialización, visita:

```
https://tu-app.onrender.com/init-db
```

---

## 🐛 Debugging

### Logs en Render

Accede a los logs desde el dashboard de Render para ver errores de producción.

### Errores Comunes

**Error: `DATABASE_URL` not found**

- Asegúrate de que la variable de entorno está configurada en Render

**Error: `ModuleNotFoundError: No module named 'psycopg2'`**

- Verifica que `requirements.txt` incluye `psycopg2-binary`

**Scores no se guardan (usuarios logueados)**

- Verifica que `user_id` se está pasando correctamente a `save_score()`
- Revisa la lógica de Personal Best en `save_score()`

---

## 📝 Convenciones de Código

- **Python**: PEP 8
- **JavaScript**: camelCase para variables, PascalCase para clases
- **CSS**: kebab-case para clases, camelCase para variables JS
- **Commits**: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📞 Soporte

Si encuentras algún bug o tienes preguntas técnicas, abre un **Issue** en GitHub.

---

_Desarrollado por Carlos (Carlodium) con la asistencia de Jose (IA)_
