import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import db

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# --- SISTEMA DE LOGS OMNISCIENTE ---
def log_event(evento, usuario, detalle=""):
    hora = datetime.now().strftime("%H:%M:%S")
    print(f"[{hora}] 🟢 {evento} | User: {usuario} | {detalle}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    log_event("COMANDO /start", user.first_name)
    
    db_user = db.obtener_usuario(telegram_id)
    
    if not db_user:
        log_event("NUEVO USUARIO", user.first_name, "Creando registro en BD...")
        db.crear_usuario(telegram_id)
        db.actualizar_campo_usuario(telegram_id, "nombre_completo", user.full_name)
        
        boton_contacto = [[KeyboardButton("📱 Compartir mi WhatsApp", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(boton_contacto, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            f"¡Hola {user.first_name}! Bienvenido a tu Sistema de Aceleración y Abundancia Integral. 🚀\n\n"
            "Para iniciar tu transformación y crear tu perfil seguro, necesito que valides tu número tocando el botón de abajo:",
            reply_markup=reply_markup
        )
        log_event("MENSAJE ENVIADO", user.first_name, "Petición de WhatsApp enviada.")
    else:
        log_event("USUARIO RECURRENTE", user.first_name)
        if db_user['status_legal']:
            await update.message.reply_text("¡Qué bueno verte de nuevo! Tu ecosistema ya está activo. 🚀")
        else:
            await enviar_tyc(update.message)

async def recibir_contacto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    telefono = update.message.contact.phone_number
    log_event("WHATSAPP RECIBIDO", user.first_name, f"Número capturado: {telefono}")
    
    db.actualizar_campo_usuario(telegram_id, "telefono_whatsapp", telefono)
    
    await update.message.reply_text(
        "¡Teléfono verificado con éxito! ✅", 
        reply_markup=ReplyKeyboardRemove()
    )
    await enviar_tyc(update.message)

async def enviar_tyc(message):
    teclado = [[InlineKeyboardButton("✅ Acepto mi Transformación", callback_data="acepto_tyc")]]
    reply_markup = InlineKeyboardMarkup(teclado)
    await message.reply_text(
        "Último paso antes de entrar.\n\n"
        "Al continuar, aceptas nuestros Términos de Confidencialidad. Tu información y la de tu negocio están blindadas.",
        reply_markup=reply_markup
    )

async def boton_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    await query.answer()
    
    if query.data == "acepto_tyc":
        telegram_id = user.id
        log_event("TYC ACEPTADOS", user.first_name, "Cambiando status_legal a TRUE en BD")
        db.actualizar_campo_usuario(telegram_id, "status_legal", True)
        
        await query.edit_message_text(
            "¡Contrato firmado! 🖋️\n\n"
            "Tu perfil está creado y tu Tanque de Gasolina está al 100%.\n\n"
            "*(Fin de la Prueba Sprint 1. Acá entrará el Hostess en el siguiente paso)*"
        )

async def eraseall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    
    if not context.args or context.args[0] != "Chaty2026":
        log_event("INTENTO BORRADO FALLIDO", user.first_name, "Contraseña incorrecta o ausente")
        await update.message.reply_text("⛔ Comando no autorizado o contraseña incorrecta.")
        return

    log_event("BOTÓN DE PÁNICO", user.first_name, "Borrando usuario de la BD (ON DELETE CASCADE)")
    db.borrar_usuario(telegram_id)
    
    await update.message.reply_text(
        "💥 ¡Booooom! Tu perfil, tus datos y tu memoria han sido borrados de la Matrix.\n\n"
        "El sistema ahora te reconoce como un completo desconocido. Escribe /start para volver a nacer.",
        reply_markup=ReplyKeyboardRemove()
    )

async def catch_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    telegram_id = user.id
    texto = update.message.text if update.message.text else "Archivo Multimedia/Sticker"
    log_event("CATCH-ALL TRIGGER", user.first_name, f"Input recibido: '{texto}'")
    
    db_user = db.obtener_usuario(telegram_id)
    
    if not db_user:
        # El usuario no existe en la BD
        await update.message.reply_text(
            "¡Hola! 👋 Para iniciar tu experiencia y configurar tu sistema, por favor presiona o escribe /start"
        )
    elif not db_user.get('status_legal'):
        # El usuario existe, dio el teléfono, pero NO firmó
        log_event("LIMBO LEGAL", user.first_name, "Reenviando Términos y Condiciones")
        await update.message.reply_text(
            "¡Ojo! 👀 Para continuar es necesario aceptar los Términos y Condiciones. Continuamos, acá te los dejo de nuevo:"
        )
        await enviar_tyc(update.message)
    else:
        # El usuario ya tiene todo en regla
        await update.message.reply_text(
            "¡Tu ecosistema está blindado y listo! 🚀\n(Fase de Onboarding en construcción para el Sprint 2)."
        )

if __name__ == '__main__':
    print("===========================================================")
    print("🚀 [GATEKEEPER LOGS ACTIVOS] Sistema esperando interacciones...")
    print("===========================================================")
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("eraseall", eraseall))
    app.add_handler(MessageHandler(filters.CONTACT, recibir_contacto))
    app.add_handler(CallbackQueryHandler(boton_inline))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & ~filters.CONTACT, catch_all))
    
    app.run_polling()
