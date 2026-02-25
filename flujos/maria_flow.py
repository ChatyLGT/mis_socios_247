import db, re, asyncio
from core.gemini_multimodal import procesar_texto_puro
from core.grabadora import log_bot_response, log_terminal
from agentes import maria
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def manejar_maria(update, context, telegram_id, texto, file_path=None):
    target = update.message if update.message else update.callback_query.message
    adn = db.obtener_adn_completo(telegram_id) or {}
    
    historial = adn.get('historial_reciente') or []
    hilo_txt = "\n".join([f"{m['rol']}: {m['txt']}" for m in historial[-6:]]) if historial else "Sin historial aún."
    
    # Llamamos a María pasándole el telegram_id
    prompt = f"{maria.obtener_prompt(telegram_id)}\n\nHISTORIAL RECIENTE:\n{hilo_txt}"
    
    res_ia = await procesar_texto_puro(prompt, texto)
    db.guardar_memoria_hilo(telegram_id, "SOCIO", texto)

    print(f"\n--- 🕵️ FORENSE MARIA RAW ---\n{res_ia}\n-----------------------------\n")

    # 1. Buscamos el semáforo para avanzar
    estado_aprobado = False
    if 'ESTADO_MARIA="Aprobado"' in res_ia:
        estado_aprobado = True

    # 2. Limpieza de pantalla (escondemos la etiqueta y los posibles JSON de la vista del usuario)
    res_limpia = re.sub(r'ESTADO_MARIA=".*?"', '', res_ia).strip()
    res_limpia = re.sub(r'```json.*?```', '', res_limpia, flags=re.DOTALL).strip()

    db.guardar_memoria_hilo(telegram_id, "MARIA", res_limpia)
    log_bot_response("MARIA", res_limpia)

    # 3. La claqueta de acción
    if estado_aprobado:
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Avanzar con Josefina", callback_data="maria_avanzar_josefina")]
        ])
        await target.reply_text(f"<b>María:</b> {res_limpia}", reply_markup=teclado, parse_mode="HTML")
    else:
        await target.reply_text(f"<b>María:</b> {res_limpia}", parse_mode="HTML")
