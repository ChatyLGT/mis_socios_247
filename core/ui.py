from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def obtener_teclado_por_estado(estado):
    if estado in ["NUEVO"]:
        return InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Iniciar Registro", callback_data="start_flow")]])
    elif estado == "WHATSAPP":
        kb = [[KeyboardButton("📱 Compartir mi WhatsApp", request_contact=True)]]
        return ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
    elif estado == "TYC":
        return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Acepto los términos", callback_data="acepto_tyc")]])
    elif estado == "CONFIRMACION":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Sí, es correcto", callback_data="confirmacion_ok")],
            [InlineKeyboardButton("❌ Hay un error", callback_data="confirmacion_error")]
        ])
    elif estado == "PASO_PEPE":
        return InlineKeyboardMarkup([[InlineKeyboardButton("🎙️ Ir con Pepe", callback_data="ir_a_pepe")]])
    else:
        return ReplyKeyboardRemove()
