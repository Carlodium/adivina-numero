import os
import sqlite3
from datetime import datetime

def get_db_connection():
    """Conectar a la base de datos"""
    database_url = os.environ.get('DATABASE_URL')
    
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    if database_url:
        try:
            import psycopg2
            print("🔌 Conectando a PostgreSQL...")
            return psycopg2.connect(database_url)
        except ImportError:
            print("❌ Error: No tienes instalado 'psycopg2'.")
            return None
    else:
        db_path = 'scores.db'
        if os.path.exists(db_path):
            print(f"🔌 Conectando a SQLite ({db_path})...")
        else:
            print(f"⚠️  AVISO: No encuentro '{db_path}' en este directorio.")
            
        return sqlite3.connect(db_path)

def list_users():
    conn = get_db_connection()
    c = conn.cursor()
    
    print("\n" + "="*85)
    print(f"{'ID':<5} | {'USUARIO':<20} | {'CREADO':<25} | {'ÚLTIMA ACTIVIDAD':<25}")
    print("="*85)
    
    try:
        # Get all users
        if os.environ.get('DATABASE_URL'):
            c.execute("SELECT id, username, created_at FROM users ORDER BY id ASC")
        else:
            c.execute("SELECT id, username, created_at FROM users ORDER BY id ASC")
            
        users = c.fetchall()
        
        for user in users:
            user_id = user[0]
            username = user[1]
            created_at = user[2]
            
            # Get last activity (latest score)
            if os.environ.get('DATABASE_URL'):
                c.execute("SELECT MAX(created_at) FROM scores WHERE user_id = %s", (user_id,))
            else:
                c.execute("SELECT MAX(created_at) FROM scores WHERE user_id = ?", (user_id,))
                
            last_score_date = c.fetchone()[0]
            
            last_activity = last_score_date if last_score_date else "Sin partidas"
            
            # Format dates if they are strings (SQLite) or datetime objects (Postgres)
            # For simplicity in display, just converting to string usually works well enough
            
            print(f"{user_id:<5} | {username:<20} | {str(created_at):<25} | {str(last_activity):<25}")
            
    except Exception as e:
        print(f"Error al leer la base de datos: {e}")
        print("Asegúrate de que la base de datos 'scores.db' existe y tiene la tabla 'users'.")

    print("="*85)
    print(f"Total: {len(users)} usuarios registrados.\n")
    conn.close()
    
    input("Presiona ENTER para salir...")

if __name__ == "__main__":
    list_users()
