import db, re, os, asyncio
from core.gemini_multimodal import procesar_texto_puro, procesar_multimodal
from core.grabadora import log_bot_response, log_terminal
from agentes import pepe
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def manejar_pepe(update, context, telegram_id, texto, file_path=None):
    target = update.message if update.message else update.callback_query.message
    adn = db.obtener_adn_completo(telegram_id) or {}
    
    historial = adn.get('historial_reciente') or []
    hilo_txt = "\n".join([f"{m['rol']}: {m['txt']}" for m in historial[-6:]]) if historial else "Sin historial aún."
    
    # LA MEMORIA INMORTAL DE PEPE
    memoria_largo_plazo = adn.get('notas_pepe', 'Aún no hay datos acumulados.')
    ctx_negocio = f"BÓVEDA ACTUAL: Socio {adn.get('nombre_completo', '')} | Negocio {adn.get('nombre_empresa', '')}\nMEMORIA LARGO PLAZO (TU RESUMEN ANTERIOR): {memoria_largo_plazo}"
    
    prompt = f"{pepe.obtener_prompt()}\n{ctx_negocio}\nHISTORIAL RECIENTE:\n{hilo_txt}"
    
    res_ia = ""
    # EL TEATRO MULTIMODAL (UX)
    if file_path:
        await target.reply_text("⏳ *Pepe está analizando tu archivo/audio. Dame unos segundos...*", parse_mode="Markdown")
        await asyncio.sleep(2) # Delay humano para dar realismo
        res_ia, desc = await procesar_multimodal(file_path, prompt)
        log_terminal("👁️ PERCEPCIÓN", "PEPE", desc)
        
        # Le mostramos al usuario lo que Pepe entendió en crudo
        await target.reply_text(f"🧠 *Notas internas de Pepe:* \n_{desc}_", parse_mode="Markdown")
        db.guardar_memoria_hilo(telegram_id, "SOCIO", f"[Archivo Adjunto: {desc}] {texto}")
    else:
        res_ia = await procesar_texto_puro(prompt, texto)
        db.guardar_memoria_hilo(telegram_id, "SOCIO", texto)

    print(f"\n--- 🕵️ FORENSE PEPE RAW ---\n{res_ia}\n-----------------------------\n")

    # ATRAPAMOS EL RESUMEN ACUMULADO Y LO GUARDAMOS PARA SIEMPRE
    m_resumen = re.search(r'RESUMEN_ACUMULADO:\s*["\']?(.*?)["\']?(?=\n|$)', res_ia, re.IGNORECASE | re.DOTALL)
    if m_resumen:
        resumen_limpio = m_resumen.group(1).strip()
        db.actualizar_adn(telegram_id, "notas_pepe", resumen_limpio)
        print(f"💾 MEMORIA LARGO PLAZO GUARDADA: {resumen_limpio[:60]}...")

    checklist_completo = False
    m_check = re.search(r'ESTADO_CHECKLIST:.*?rubro=[\'"]?([^\'"\n]+)[\'"]?.*?dolor=[\'"]?([^\'"\n]+)[\'"]?.*?modelo=[\'"]?([^\'"\n]+)[\'"]?', res_ia, re.IGNORECASE)
    if m_check:
        cr, cd, cm = m_check.groups()
        cr, cd, cm = cr.strip().lower(), cd.strip().lower(), cm.strip().lower()
        print(f"📋 PEPE CHECKLIST -> Rubro: {cr} | Dolor: {cd} | Modelo: {cm}")
        if cr == "ok" and cd == "ok" and cm == "ok":
            checklist_completo = True

    # Limpiamos la basura técnica
    res_limpia = re.sub(r'(?i)(ESTADO_CHECKLIST|RESUMEN_ACUMULADO|DATOS_EXTRAIDOS).*', '', res_ia, flags=re.DOTALL).strip()
    db.guardar_memoria_hilo(telegram_id, "PEPE", res_limpia)
    log_bot_response("PEPE", res_limpia)

    if checklist_completo:
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Quiero dar más contexto", callback_data="pepe_mas_contexto")],
            [InlineKeyboardButton("🚀 Todo claro, avanzar con María", callback_data="pepe_avanzar_maria")]
        ])
        await target.reply_text(f"<b>Pepe:</b> {res_limpia}", reply_markup=teclado, parse_mode="HTML")
    else:
        await target.reply_text(f"<b>Pepe:</b> {res_limpia}", parse_mode="HTML")
