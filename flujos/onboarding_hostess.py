import db, re, os
from core.gemini_multimodal import procesar_texto_puro, procesar_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import hostess
from core.ui import obtener_teclado_por_estado

async def manejar_onboarding(update, context, telegram_id, estado, texto, file_path=None):
    if estado in ["PEPE_ACTIVO", "MARIA_ACTIVO", "JOSEFINA_ACTIVO", "FAUSTO_ACTIVO"]: return
    target = update.message if update.message else update.callback_query.message
    
    db_u = db.obtener_usuario(telegram_id) or {}
    neg_u = db.obtener_contexto_negocio(telegram_id)

    # 1. Validación de Transición Automática (Corta el bucle)
    if db_u.get('nombre_completo') and db_u.get('email') and neg_u:
        if estado == "DATOS_GENERALES":
            db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "CONFIRMACION")
            estado = "CONFIRMACION"

    # 2. Manejo de Registro de Contacto
    if estado == "WHATSAPP" and update.message and update.message.contact:
        db.actualizar_campo_usuario(telegram_id, "telefono_whatsapp", update.message.contact.phone_number)
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "TYC")
        estado = "TYC"

    # 3. Respuesta de la IA o Mensaje de Estado
    res_ia = ""
    if estado == "DATOS_GENERALES":
        prompt = f"{hostess.obtener_prompt()}\nBÓVEDA: {db_u.get('nombre_completo')} | {db_u.get('email')} | {neg_u}"
        if file_path:
            res_ia, desc = await procesar_multimodal(file_path, prompt)
            log_terminal("👁️ PERCEPCIÓN", "SOFY", desc)
        else:
            res_ia = await procesar_texto_puro(prompt, texto)
        
        # Extracción Forzada
        m = re.search(r'DATOS_CAPTURA:.*?nombre=["\'](.*?)["\'].*?email=["\'](.*?)["\'].*?negocio=["\'](.*?)["\']', res_ia, re.IGNORECASE | re.DOTALL)
        if m:
            n, e, neg = m.groups()
            if n.lower() != "none": db.actualizar_campo_usuario(telegram_id, "nombre_completo", n)
            if e.lower() != "none": db.actualizar_campo_usuario(telegram_id, "email", e)
            if neg.lower() != "none": db.actualizar_adn(telegram_id, "nombre_empresa", neg)
        
        res_limpia = re.sub(r'DATOS_CAPTURA:.*', '', res_ia, flags=re.IGNORECASE | re.DOTALL).strip()
    
    elif estado == "CONFIRMACION":
        res_limpia = f"¡Excelente! Revisemos tu legajo:\n👤 {db_u.get('nombre_completo')}\n📧 {db_u.get('email')}\n🏢 {neg_u}\n\n¿Es correcto?"
    elif estado == "TYC":
        res_limpia = "Por favor, aceptá los términos abajo."
    else:
        res_limpia = "Hola, iniciemos el proceso."

    # 4. Salida
    log_bot_response("SOFY", res_limpia)
    await target.reply_text(f"<b>Sofy:</b> {res_limpia}", reply_markup=obtener_teclado_por_estado(estado), parse_mode="HTML")
