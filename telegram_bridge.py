import os, asyncio
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import db
from core.borrado import ejecutar_borrado_total
from core.registro import manejar_paso_registro
from core.grabadora import log_terminal, obtener_info_mensaje
from flujos.onboarding_hostess import manejar_onboarding

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def catch_all(update, context):
    user = update.effective_user
    if not user or not update.message: return
    
    # 1. Registro Obligatorio (Regla de Oro)
    db.crear_usuario(user.id)
    db_user = db.obtener_usuario(user.id)
    
    # Identidad: ID de Telegram es el ancla
    nombre_log = db_user.get('nombre_completo') or f"ID:{user.id}"
    tipo, contenido = obtener_info_mensaje(update)
    
    # 2. Lógica de Estados Blindada
    estado_db = db_user.get('estado_onboarding')
    # Si no tiene nombre y no ha aceptado TyC, lo forzamos a NUEVO o el estado que toque
    if not estado_db or estado_db == 'WHATSAPP' and not db_user.get('telefono_whatsapp'):
        if not estado_db: estado = "NUEVO"
        else: estado = "WHATSAPP"
    else:
        estado = estado_db

    # Forzamos que si es el primer mensaje tras borrar, sea NUEVO
    if not db_user.get('telefono_whatsapp') and not estado_db:
        estado = "NUEVO"

    log_terminal(f"{tipo} | ESTADO: {estado}", nombre_log, contenido)
    await manejar_onboarding(update, context, user.id, estado, contenido)

async def manejar_callback(update, context):
    query = update.callback_query
    user = update.effective_user
    db_user = db.obtener_usuario(user.id)
    nombre_log = db_user.get('nombre_completo') or f"ID:{user.id}"
    
    log_terminal("CALLBACK", nombre_log, f"🔘 Clic en: {query.data}")
    await query.answer()

    if query.data == "start_flow":
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "WHATSAPP")
        await manejar_paso_registro(update, context)
    elif query.data == "acepto_tyc":
        db.actualizar_campo_usuario(user.id, "status_legal", True)
        db.inicializar_adn(user.id)
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "DATOS_GENERALES")
        await manejar_onboarding(update, context, user.id, "DATOS_GENERALES", "Acepto")
    elif query.data == "confirmacion_ok":
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "PASO_PEPE")
        await manejar_onboarding(update, context, user.id, "PASO_PEPE", "Confirmado")
    elif query.data == "ir_a_pepe":
        db.actualizar_campo_usuario(user.id, "estado_onboarding", "PEPE_ACTIVO")
        await query.message.reply_text("🤝 **Sofy:** ¡Listo! Te dejé con Pepe.")

if __name__ == '__main__':
    print("🚀 [SISTEMA DE TITANIO] - Omnisciencia Selectiva Activada")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("eraseall", ejecutar_borrado_total))
    app.add_handler(CommandHandler("start", manejar_paso_registro))
    app.add_handler(CallbackQueryHandler(manejar_callback))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, catch_all))
    app.run_polling()
