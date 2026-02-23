import db, re
from core.gemini_multimodal import procesar_texto_puro, procesar_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import fausto

async def manejar_fausto(update, context, telegram_id, texto, file_path=None):
    target = update.message if update.message else update.callback_query.message
    adn = db.obtener_adn_completo(telegram_id)
    
    # 1. Percepción Multimodal
    desc = ""
    if file_path:
        _, desc = await procesar_multimodal(file_path, "Describe estas rutinas para Fausto.")
        log_terminal("👁️ PERCEPCIÓN", "FAUSTO", desc)
    
    # 2. Contexto de Identidad
    historial = adn.get('historial_reciente') or []
    hilo_txt = "\n".join([f"{m['rol']}: {m['txt']}" for m in historial])
    ctx = f"EQUIPO: {adn.get('estructura_equipo')} | PERSONALIDADES: {adn.get('personalidad_agentes')}"
    
    prompt = f"{fausto.obtener_prompt()}\n\nTU IDENTIDAD: FAUSTO.\n{ctx}\nARCHIVO: {desc}\nHISTORIAL:\n{hilo_txt}"
    
    respuesta = await procesar_texto_puro(prompt, texto)
    
    # 3. Extractor de Rutinas
    r_match = re.search(r'RUTINAS[:=]\s*["\']?(.*?)["\']?($|\n|FINALIZAR)', respuesta, re.IGNORECASE | re.DOTALL)
    if r_match:
        db.actualizar_adn(telegram_id, "rutinas_trabajo", r_match.group(1).strip())

    # 4. Salida y Logs
    finalizar = "FINALIZAR_RUTINAS: SOFIA" in respuesta
    res_limpia = re.sub(r'(FINALIZAR_RUTINAS|RUTINAS[:=]).*', '', respuesta, flags=re.IGNORECASE | re.DOTALL).strip()
    
    log_bot_response("FAUSTO", res_limpia)
    db.guardar_memoria_hilo(telegram_id, "SOCIO", texto)
    db.guardar_memoria_hilo(telegram_id, "FAUSTO", res_limpia)

    if finalizar:
        db.actualizar_campo_usuario(telegram_id, "estado_onboarding", "RESUMEN_FINAL")
        await target.reply_text(f"⚙️ <b>Fausto:</b> {res_limpia}\n\n👑 <i>Todo listo. Volviendo con Sofía...</i>", parse_mode="HTML")
    else:
        await target.reply_text(f"⚙️ <b>Fausto:</b> {respuesta}", parse_mode="HTML")
