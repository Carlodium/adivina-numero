# 👾 Carlodium Arcade

<div align="center">

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![Flask](https://img.shields.io/badge/flask-3.0+-red)
![License](https://img.shields.io/badge/license-MIT-yellow)

**Una colección de juegos retro modernizados con sistema de autenticación, rankings globales y easter eggs.**

[🎮 Jugar Ahora](https://adivina-numero-qv60.onrender.com) • [📖 Documentación](#-características) • [🚀 Instalación](#️-instalación-local)

</div>

---

## 🎯 Sobre el Proyecto

Carlodium Arcade es una plataforma de juegos web que combina la nostalgia de los clásicos arcade con tecnología moderna. Actualmente incluye **Adivina el Número**, un juego adictivo de lógica y estrategia con sistema de puntuación competitivo.

### 🌟 Características Principales

#### 🔐 Sistema de Autenticación

- **Registro e Inicio de Sesión** con contraseñas hasheadas (bcrypt)
- **Sesiones persistentes** con Flask sessions
- **Modo Invitado**: Juega sin registrarte y guarda tu score al crear cuenta
- **Personal Best**: Solo se guarda tu mejor puntuación (sin duplicados)

#### 🏆 Rankings Globales

- **Top 5 Mundial** con filtros por período (Global, Mensual, Semanal)
- **Sistema de Logros/Badges**:
  - 🎯 Francotirador (1 intento)
  - 🧠 Genio (2-4 intentos)
  - ⚡ Veloz (5-7 intentos)
  - 🐢 Persistente (>10 intentos)
  - 📱/💻 Badges de dispositivo (Mobile/Desktop)
- **Racha de Victorias** guardada localmente

#### 🎨 Diseño Premium

- **Tema Oscuro/Claro** con transición suave (1s)
- **Animaciones Micro**:
  - Efecto "respiración" en cards
  - Glow intenso al hover
  - Fade-in al cargar páginas
- **Responsive Design**: Perfecto en móvil, tablet y desktop
- **Glassmorphism** y efectos de neón

#### 🎮 Easter Eggs

- **Código Konami** (↑↑↓↓←→←→BA): Activa el **Modo Matrix** 🟢
  - Tema verde hacker
  - Confetti verde
  - Persiste entre sesiones

#### 💾 Base de Datos

- **PostgreSQL** en producción (Render)
- **SQLite** en desarrollo local
- **Migraciones automáticas** al iniciar

---

## 🎲 Juegos Disponibles

### Adivina el Número

Adivina un número entre 1 y 100 en el menor número de intentos posible.

**Características:**

- Historial visual de intentos con indicadores ⬆️/⬇️
- Validación de entradas duplicadas
- Confetti al ganar 🎊
- Contador de racha de victorias
- Feedback inteligente (récord vs. no récord)

---

## 🛠️ Instalación Local

### Requisitos Previos

- Python 3.9+
- pip
- Git

### Pasos

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/Carlodium/adivina-numero.git
   cd adivina-numero
   ```

2. **Crea un entorno virtual (recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno (opcional):**

   ```bash
   # Crea un archivo .env
   SECRET_KEY=tu_clave_secreta_aqui
   # DATABASE_URL se usa solo en producción
   ```

5. **Ejecuta la aplicación:**

   ```bash
   python app.py
   ```

6. **Abre tu navegador:**
   ```
   http://127.0.0.1:5000
   ```

---

## 💻 Stack Tecnológico

### Backend

- **Flask 3.0+**: Framework web
- **PostgreSQL**: Base de datos en producción
- **SQLite**: Base de datos en desarrollo
- **psycopg2**: Adaptador PostgreSQL
- **Werkzeug**: Hashing de contraseñas

### Frontend

- **HTML5**: Estructura semántica
- **CSS3**: Diseño moderno con variables CSS
- **JavaScript (Vanilla)**: Lógica del juego
- **Canvas Confetti**: Efectos de celebración

### Deployment

- **Render**: Hosting en la nube
- **Gunicorn**: Servidor WSGI en producción

---

## 📁 Estructura del Proyecto

```
adivina-numero/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── static/
│   ├── style.css         # Estilos globales
│   ├── hub.css           # Estilos del Hub
│   ├── game.css          # Estilos del juego
│   └── auth.css          # Estilos de autenticación
├── templates/
│   ├── hub.html          # Página principal (Arcade)
│   ├── game.html         # Juego "Adivina el Número"
│   └── auth.html         # Login/Registro
└── database.db           # SQLite (local)
```

---

## 🎯 Roadmap

### Próximas Features

- [ ] 🐍 Snake Espacial (2º juego)
- [ ] 📊 Estadísticas personales con gráficos
- [ ] 🎯 Sistema de dificultad (Fácil/Normal/Difícil/Extremo)
- [ ] 🔊 Efectos de sonido opcionales
- [ ] 🌐 Internacionalización (i18n)
- [ ] 🏅 Más logros y achievements

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si quieres mejorar el proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👨‍💻 Autor

**Carlos (Carlodium)**

- GitHub: [@Carlodium](https://github.com/Carlodium)

_Desarrollado con la asistencia de Jose (IA) - Google Deepmind_

---

## 🎮 ¿Listo para Jugar?

No esperes más. Demuestra tu habilidad y entra en el Top 5 mundial:

### 👉 **[JUGAR AHORA](https://adivina-numero-qv60.onrender.com)** 👈

---

<div align="center">

**¿Encontraste el Código Konami?** 🎮

_Pista: ↑↑↓↓←→←→BA_

</div>
