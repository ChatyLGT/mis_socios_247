import os, psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

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
    # Forzamos 'NUEVO' solo si el registro no existe
    cur.execute("""
        INSERT INTO usuarios (telegram_id, estado_onboarding) 
        VALUES (%s, 'NUEVO') 
        ON CONFLICT (telegram_id) DO NOTHING;
    """, (telegram_id,))
    conn.commit()
    cur.close()
    conn.close()

def inicializar_adn(telegram_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO adn_negocios (usuario_id) SELECT id FROM usuarios WHERE telegram_id = %s ON CONFLICT DO NOTHING;", (telegram_id,))
    conn.commit()
    cur.close()
    conn.close()

def actualizar_campo_usuario(telegram_id, campo, valor):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE usuarios SET {campo} = %s WHERE telegram_id = %s;", (valor, telegram_id))
    conn.commit()
    cur.close()
    conn.close()

def actualizar_adn(telegram_id, campo, valor):
    conn = get_connection()
    cur = conn.cursor()
    query = f"UPDATE adn_negocios SET {campo} = %s WHERE usuario_id = (SELECT id FROM usuarios WHERE telegram_id = %s);"
    cur.execute(query, (valor, telegram_id))
    conn.commit()
    cur.close()
    conn.close()

def obtener_contexto_negocio(telegram_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT nombre_empresa FROM adn_negocios an JOIN usuarios u ON an.usuario_id = u.id WHERE u.telegram_id = %s", (telegram_id,))
    res = cur.fetchone()
    cur.close()
    conn.close()
    return res['nombre_empresa'] if res and res.get('nombre_empresa') else ""

def borrar_usuario(telegram_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM adn_negocios WHERE usuario_id = (SELECT id FROM usuarios WHERE telegram_id = %s)", (telegram_id,))
    cur.execute("DELETE FROM usuarios WHERE telegram_id = %s", (telegram_id,))
    conn.commit()
    cur.close()
    conn.close()
