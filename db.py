import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": "mis_socios",
    "user": "bot_master",
    "password": "Abundancia2026",
    "host": "localhost",
    "port": "5432"
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def obtener_usuario(telegram_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM usuarios WHERE telegram_id = %s;", (telegram_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def crear_usuario(telegram_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO usuarios (telegram_id) VALUES (%s) RETURNING id;", 
        (telegram_id,)
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def actualizar_campo_usuario(telegram_id, campo, valor):
    conn = get_connection()
    cur = conn.cursor()
    query = f"UPDATE usuarios SET {campo} = %s WHERE telegram_id = %s;"
    cur.execute(query, (valor, telegram_id))
    conn.commit()
    cur.close()
    conn.close()

def borrar_usuario(telegram_id):
    """Borra absolutamente todo el rastro del usuario de la Matrix"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE telegram_id = %s;", (telegram_id,))
    conn.commit()
    cur.close()
    conn.close()
