import db, re
from core.gemini_multimodal import procesar_texto_puro, describir_contenido_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import pepe

async def manejar_pepe(update, context, telegram_id, texto, file_path=None):
    target = update.message if update.message else update.callback_query.message
    adn = db.obtener_adn_completo(telegram_id)
    
    # 1. PERCEPCIÓN: Si hay archivo, lo transcribimos/describimos primero
    descripcion_archivo = ""
    if file_path:
        descripcion_archivo = await describir_contenido_multimodal(file_path)
        log_terminal("👁️ PERCEPCIÓN", "MULTIMODAL", descripcion_archivo)
    
    # 2. Contextos
    historial = adn.get('historial_reciente') or []
    hilo_txt = "\n".join([f"{m['rol']}: {m['txt']}" for m in historial])
    ctx_negocio = f"BÓVEDA: Socio {adn.get('nombre_completo')} | Negocio {adn.get('nombre_empresa')} | Rubro {adn.get('rubro')}"
    
    # 3. Prompt con la "Verdad" del archivo inyectada
    prompt_completo = f"""
    {pepe.obtener_prompt()}
    {ctx_negocio}
    CONTENIDO DEL ARCHIVO RECIBIDO: {descripcion_archivo}
    HISTORIAL: {hilo_txt}
    MENSAJE ACTUAL: {texto}
    """
    
    respuesta = await procesar_texto_puro(prompt_completo, texto)
    
    # 4. Extracción de Datos
    for reg, col in [(r'RUBRO=["\'](.*?)["\']', "rubro"), (r'DOLOR=["\'](.*?)["\']', "dolor_principal")]:
        m = re.search(reg, respuesta, re.IGNORECASE)
        if m: db.actualizar_adn(telegram_id, col, m.group(1))

    if "FINALIZAR_CONSULTORIA: MARIA" in respuesta:
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "MARIA_ACTIVO")
        res_limpia = re.sub(r'(FINALIZAR_CONSULTORIA|RUBRO|DOLOR):.*', '', respuesta, flags=re.IGNORECASE | re.DOTALL).strip()
        await target.reply_text(f"<b>Pepe:</b> {res_limpia}\n\n🤝 <i>Pasando con María...</i>", parse_mode="HTML")
        return

    res_limpia = re.sub(r'(RUBRO|DOLOR):.*', '', respuesta, flags=re.IGNORECASE | re.DOTALL).strip()
    db.guardar_memoria_hilo(telegram_id, "SOCIO", f"{texto} [Archivo: {descripcion_archivo}]")
    db.guardar_memoria_hilo(telegram_id, "PEPE", res_limpia)
    
    log_bot_response("PEPE", res_limpia)
    await target.reply_text(f"<b>Pepe:</b> {res_limpia}", parse_mode="HTML")
