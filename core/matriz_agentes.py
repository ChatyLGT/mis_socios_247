import psycopg2, os
from dotenv import load_dotenv

load_dotenv()

def obtener_personalidad(id_agente):
    try:
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "mis_socios"),
                user=os.getenv("DB_USER", "bot_master"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST", "localhost")
            )
        with conn.cursor() as cur:
            cur.execute("SELECT nombre, rol_crewai, objetivo_goal, soul_backstory, playbook_reglas, voice_tono FROM agentes_personalidad WHERE id_agente = %s", (id_agente,))
            res = cur.fetchone()
            if res:
                return {
                    "nombre": res[0], "rol": res[1], "goal": res[2],
                    "soul": res[3], "playbook": res[4], "voice": res[5]
                }
    except Exception as e:
        print(f"❌ Error leyendo matriz de agentes: {e}")
    finally:
        if 'conn' in locals(): conn.close()
    return None
