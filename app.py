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
    
    # Para asegurar que tenemos la columna created_at, vamos a recrear la tabla
    # En producción idealmente haríamos una migración, pero para este prototipo es más eficaz
    try:
        # Verificar si existe la columna created_at
        c.execute('SELECT created_at FROM scores LIMIT 1')
    except:
        conn.rollback()
        c.execute('DROP TABLE IF EXISTS scores')
        conn.commit()
        
        if os.environ.get('DATABASE_URL'):
            # PostgreSQL
            c.execute('''CREATE TABLE scores
                         (id SERIAL PRIMARY KEY,
                          name TEXT,
                          attempts INTEGER,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        else:
            # SQLite
            c.execute('''CREATE TABLE scores
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          attempts INTEGER,
                          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()

def get_top_scores(period='all'):
    conn = get_db_connection()
    c = conn.cursor()
    
    is_postgres = bool(os.environ.get('DATABASE_URL'))
    
    query = 'SELECT name, attempts FROM scores'
    params = []
    
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
    
    c.execute(query, params)
    scores = c.fetchall()
    conn.close()
    return scores

def save_score(name, attempts):
    conn = get_db_connection()
    c = conn.cursor()
    # created_at se pone solo por el DEFAULT
    c.execute('INSERT INTO scores (name, attempts) VALUES (%s, %s)', (name, attempts))
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'guardar_score' in request.form:
            nombre = request.form.get('nombre', '').strip()
            intentos_str = request.form.get('intentos_finales')
            
            try:
                intentos = int(intentos_str)
            except (ValueError, TypeError):
                intentos = 999

            if nombre and len(nombre) <= 16 and nombre.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                save_score(nombre, intentos)
                return redirect(url_for('index', saved='1'))
            
            return redirect(url_for('index'))

    # Por defecto mostramos el global
    top_scores = get_top_scores('all')
    saved = request.args.get('saved')
    return render_template('index.html', top_scores=top_scores, saved=saved)

@app.route('/api/rankings/<period>')
def api_rankings(period):
    if period not in ['all', 'weekly', 'monthly']:
        period = 'all'
    scores = get_top_scores(period)
    # Convertir a lista de dicts para JSON
    scores_list = [{'name': s[0], 'attempts': s[1]} for s in scores]
    return {'scores': scores_list}

if __name__ == '__main__':
    app.run(debug=True)
