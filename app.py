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
    
    # Verificar si la tabla existe y tiene la columna id
    try:
        c.execute('SELECT id FROM scores LIMIT 1')
    except:
        # Si falla, es que no existe o es la versión vieja. Borramos y creamos de nuevo.
        conn.rollback() # Necesario en Postgres si hay error
        c.execute('DROP TABLE IF EXISTS scores')
        conn.commit()
        
        # Crear tabla nueva con ID
        if os.environ.get('DATABASE_URL'):
            # PostgreSQL
            c.execute('''CREATE TABLE scores
                         (id SERIAL PRIMARY KEY,
                          name TEXT,
                          attempts INTEGER)''')
        else:
            # SQLite
            c.execute('''CREATE TABLE scores
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          attempts INTEGER)''')
    
    conn.commit()
    conn.close()

def get_top_scores():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT name, attempts FROM scores ORDER BY attempts ASC LIMIT 5')
    scores = c.fetchall()
    conn.close()
    return scores

def save_score(name, attempts):
    conn = get_db_connection()
    c = conn.cursor()
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
                intentos = 999 # Fallback por si acaso

            # Validar nombre: máximo 16 caracteres, permite letras, números, guiones y espacios
            if nombre and len(nombre) <= 16 and nombre.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                save_score(nombre, intentos)
            
            return redirect(url_for('index'))

    top_scores = get_top_scores()
    return render_template('index.html', top_scores=top_scores)

if __name__ == '__main__':
    app.run(debug=True)
