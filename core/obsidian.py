import psycopg2, os
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    db_url = os.getenv("DATABASE_URL")
    if db_url: return psycopg2.connect(db_url)
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "mis_socios"),
        user=os.getenv("DB_USER", "bot_master"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost")
    )

def guardar_documento(telegram_id, nombre_documento, contenido):
    try:
        conn = obtener_conexion()
        with conn.cursor() as cur:
            query = """
            INSERT INTO boveda_obsidian (telegram_id, nombre_documento, contenido_md, fecha_actualizacion)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (telegram_id, nombre_documento)
            DO UPDATE SET contenido_md = EXCLUDED.contenido_md, fecha_actualizacion = CURRENT_TIMESTAMP;
            """
            cur.execute(query, (telegram_id, nombre_documento, contenido))
        conn.commit()
    except Exception as e:
        print(f"❌ Error escribiendo en Bóveda: {e}")
    finally:
        if 'conn' in locals(): conn.close()

def leer_documento(telegram_id, nombre_documento):
    try:
        conn = obtener_conexion()
        with conn.cursor() as cur:
            cur.execute("SELECT contenido_md FROM boveda_obsidian WHERE telegram_id = %s AND nombre_documento = %s", (telegram_id, nombre_documento))
            res = cur.fetchone()
            return res[0] if res else "Aún no hay datos acumulados."
    except Exception as e:
        print(f"❌ Error leyendo Bóveda: {e}")
        return "Aún no hay datos acumulados."
    finally:
        if 'conn' in locals(): conn.close()
