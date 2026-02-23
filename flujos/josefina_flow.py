import db, re
from core.gemini_multimodal import procesar_texto_puro, procesar_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import josefina

async def manejar_josefina(update, context, telegram_id, texto, file_path=None):
    target = update.message if update.message else update.callback_query.message
    adn = db.obtener_adn_completo(telegram_id)
    
    desc = ""
    if file_path:
        _, desc = await procesar_multimodal(file_path, "Describe este archivo para Josefina.")
    
    historial = adn.get('historial_reciente') or []
    hilo_txt = "\n".join([f"{m['rol']}: {m['txt']}" for m in historial])
    
    ctx = f"BÓVEDA - EQUIPO: {adn.get('estructura_equipo') or 'Ver historial'}"
    prompt = f"{josefina.obtener_prompt()}\n\nTU IDENTIDAD: JOSEFINA.\n{ctx}\nHISTORIAL:\n{hilo_txt}"
    
    respuesta = await procesar_texto_puro(prompt, f"{texto} [Archivo: {desc}]")
    
    # Captura de Personalidad
    p_match = re.search(r'PERSONALIDAD[:=]\s*["\']?(.*?)["\']?($|\n|FINALIZAR)', respuesta, re.IGNORECASE | re.DOTALL)
    if p_match: db.actualizar_adn(telegram_id, "personalidad_agentes", p_match.group(1))

    finalizar = "FINALIZAR_PERSONALIDAD: FAUSTO" in respuesta
    res_limpia = re.sub(r'(FINALIZAR_PERSONALIDAD|PERSONALIDAD[:=]).*', '', respuesta, flags=re.IGNORECASE | re.DOTALL).strip()
    
    log_bot_response("JOSEFINA", res_limpia)
    db.guardar_memoria_hilo(telegram_id, "SOCIO", texto)
    db.guardar_memoria_hilo(telegram_id, "JOSEFINA", res_limpia)

    if finalizar:
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "FAUSTO_ACTIVO")
        await target.reply_text(f"✨ <b>Josefina:</b> {res_limpia}\n\n⚙️ <i>Pasando con Fausto...</i>", parse_mode="HTML")
    else:
        await target.reply_text(f"✨ <b>Josefina:</b> {res_limpia}", parse_mode="HTML")
