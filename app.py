from flask import Flask, render_template, request, session, redirect, url_for
import random
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    """Get database connection from environment variable or use SQLite locally"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # PostgreSQL (production on Render)
        return psycopg2.connect(database_url)
    else:
        # SQLite (local development)
        import sqlite3
        return sqlite3.connect('scores.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Crear tabla si no existe
    # Nota: En SQLite usamos AUTOINCREMENT, en Postgres SERIAL (que se maneja al crear).
    # Para simplificar la query compatible, asumimos creación básica.
    # Si es Postgres, la tabla persistente ya existe.
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    except Exception:
        # Fallback para SQLite local si falla la sintaxis de Postgres
        try:
            c.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    attempts INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        except Exception:
            pass

    # Migración: Añadir columna 'device' si no existe
    try:
        # Intentamos añadir la columna. Si ya existe, fallará y lo ignoramos.
        c.execute('ALTER TABLE scores ADD COLUMN device TEXT DEFAULT \'Desktop\'')
        conn.commit()
    except Exception:
        conn.rollback()
        
    conn.commit()
    conn.close()

def save_score(name, attempts, device):
    conn = get_db_connection()
    c = conn.cursor()
    # created_at se pone solo por el DEFAULT
    c.execute('INSERT INTO scores (name, attempts, device) VALUES (%s, %s, %s)', (name, attempts, device))
    conn.commit()
    conn.close()

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

@app.route('/adivina', methods=['GET', 'POST'])
def adivina():
    if request.method == 'POST':
        if 'guardar_score' in request.form:
            nombre = request.form.get('nombre', '').strip()
            intentos_str = request.form.get('intentos_finales')
            device = request.form.get('device', 'Desktop') # Recibir dispositivo
            
            try:
                intentos = int(intentos_str)
            except (ValueError, TypeError):
                intentos = 999

            if nombre and len(nombre) <= 16 and nombre.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                save_score(nombre, intentos, device)
                return redirect(url_for('adivina', saved='1'))
            
            return redirect(url_for('adivina'))

    # Por defecto mostramos el global
    top_scores = get_top_scores('all')
    saved = request.args.get('saved')
    return render_template('game.html', top_scores=top_scores, saved=saved)

@app.route('/api/rankings/<period>')
def api_rankings(period):
    if period not in ['all', 'weekly', 'monthly']:
        period = 'all'
    scores = get_top_scores(period)
    # Incluir device en la respuesta JSON
    # s[0]=name, s[1]=attempts, s[2]=device (si existe, sino Desktop)
    scores_list = []
    for s in scores:
        device = s[2] if len(s) > 2 and s[2] else 'Desktop'
        scores_list.append({'name': s[0], 'attempts': s[1], 'device': device})
        
    return {'scores': scores_list}

if __name__ == '__main__':
    app.run(debug=True)
