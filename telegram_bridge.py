import os, asyncio, datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import vault_manager
from agentes import javier, rene, ana, marce

# CARGA DE SECRETOS DESDE .ENV
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
TOKEN = os.getenv("TELEGRAM_TOKEN")

contexto_socios = {}
SOCIOS = {
    "javier": {"nombre": "Javier (Legal)", "mod": javier},
    "javi": {"nombre": "Javier (Legal)", "mod": javier},
    "rene": {"nombre": "René (IT)", "mod": rene},
    "rené": {"nombre": "René (IT)", "mod": rene},
    "ana": {"nombre": "Ana (Negocios)", "mod": ana},
    "marce": {"nombre": "Marce (Ventas)", "mod": marce}
}

async def ejecutar_agente(socio_data, msg, texto_usuario, contexto_file):
    nombre = socio_data['nombre']
    print(f"🧠 {nombre} PENSANDO...")
    try:
        loop = asyncio.get_event_loop()
        prompt = f"Gunnar dice: '{texto_usuario}'. Contexto archivo: '{contexto_file}'. RESPONDÉ BREVE Y COMO SOCIO PORTEÑO."
        res = await loop.run_in_executor(None, socio_data['mod'].ejecutar, prompt, contexto_file)
        print(f"🤖 RESPUESTA DE {nombre}:\n{res}")
        await msg.reply_text(f"*{nombre}*:\n{res}", parse_mode='Markdown')
        return True
    except Exception as e:
        print(f"❌ ERROR EN {nombre}: {e}")
        return False

async def handle_everything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    user_id = update.message.from_user.id
    msg = update.message
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    texto_usuario = msg.text or msg.caption or ""
    print(f"\n--- [LOG {timestamp}] INTERACCIÓN ---")

    file_path = None
    if msg.voice:
        file_path = f"vault_{user_id}.ogg"
        file = await msg.voice.get_file()
    elif msg.photo and len(msg.photo) > 0:
        file_path = f"vault_{user_id}.jpg"
        file = await msg.photo[-1].get_file()
    elif msg.document:
        file_path = msg.document.file_name
        file = await msg.document.get_file()

    contexto_file = ""
    if file_path:
        await file.download_to_drive(file_path)
        contexto_file = vault_manager.analizar_archivo(file_path, "Sistema")

    texto_total = (texto_usuario + " " + contexto_file).lower()
    es_grupal = any(x in texto_total for x in ["todos", "equipo", "muchachos", "consejo", "board"])

    if es_grupal:
        await msg.reply_text("🎙️ *Iniciando sesión de consejo...*", parse_mode='Markdown')
        for clave in ["rene", "ana", "javier", "marce"]:
            await ejecutar_agente(SOCIOS[clave], msg, texto_usuario, contexto_file)
            await asyncio.sleep(1)
    else:
        for clave, data in SOCIOS.items():
            if clave in texto_total:
                contexto_socios[user_id] = data
                break
        
        socio_actual = contexto_socios.get(user_id)
        if socio_actual:
            await ejecutar_agente(socio_actual, msg, texto_usuario, contexto_file)
        else:
            await msg.reply_text("¿Con quién hablo? (Javier, René, Ana o Marce)")

    if file_path and os.path.exists(file_path): os.remove(file_path)

if __name__ == '__main__':
    print("🚀 SISTEMA SEGURO Y MODO SALA DE JUNTAS ONLINE.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_everything))
    app.run_polling()
