from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

def obtener_teclado_por_estado(estado):
    if estado == "NUEVO":
        return InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Iniciar Registro", callback_data="start_flow")]])
    if estado == "WHATSAPP":
        return ReplyKeyboardMarkup([[KeyboardButton("📱 Compartir mi WhatsApp", request_contact=True)]],
                                   resize_keyboard=True, one_time_keyboard=True)
    if estado == "TYC":
        return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Acepto los Términos", callback_data="acepto_tyc")]])
    if estado == "DATOS_GENERALES":
        return InlineKeyboardMarkup([[InlineKeyboardButton("📝 Enviar mis datos generales", callback_data="enviar_generales")]])
    if estado == "CONFIRMACION":
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Todo bien, avanzar", callback_data="confirmacion_ok")],
            [InlineKeyboardButton("❌ Hay un error, corregir", callback_data="confirmacion_error")]
        ])
    if estado == "PASO_PEPE":
        return InlineKeyboardMarkup([[InlineKeyboardButton("🤝 Ir con Pepe", callback_data="ir_a_pepe")]])
        
    return ReplyKeyboardRemove()
