import os, asyncio, tempfile
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import db
from core.borrado import ejecutar_borrado_total
from core.registro import manejar_paso_registro
from core.grabadora import log_terminal
from core.parser import parsear_evento
from flujos.onboarding_hostess import manejar_onboarding
from flujos.pepe_flow import manejar_pepe
from flujos.maria_flow import manejar_maria
from flujos.josefina_flow import manejar_josefina
from flujos.fausto_flow import manejar_fausto

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def descargar_medio(update, context):
    msg = update.message
    file = None
    if msg and msg.photo: file = await msg.photo[-1].get_file()
    elif msg and msg.document: file = await msg.document.get_file()
    elif msg and msg.voice: file = await msg.voice.get_file()
    elif msg and msg.audio: file = await msg.audio.get_file()
    if file:
        ext = file.file_path.split('.')[-1]
        path = os.path.join(tempfile.gettempdir(), f"{file.file_id}.{ext}")
        await file.download_to_drive(path)
        return path
    return None

async def catch_all(update, context):
    identidad, tipo, contenido, user_data = parsear_evento(update)
    user = update.effective_user
    if not user: return

    db_user = db.obtener_usuario(user.id)
    estado = db_user.get('estado_onboarding') if db_user else "NUEVO"
    log_terminal(f"{tipo} | ESTADO: {estado}", identidad, contenido)
    
    # TRIPLE CHECK: Solo creamos/sobrescribimos el perfil si es un usuario NUEVO.
    # Si ya está en medio del onboarding, NO tocamos su nombre de la base de datos.
    if estado == "NUEVO":
        db.crear_usuario(user.id, user_data['username'], 
                        f"{user_data['first_name'] or ''} {user_data['last_name'] or ''}".strip(), 
                        user_data['language_code'])

    file_path = await descargar_medio(update, context)

    if estado == "FAUSTO_ACTIVO":
        await manejar_fausto(update, context, user.id, contenido)
    elif estado == "JOSEFINA_ACTIVO":
        await manejar_josefina(update, context, user.id, contenido)
    elif estado == "MARIA_ACTIVO":
        await manejar_maria(update, context, user.id, contenido)
    elif estado == "PEPE_ACTIVO":
        await manejar_pepe(update, context, user.id, contenido, file_path)
    else:
        await manejar_onboarding(update, context, user.id, estado, contenido, file_path)

async def manejar_callback(update, context):
    identidad, tipo, contenido, user_data = parsear_evento(update)
    query = update.callback_query
    user = update.effective_user
    if not user: return
    log_terminal(tipo, identidad, contenido)
    await query.answer()

    if query.data == "start_flow":
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "WHATSAPP")
        await manejar_paso_registro(update, context)
    elif query.data == "acepto_tyc":
        db.actualizar_campo_usuario(user.id, "status_legal", True)
        db.inicializar_adn(user.id)
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "DATOS_GENERALES")
        await manejar_onboarding(update, context, user.id, "DATOS_GENERALES", "Acepto")
    elif query.data == "enviar_generales":
        await context.bot.send_message(chat_id=user.id, text="⏳ Entendido. Por favor, escribe tu Nombre, Correo y Negocio en un solo mensaje. Te estoy leyendo...")
    elif query.data == "confirmacion_ok":
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "PASO_PEPE")
        await manejar_onboarding(update, context, user.id, "PASO_PEPE", "Confirmado")
    elif query.data == "confirmacion_error":
        await context.bot.send_message(chat_id=user.id, text="✏️ Entendido. Por favor, decime qué dato está mal y cuál es el correcto.")
    elif query.data == "ir_a_pepe":
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "PEPE_ACTIVO")
        await manejar_pepe(update, context, user.id, "¡Hola Pepe! Presentate y decime qué vamos a hacer ahora.", None)

if __name__ == '__main__':
    print("🚀 [SISTEMA DE TITANIO] - Ruteador Multi-Agente (Sofy-Pepe-Maria-Jose-Fausto) Activado")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("eraseall", ejecutar_borrado_total))
    app.add_handler(CommandHandler("start", manejar_paso_registro))
    app.add_handler(CallbackQueryHandler(manejar_callback))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, catch_all))
    app.run_polling()
