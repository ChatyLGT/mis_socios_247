import db, re
from core.gemini_multimodal import procesar_texto_puro, procesar_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import maria

async def manejar_maria(update, context, telegram_id, texto, file_path=None):
    target = update.message if update.message else update.callback_query.message
    adn = db.obtener_adn_completo(telegram_id)
    
    # 1. Percepción Multimodal
    desc = ""
    if file_path:
        _, desc = await procesar_multimodal(file_path, "Describe este archivo para el contexto de la app.")
        log_terminal("👁️ PERCEPCIÓN", "MARIA", desc)
    
    # 2. Contexto de Identidad y Bóveda
    historial = adn.get('historial_reciente') or []
    hilo_txt = "\n".join([f"{m['rol']}: {m['txt']}" for m in historial])
    ctx = f"Socio: {adn.get('nombre_completo')} | Negocio: {adn.get('nombre_empresa')} | Dolor: {adn.get('dolor_principal')}"
    
    prompt = f"{maria.obtener_prompt()}\n\nTU IDENTIDAD: Eres MARÍA.\n{ctx}\nARCHIVO: {desc}\nHISTORIAL:\n{hilo_txt}"
    
    respuesta = await procesar_texto_puro(prompt, texto)
    
    # 3. Extractor Robusto de Equipo (Busca etiquetas EQUIPO: o EQUIPO=)
    equipo_match = re.search(r'EQUIPO[:=]\s*["\']?(.*?)["\']?($|\n|FINALIZAR)', respuesta, re.IGNORECASE | re.DOTALL)
    if equipo_match:
        equipo_str = equipo_match.group(1).strip()
        db.actualizar_adn(telegram_id, "estructura_equipo", equipo_str)
        log_terminal("BÓVEDA", "MARIA", f"✅ Equipo guardado: {equipo_str}")

    # 4. Lógica de Salida y Logs
    finalizar = "FINALIZAR_ESTRATEGIA: JOSEFINA" in respuesta
    res_limpia = re.sub(r'(FINALIZAR_ESTRATEGIA|EQUIPO[:=]).*', '', respuesta, flags=re.IGNORECASE | re.DOTALL).strip()
    
    log_bot_response("MARIA", res_limpia)
    db.guardar_memoria_hilo(telegram_id, "SOCIO", texto)
    db.guardar_memoria_hilo(telegram_id, "MARIA", res_limpia)

    if finalizar:
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "JOSEFINA_ACTIVO")
        await target.reply_text(f"📊 <b>María:</b> {res_limpia}\n\n✨ <i>Pasando con Josefina...</i>", parse_mode="HTML")
    else:
        await target.reply_text(f"📊 <b>María:</b> {res_limpia}", parse_mode="HTML")
