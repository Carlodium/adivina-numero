from flask import Flask, render_template, request, session, redirect, url_for
import random
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

def init_db():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (name TEXT, attempts INTEGER)''')
    conn.commit()
    conn.close()

def get_top_scores():
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('SELECT name, attempts FROM scores ORDER BY attempts ASC LIMIT 5')
    scores = c.fetchall()
    conn.close()
    return scores

def save_score(name, attempts):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('INSERT INTO scores (name, attempts) VALUES (?, ?)', (name, attempts))
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'numero_secreto' not in session:
        session['numero_secreto'] = random.randint(1, 100)
        session['intentos'] = 0
        session['mensaje'] = "He pensado un número entre 1 y 100. ¿Puedes adivinar cuál es?"
        session['juego_terminado'] = False
        session['pidiendo_nombre'] = False

    if request.method == 'POST':
        if 'reiniciar' in request.form:
            session.pop('numero_secreto', None)
            return redirect(url_for('index'))

        if 'guardar_score' in request.form:
            nombre = request.form.get('nombre')
            if nombre:
                save_score(nombre, session['intentos'])
                session['mensaje'] = f"¡Guardado! {nombre} con {session['intentos']} intentos."
                session['pidiendo_nombre'] = False
            return redirect(url_for('index'))

        if not session.get('juego_terminado'):
            entrada = request.form.get('intento')
            
            if not entrada:
                 session['mensaje'] = "Por favor, escribe algo."
            else:
                try:
                    estimacion = int(entrada)
                    session['intentos'] += 1
                    
                    if estimacion < session['numero_secreto']:
                        session['mensaje'] = f"El número {estimacion} es demasiado bajo. ¡Inténtalo de nuevo!"
                    elif estimacion > session['numero_secreto']:
                        session['mensaje'] = f"El número {estimacion} es demasiado alto. ¡Inténtalo de nuevo!"
                    else:
                        session['mensaje'] = f"¡Felicidades! Has adivinado el número {session['numero_secreto']} en {session['intentos']} intentos."
                        session['juego_terminado'] = True
                        session['pidiendo_nombre'] = True
                except ValueError:
                    session['mensaje'] = "Por favor, introduce un número válido."

    top_scores = get_top_scores()
    return render_template('index.html', 
                         mensaje=session.get('mensaje'), 
                         intentos=session.get('intentos'),
                         juego_terminado=session.get('juego_terminado'),
                         pidiendo_nombre=session.get('pidiendo_nombre'),
                         top_scores=top_scores)

if __name__ == '__main__':
    app.run(debug=True)
