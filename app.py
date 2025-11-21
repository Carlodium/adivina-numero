import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

from flask_socketio import SocketIO
import events

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_arcade_key_123')
socketio = SocketIO(app, async_mode='eventlet')

# Register SocketIO events
events.register_events(socketio)

def get_db_connection():
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = sqlite3.connect('scores.db')
    return conn



if __name__ == '__main__':
    socketio.run(app, debug=True)


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Tabla Scores
    if os.environ.get('DATABASE_URL'):
        # PostgreSQL
        c.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tabla Users (Postgres)
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # SQLite
        c.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tabla Users (SQLite)
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Commit table creation immediately to ensure they exist before migrations run
    conn.commit()

    # Migración: Añadir columna 'device' si no existe
    try:
        c.execute('ALTER TABLE scores ADD COLUMN device TEXT DEFAULT \'Desktop\'')
        conn.commit()
    except Exception:
        conn.rollback()

    # Migración: Añadir columna 'user_id' si no existe
    try:
        if os.environ.get('DATABASE_URL'):
            c.execute('ALTER TABLE scores ADD COLUMN user_id INTEGER REFERENCES users(id)')
        else:
            c.execute('ALTER TABLE scores ADD COLUMN user_id INTEGER REFERENCES users(id)')
        conn.commit()
    except Exception:
        conn.rollback()

    conn.commit()
    conn.close()

