"""
Script para gestionar la base de datos de puntuaciones.
Ejecuta este archivo para borrar todas las puntuaciones o ver las actuales.
"""

import os

def get_db_connection():
    """Conectar a la base de datos"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        import psycopg2
        return psycopg2.connect(database_url)
    else:
        import sqlite3
        conn = sqlite3.connect('scores.db')
        # Asegurar que la tabla existe
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scores
                     (name TEXT, attempts INTEGER)''')
        conn.commit()
        return conn

def ver_todas_puntuaciones():
    """Mostrar todas las puntuaciones"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT name, attempts FROM scores ORDER BY attempts ASC')
    scores = c.fetchall()
    conn.close()
    
    if scores:
        print("\n🏆 ¡AQUÍ ESTÁN LOS CAMPEONES! 🏆")
        print("=" * 40)
        for i, (name, attempts) in enumerate(scores, 1):
            print(f"  {i}. {name} --> {attempts} intentos")
        print("=" * 40)
        print(f"Total: {len(scores)} puntuaciones registradas.")
    else:
        print("\n📭 La lista está vacía...")
        print("¡Nadie ha jugado todavía (o has borrado todo)!")
        print("¡Es tu oportunidad de ser el primero! 🥇")
    
    return len(scores)

def borrar_todas_puntuaciones():
    """Borrar TODAS las puntuaciones"""
    print("\n🚨 ¡CUIDADO! ESTÁS A PUNTO DE BORRAR TODO 🚨")
    print("Esto eliminará permanentemente el historial de todos los jugadores.")
    respuesta = input("¿Estás 100% seguro? Escribe 'BORRAR' para confirmar: ")
    
    if respuesta == 'BORRAR':
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM scores')
        conn.commit()
        conn.close()
        print("\n✨ ¡Puf! Todo ha desaparecido.")
        print("La base de datos está limpia como una patena.")
    else:
        print("\n😅 ¡Uff! Operación cancelada.")
        print("Los datos están a salvo.")

def borrar_puntuacion_especifica():
    """Borrar una puntuación específica por nombre"""
    print("\n🕵️  MODO DETECTIVE: Borrar un jugador específico")
    nombre = input("Escribe el nombre EXACTO del jugador que quieres borrar: ")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Primero verificamos si existe
    c.execute('SELECT COUNT(*) FROM scores WHERE name = %s' if os.environ.get('DATABASE_URL') else 'SELECT COUNT(*) FROM scores WHERE name = ?', (nombre,))
    count = c.fetchone()[0]
    
    if count == 0:
        print(f"\n❌ Mmm... No encuentro a nadie llamado '{nombre}'.")
        print("¿Seguro que lo escribiste bien? Revisa mayúsculas y minúsculas.")
    else:
        c.execute('DELETE FROM scores WHERE name = %s' if os.environ.get('DATABASE_URL') else 'DELETE FROM scores WHERE name = ?', (nombre,))
        conn.commit()
        print(f"\n✅ ¡Listo! He borrado {count} registro(s) de '{nombre}'.")
        print("¡Adiós popó! 👋")
    
    conn.close()

def menu():
    """Menú principal"""
    while True:
        print("\n" + "="*40)
        print("🎲 GESTOR DE PUNTUACIONES")
        print("="*40)
        print("1. Ver todas las puntuaciones")
        print("2. Borrar TODAS las puntuaciones")
        print("3. Borrar una puntuación específica")
        print("4. Salir")
        print("="*40)
        
        opcion = input("\nElige una opción (1-4): ")
        
        if opcion == '1':
            ver_todas_puntuaciones()
        elif opcion == '2':
            ver_todas_puntuaciones()
            borrar_todas_puntuaciones()
        elif opcion == '3':
            total = ver_todas_puntuaciones()
            if total > 0:
                borrar_puntuacion_especifica()
        elif opcion == '4':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("\n❌ Opción inválida. Elige 1, 2, 3 o 4.")

if __name__ == '__main__':
    menu()
