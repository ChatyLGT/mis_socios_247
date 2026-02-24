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

    if estado == "WHATSAPP" and update.message and update.message.contact:
        db.actualizar_campo_usuario(telegram_id, "telefono_whatsapp", update.message.contact.phone_number)
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "TYC")
        estado = "TYC"
        res_limpia = "¡Excelente! Número protegido y encriptado en nuestra bóveda.\n\nPor favor, revisá y aceptá los términos abajo para continuar."
        log_bot_response("SOFY", res_limpia)
        await target.reply_text(f"<b>Sofy:</b> {res_limpia}", reply_markup=obtener_teclado_por_estado(estado), parse_mode="HTML")
        return

    res_ia = ""
    res_limpia = ""
    
    # 1. SI ESTAMOS CAPTURANDO DATOS POR PRIMERA VEZ
    if estado == "DATOS_GENERALES":
        prompt = f"{hostess.obtener_prompt(estado)}\nBÓVEDA ACTUAL: {db_u.get('nombre_completo')} | {db_u.get('email')} | {neg_u}"
        if file_path:
            res_ia, desc = await procesar_multimodal(file_path, prompt)
            log_terminal("👁️ PERCEPCIÓN", "SOFY", desc)
        else:
            res_ia = await procesar_texto_puro(prompt, texto)
        
        print(f"\n--- 🕵️ FORENSE GEMINI RAW ---\n{res_ia}\n-----------------------------\n")
        m = re.search(r'DATOS_CAPTURA:.*?nombre=[\'"]?([^\'"\n]+)[\'"]?.*?email=[\'"]?([^\'"\n]+)[\'"]?.*?negocio=[\'"]?([^\'"\n]+)[\'"]?', res_ia, re.IGNORECASE | re.DOTALL)
        if m:
            n, e, neg = m.groups()
            n, e, neg = n.strip(), e.strip(), neg.strip()
            print(f"✅ EXTRACCIÓN EXITOSA -> Nombre: {n} | Email: {e} | Negocio: {neg}")
            if n.lower() != "none" and n: db.actualizar_campo_usuario(telegram_id, "nombre_completo", n)
            if e.lower() != "none" and e: db.actualizar_campo_usuario(telegram_id, "email", e)
            if neg.lower() != "none" and neg: db.actualizar_adn(telegram_id, "nombre_empresa", neg)
        
        res_limpia = re.sub(r'(?i)\*?DATOS_CAPTURA.*', '', res_ia, flags=re.DOTALL).strip()
        
        # TRANSICIÓN AUTOMÁTICA
        db_u = db.obtener_usuario(telegram_id) or {}
        neg_u = db.obtener_contexto_negocio(telegram_id)
        if db_u.get('nombre_completo') and db_u.get('email') and neg_u and str(neg_u).lower() != "none":
            print("🏆 BOVEDA LLENA. Transición automática a CONFIRMACIÓN.")
            db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "CONFIRMACION")
            estado = "CONFIRMACION"
            
    # 2. SI EL USUARIO ESTÁ HACIENDO UNA CORRECCIÓN EN LA BÓVEDA
    elif estado == "CONFIRMACION":
        prompt = f"{hostess.obtener_prompt(estado)}\nBÓVEDA ACTUAL: Nombre: {db_u.get('nombre_completo')} | Email: {db_u.get('email')} | Negocio: {neg_u}"
        if file_path:
            res_limpia, desc = await procesar_multimodal(file_path, prompt)
        else:
            res_limpia = await procesar_texto_puro(prompt, texto)

        print(f"\n--- 🕵️ FORENSE GEMINI RAW (CONF) ---\n{res_limpia}\n-----------------------------\n")
        m = re.search(r'CORRECCION_DATOS:.*?nombre=[\'"]?([^\'"\n]+)[\'"]?.*?email=[\'"]?([^\'"\n]+)[\'"]?.*?negocio=[\'"]?([^\'"\n]+)[\'"]?', res_limpia, re.IGNORECASE | re.DOTALL)
        if m:
            n, e, neg = m.groups()
            n, e, neg = n.strip(), e.strip(), neg.strip()
            print(f"✅ CORRECCIÓN DETECTADA -> Nombre: {n} | Email: {e} | Negocio: {neg}")
            if n.lower() != "none" and n: db.actualizar_campo_usuario(telegram_id, "nombre_completo", n)
            if e.lower() != "none" and e: db.actualizar_campo_usuario(telegram_id, "email", e)
            if neg.lower() != "none" and neg: db.actualizar_adn(telegram_id, "nombre_empresa", neg)
            
        res_limpia = re.sub(r'(?i)\*?CORRECCION_DATOS.*', '', res_limpia, flags=re.DOTALL).strip()

    # 3. CUALQUIER OTRA FASE (NUEVO, WHATSAPP, TYC, PASO_PEPE)
    else:
        prompt = hostess.obtener_prompt(estado)
        if file_path:
            res_limpia, desc = await procesar_multimodal(file_path, prompt)
            log_terminal("👁️ PERCEPCIÓN", "SOFY", desc)
        else:
            res_limpia = await procesar_texto_puro(prompt, texto)

    # REGLA FINAL: Si el estado actual es CONFIRMACION (sea porque acaba de llegar o porque corrigió), SIEMPRE adjunta el legajo actualizado.
    if estado == "CONFIRMACION":
        db_u = db.obtener_usuario(telegram_id) or {}
        neg_u = db.obtener_contexto_negocio(telegram_id)
        res_limpia = res_limpia + f"\n\n---\nRevisemos tu legajo:\n👤 {db_u.get('nombre_completo')}\n📧 {db_u.get('email')}\n🏢 {neg_u}\n\n¿Es correcto?"

    if not res_limpia: res_limpia = "Entendido."

    log_bot_response("SOFY", res_limpia)
    await target.reply_text(f"<b>Sofy:</b> {res_limpia}", reply_markup=obtener_teclado_por_estado(estado), parse_mode="HTML")