def save_score(name, attempts, device, user_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Si el usuario está logueado, comprobamos Personal Best
    if user_id:
        # Buscar mejor puntuación actual
        if os.environ.get('DATABASE_URL'):
            c.execute('SELECT MIN(attempts), id FROM scores WHERE user_id = %s GROUP BY id ORDER BY attempts ASC LIMIT 1', (user_id,))
        else:
            c.execute('SELECT MIN(attempts), id FROM scores WHERE user_id = ? GROUP BY id ORDER BY attempts ASC LIMIT 1', (user_id,))
            
        result = c.fetchone()
        
        if result and result[0] is not None:
            current_best = result[0]
            score_id = result[1]
            
            if attempts >= current_best:
                # No es récord personal, no guardamos
                conn.close()
                return False
            
            # Es mejor score - ACTUALIZAR el existente
            if os.environ.get('DATABASE_URL'):
                c.execute('UPDATE scores SET attempts = %s, device = %s, created_at = CURRENT_TIMESTAMP WHERE id = %s', 
                         (attempts, device, score_id))
            else:
                c.execute('UPDATE scores SET attempts = ?, device = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?', 
                         (attempts, device, score_id))
            conn.commit()
            conn.close()
            return True
        else:
            # Primera vez jugando - INSERT
            if os.environ.get('DATABASE_URL'):
                c.execute('INSERT INTO scores (name, attempts, device, user_id) VALUES (%s, %s, %s, %s)', 
                         (name, attempts, device, user_id))
            else:
                c.execute('INSERT INTO scores (name, attempts, device, user_id) VALUES (?, ?, ?, ?)', 
                         (name, attempts, device, user_id))
            conn.commit()
            conn.close()
            return True
    
    # Usuario invitado - no guardar (ya se maneja en adivina route)
    conn.close()
    return False

def get_top_scores(period='all'):
    conn = get_db_connection()
    c = conn.cursor()
    
    is_postgres = bool(os.environ.get('DATABASE_URL'))
    
    # Seleccionamos también el dispositivo
    query = 'SELECT name, attempts, device FROM scores'
    
    if period == 'weekly':
        if is_postgres:
            query += " WHERE created_at >= NOW() - INTERVAL '7 days'"
        else:
            query += " WHERE created_at >= datetime('now', '-7 days')"
    elif period == 'monthly':
        if is_postgres:
            query += " WHERE created_at >= NOW() - INTERVAL '30 days'"
        else:
            query += " WHERE created_at >= datetime('now', '-30 days')"
            
    query += ' ORDER BY attempts ASC LIMIT 5'
    
    c.execute(query)
    scores = c.fetchall()
    conn.close()
    return scores

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    return render_template('hub.html')

@app.route('/auth')
def auth_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('auth.html')

@app.route('/init-db')
def init_db_route():
    try:
        init_db()
        return "Base de datos inicializada correctamente (Tablas users y scores revisadas)."
    except Exception as e:
        return f"Error inicializando BD: {str(e)}"

# --- AUTH ROUTES ---
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {'success': False, 'message': 'Faltan datos'}
        
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        hashed_pw = generate_password_hash(password)
        if os.environ.get('DATABASE_URL'):
            c.execute('INSERT INTO users (username, password_hash) VALUES (%s, %s)', (username, hashed_pw))
        else:
            c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        
        # Auto login logic
        # Get the new user ID
        if os.environ.get('DATABASE_URL'):
            c.execute("SELECT id FROM users WHERE username = %s", (username,))
        else:
            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            
        user_id = c.fetchone()[0]
        
        session['user_id'] = user_id
        session['username'] = username
        
        # Check for pending score
        if 'pending_score' in session:
            score_data = session['pending_score']
            save_score(username, score_data['attempts'], score_data['device'], user_id)
            session.pop('pending_score', None)

        return {'success': True}
    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        return {'success': False, 'message': 'El usuario ya existe'}
    except Exception as e:
        print(f"Error en registro: {e}")
        return {'success': False, 'message': f'Error del servidor: {str(e)}'}
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    if os.environ.get('DATABASE_URL'):
        c.execute('SELECT id, password_hash FROM users WHERE username = %s', (username,))
    else:
        c.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['username'] = username
        
        # Check for pending score
        if 'pending_score' in session:
            score_data = session['pending_score']
            save_score(username, score_data['attempts'], score_data['device'], user[0])
            session.pop('pending_score', None)
            
        return {'success': True}
    
    return {'success': False, 'message': 'Usuario o contraseña incorrectos'}

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/check_auth')
def check_auth():
    if 'user_id' in session:
        return {'authenticated': True, 'username': session['username']}
    return {'authenticated': False}

@app.route('/adivina', methods=['GET', 'POST'])
def adivina():
    if request.method == 'POST':
        if 'guardar_score' in request.form:
            # Si está logueado, guardamos
            if 'user_id' in session:
                nombre = session['username']
                user_id = session['user_id']
                intentos_str = request.form.get('intentos_finales')
                device = request.form.get('device', 'Desktop')
                
                try:
                    intentos = int(intentos_str)
                except (ValueError, TypeError):
                    intentos = 999

                is_record = save_score(nombre, intentos, device, user_id)
                return redirect(url_for('adivina', saved='1', record=str(is_record).lower()))
            
            else:
                # GUEST MODE: No guardamos en DB, guardamos en sesión para registro posterior
                intentos_str = request.form.get('intentos_finales')
                device = request.form.get('device', 'Desktop')
                try:
                    intentos = int(intentos_str)
                except (ValueError, TypeError):
                    intentos = 999
                
                session['pending_score'] = {'attempts': intentos, 'device': device}
                return redirect(url_for('adivina', guest_score=intentos))

    # Por defecto mostramos el global
    top_scores = get_top_scores('all')
    saved = request.args.get('saved')
    record = request.args.get('record') # 'true' or 'false'
    guest_score = request.args.get('guest_score')
    
    # Obtener el personal best del usuario si está logueado
    user_best = None
    if 'user_id' in session:
        conn = get_db_connection()
        c = conn.cursor()
        if os.environ.get('DATABASE_URL'):
            c.execute('SELECT MIN(attempts) FROM scores WHERE user_id = %s', (session['user_id'],))
        else:
            c.execute('SELECT MIN(attempts) FROM scores WHERE user_id = ?', (session['user_id'],))
        result = c.fetchone()
        user_best = result[0] if result and result[0] is not None else None
        conn.close()
    
    return render_template('game.html', top_scores=top_scores, saved=saved, record=record, guest_score=guest_score, user_best=user_best)

@app.route('/api/rankings/<period>')
def api_rankings(period):
    if period not in ['all', 'weekly', 'monthly']:
        period = 'all'
    scores = get_top_scores(period)
    
    scores_list = []
    for s in scores:
        name = s[0]
        attempts = s[1]
        device = s[2] if len(s) > 2 and s[2] else 'Desktop'
        
        # --- BADGE LOGIC ---
        badges = []
        
        # 1. Device Badge
        if device == 'Mobile':
            badges.append({'icon': '📱', 'title': 'Jugador Móvil', 'class': 'badge-mobile'})
        else:
            badges.append({'icon': '💻', 'title': 'Jugador PC', 'class': 'badge-desktop'})
            
        # 2. Performance Badges
        if attempts == 1:
            badges.append({'icon': '🎯', 'title': 'Francotirador (1 intento)', 'class': 'badge-sniper'})
        elif attempts <= 4:
            badges.append({'icon': '🧠', 'title': 'Genio (2-4 intentos)', 'class': 'badge-genius'})
        elif attempts <= 7:
            badges.append({'icon': '⚡', 'title': 'Veloz (5-7 intentos)', 'class': 'badge-fast'})
        elif attempts > 10:
            badges.append({'icon': '🐢', 'title': 'Persistente (>10 intentos)', 'class': 'badge-persistent'})

        scores_list.append({
            'name': name, 
            'attempts': attempts, 
            'device': device,
            'badges': badges
        })
        
    return {'scores': scores_list}

@app.route('/versus')
def versus_lobby():
    """Lobby page for creating or joining rooms."""
    return render_template('versus_lobby.html')

@app.route('/versus/<room_code>')
def versus_game(room_code):
    """Game room page."""
    return render_template('versus_game.html', room_code=room_code)

if __name__ == '__main__':
    socketio.run(app, debug=True)
