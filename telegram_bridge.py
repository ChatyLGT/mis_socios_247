import os, asyncio, datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import vault_manager
from agentes import javier, rene, ana, marce

TOKEN = "8594149893:AAGkStafzVqA41MqU1YQfICAI4S_UoW2Euc"
os.environ["GOOGLE_API_KEY"] = "AIzaSyD_7E4JBtzLOhS459zKtVSA9qGFGcBan68"

contexto_socios = {}
SOCIOS = {
    "javier": {"nombre": "Javier (Legal)", "mod": javier},
    "javi": {"nombre": "Javier (Legal)", "mod": javier},
    "rene": {"nombre": "René (IT)", "mod": rene},
    "rené": {"nombre": "René (IT)", "mod": rene},
    "ana": {"nombre": "Ana (Negocios)", "mod": ana},
    "marce": {"nombre": "Marce (Ventas)", "mod": marce}
}

async def handle_everything(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    user_id = update.message.from_user.id
    msg = update.message
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"\n--- [LOG {timestamp}] INTERACCIÓN ---")

    # 1. GESTIÓN DE ARCHIVOS (CORREGIDO: Evita IndexError)
    file_path = None
    if msg.voice:
        file_path = f"vault_{user_id}.ogg"
        file = await msg.voice.get_file()
    elif msg.photo:
        file_path = f"vault_{user_id}.jpg"
        file = await msg.photo[-1].get_file()
    elif msg.document:
        file_path = msg.document.file_name
        file = await msg.document.get_file()

    contexto_file = ""
    if file_path:
        print(f"LOG: Descargando archivo {file_path}...")
        await file.download_to_drive(file_path)
        contexto_file = vault_manager.analizar_archivo(file_path, "Sistema de Despacho")
        print(f"📄 CONTENIDO ARCHIVO: {contexto_file[:200]}...")

    # 2. UNIFICACIÓN DE TEXTO (Gunnar + Transcripción)
    texto_escrito = msg.text or msg.caption or ""
    # El bot ahora analiza AMBOS para decidir el cambio de socio
    texto_para_analizar = (texto_escrito + " " + contexto_file).lower()
    
    print(f"👤 GUNNAR: '{texto_escrito}'")
    
    # 3. TRASPASO INTELIGENTE (Funciona con Voz y Texto)
    for clave, data in SOCIOS.items():
        if clave in texto_para_analizar:
            if not contexto_socios.get(user_id) or contexto_socios[user_id]['nombre'] != data['nombre']:
                print(f"🔄 TRASPASO EJECUTADO -> {data['nombre']}")
                contexto_socios[user_id] = data
                await msg.reply_text(f"🤝 Cambio de socio: Ahora hablas con {data['nombre']}")
            break

    socio_actual = contexto_socios.get(user_id)
    if not socio_actual:
        await msg.reply_text("¿Con quién hablo? (Javier, René, Ana o Marce)")
        return

    # 4. RESPUESTA DEL SOCIO CON LOG COMPLETO
    print(f"🧠 {socio_actual['nombre']} PENSANDO...")
    try:
        loop = asyncio.get_event_loop()
        prompt_final = f"Gunnar te dice: '{texto_escrito}'. Contexto de archivo: '{contexto_file}'. RESPONDÉ BREVE Y COMO SOCIO PORTEÑO."
        
        res = await loop.run_in_executor(None, socio_actual['mod'].ejecutar, prompt_final, contexto_file)
        
        print(f"🤖 RESPUESTA DE {socio_actual['nombre']}:\n{res}")
        
        for chunk in [res[i:i+4000] for i in range(0, len(res), 4000)]:
            await msg.reply_text(f"*{socio_actual['nombre']}*:\n{chunk}", parse_mode='Markdown')
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        if file_path and os.path.exists(file_path): os.remove(file_path)

if __name__ == '__main__':
    print("🚀 SISTEMA RESETEADO Y LOGS ACTIVOS. Esperando...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_everything))
    app.run_polling()
