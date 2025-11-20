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
    # Si es GET y el juego terminó y ya no está pidiendo nombre, reiniciar
    if request.method == 'GET' and session.get('juego_terminado') and not session.get('pidiendo_nombre'):
        session.clear()
    
    if 'numero_secreto' not in session:
        session['numero_secreto'] = random.randint(1, 100)
        session['intentos'] = 0
        session['mensaje'] = "He pensado un número entre 1 y 100. ¿Puedes adivinar cuál es?"
        session['juego_terminado'] = False
        session['pidiendo_nombre'] = False
        session['intentos_previos'] = []  # Lista para guardar números ya dichos

    if request.method == 'POST':
        if 'reiniciar' in request.form:
            session.pop('numero_secreto', None)
            return redirect(url_for('index'))

        if 'guardar_score' in request.form:
            nombre = request.form.get('nombre', '').strip()
            # Validar nombre: máximo 16 caracteres, permite letras, números, guiones y espacios
            # .replace(' ', '') permite validar que el resto sean caracteres válidos
            if nombre and len(nombre) <= 16 and nombre.replace('_', '').replace('-', '').replace(' ', '').isalnum():
                save_score(nombre, session['intentos'])
                session.clear()  # Limpiar sesión para empezar de nuevo
            else:
                session['mensaje'] = "Nombre inválido. Máx 16 caracteres. Solo letras, números y espacios."
                session['pidiendo_nombre'] = True
            return redirect(url_for('index'))

        if not session.get('juego_terminado'):
            entrada = request.form.get('intento')
            
            if not entrada or not entrada.strip():
                 session['mensaje'] = "¡No has escrito nada! Por favor, introduce un número."
            else:
                try:
                    estimacion = int(entrada)
                    
                    # Validaciones que NO cuentan como intento
                    if estimacion < 1 or estimacion > 100:
                        session['mensaje'] = f"¡Oye! El {estimacion} no vale. Tiene que ser entre 1 y 100."
                    elif estimacion in session['intentos_previos']:
                        session['mensaje'] = f"¡Ya dijiste el {estimacion}! Prueba con otro diferente."
                    else:
                        # Si pasa todas las validaciones, AHORA SÍ cuenta como intento
                        session['intentos'] += 1
                        session['intentos_previos'].append(estimacion)
                        
                        if estimacion < session['numero_secreto']:
                            session['mensaje'] = f"El número {estimacion} es demasiado bajo. ¡Inténtalo de nuevo!"
                        elif estimacion > session['numero_secreto']:
                            session['mensaje'] = f"El número {estimacion} es demasiado alto. ¡Inténtalo de nuevo!"
                        else:
                            session['mensaje'] = f"¡Felicidades! Has adivinado el número {session['numero_secreto']} en {session['intentos']} intentos."
                            session['juego_terminado'] = True
                            session['pidiendo_nombre'] = True
                            
                except ValueError:
                    session['mensaje'] = "Eso no parece un número válido. ¡Inténtalo otra vez!"

    top_scores = get_top_scores()
    return render_template('index.html', 
                         mensaje=session.get('mensaje'), 
                         intentos=session.get('intentos'),
                         juego_terminado=session.get('juego_terminado'),
                         pidiendo_nombre=session.get('pidiendo_nombre'),
                         top_scores=top_scores)

if __name__ == '__main__':
    app.run(debug=True)
