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
        return sqlite3.connect('scores.db')

def ver_todas_puntuaciones():
    """Mostrar todas las puntuaciones"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT name, attempts FROM scores ORDER BY attempts ASC')
    scores = c.fetchall()
    conn.close()
    
    if scores:
        print("\n🏆 TODAS LAS PUNTUACIONES:")
        print("-" * 40)
        for i, (name, attempts) in enumerate(scores, 1):
            print(f"{i}. {name} - {attempts} intentos")
        print("-" * 40)
    else:
        print("\n❌ No hay puntuaciones guardadas.")
    
    return len(scores)

def borrar_todas_puntuaciones():
    """Borrar TODAS las puntuaciones"""
    respuesta = input("\n⚠️  ¿Estás seguro de que quieres BORRAR TODAS las puntuaciones? (sí/no): ")
    if respuesta.lower() in ['sí', 'si', 's', 'yes', 'y']:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM scores')
        conn.commit()
        conn.close()
        print("\n✅ ¡Todas las puntuaciones han sido borradas!")
    else:
        print("\n❌ Operación cancelada.")

def borrar_puntuacion_especifica():
    """Borrar una puntuación específica por nombre"""
    nombre = input("\n📝 Escribe el nombre exacto de la puntuación a borrar: ")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM scores WHERE name = %s' if os.environ.get('DATABASE_URL') else 'DELETE FROM scores WHERE name = ?', (nombre,))
    filas_borradas = c.rowcount
    conn.commit()
    conn.close()
    
    if filas_borradas > 0:
        print(f"\n✅ Se borraron {filas_borradas} puntuación(es) de '{nombre}'")
    else:
        print(f"\n❌ No se encontró ninguna puntuación con el nombre '{nombre}'")

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
