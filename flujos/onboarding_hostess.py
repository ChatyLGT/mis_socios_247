import db, re, os
from core.gemini_multimodal import procesar_texto_puro, procesar_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import hostess
from core.ui import obtener_teclado_por_estado
from telegram import ReplyKeyboardRemove

async def manejar_onboarding(update, context, telegram_id, estado, texto, file_path=None):
    db_user = db.obtener_usuario(telegram_id) or {}
    target = update.message if update.message else update.callback_query.message
    
    # 1. Registro de WhatsApp
    if estado == "WHATSAPP" and update.message and update.message.contact:
        db.actualizar_campo_usuario(telegram_id, "telefono_whatsapp", update.message.contact.phone_number)
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "TYC")
        estado = "TYC"
        await target.reply_text("📱 WhatsApp vinculado.", reply_markup=ReplyKeyboardRemove())

    # 2. Respuestas Fijas (Bozal)
    if estado in ["NUEVO", "WHATSAPP", "TYC"]:
        respuestas = {
            "NUEVO": "¡Hola! Bienvenido. Dale clic al botón de abajo para iniciar.",
            "WHATSAPP": "Necesito que compartas tu contacto para seguir.",
            "TYC": "Por favor, aceptá los términos abajo."
        }
        res_ia = respuestas.get(estado, "Continuemos.")
    else:
        # 3. Lógica de Recolección (DATOS_GENERALES)
        n_db = db_user.get('nombre_completo')
        e_db = db_user.get('email')
        neg_db = db.obtener_contexto_negocio(telegram_id)
        
        ctx = f"BÓVEDA: Nombre:{n_db or 'None'}, Email:{e_db or 'None'}, Negocio:{neg_db or 'None'}"
        prompt = f"{hostess.obtener_prompt()}\nESTADO: {estado}\n{ctx}\nUSUARIO: {texto}"
        res_ia = await (procesar_multimodal(file_path, prompt) if file_path else procesar_texto_puro(prompt, texto))
        
        # EXTRACTOR DE HIERRO (Flexible con espacios, comas y comillas)
        regex_n = r'nombre=["\'](.*?)["\']'
        regex_e = r'email=["\'](.*?)["\']'
        regex_neg = r'negocio=["\'](.*?)["\']'

        n = re.search(regex_n, res_ia, re.IGNORECASE)
        e = re.search(regex_e, res_ia, re.IGNORECASE)
        neg = re.search(regex_neg, res_ia, re.IGNORECASE)

        if n and n.group(1).lower() != "none":
            db.actualizar_campo_usuario(telegram_id, "nombre_completo", n.group(1))
            log_terminal("BÓVEDA", "SISTEMA", f"✅ Nombre guardado: {n.group(1)}")
        if e and e.group(1).lower() != "none":
            db.actualizar_campo_usuario(telegram_id, "email", e.group(1))
            log_terminal("BÓVEDA", "SISTEMA", f"✅ Email guardado: {e.group(1)}")
        if neg and neg.group(1).lower() != "none":
            db.actualizar_adn(telegram_id, "nombre_empresa", neg.group(1))
            log_terminal("BÓVEDA", "SISTEMA", f"✅ Negocio guardado: {neg.group(1)}")

    # 4. Limpieza y Salto a Confirmación
    res_limpia = re.sub(r'DATOS_CAPTURA:.*', '', res_ia).strip()
    
    db_u = db.obtener_usuario(telegram_id) or {}
    neg_u = db.obtener_contexto_negocio(telegram_id)
    
    if db_u.get('nombre_completo') and db_u.get('email') and neg_u and estado == "DATOS_GENERALES":
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "CONFIRMACION")
        estado = "CONFIRMACION"
        res_limpia = f"¡Excelente! Revisemos tu legajo:\n👤 **Nombre:** {db_u['nombre_completo']}\n📧 **Email:** {db_u['email']}\n🏢 **Negocio:** {neg_u}"

    teclado = obtener_teclado_por_estado(estado)
    await target.reply_text(f"**Sofy:** {res_limpia}", reply_markup=teclado, parse_mode="Markdown")

    if estado == "TYC" and os.path.exists("flujos/tyc_texto.txt"):
        with open("flujos/tyc_texto.txt", "r") as f:
            await target.reply_text(f.read())
