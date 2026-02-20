from datetime import datetime

AZUL, VERDE, AMARILLO, ROJO, CYAN, RESET = "\033[94m", "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[0m"

def log_terminal(tipo, usuario, detalle):
    hora = datetime.now().strftime("%H:%M:%S")
    color_user = ROJO if usuario == "DESCONOCIDO" else CYAN
    
    # Colores por tipo de acción
    if any(x in tipo for x in ["COMANDO", "CALLBACK", "TYC"]): color_tipo = AMARILLO
    elif tipo in ["TEXTO", "WHATSAPP", "CONTACTO"]: color_tipo = AZUL
    elif tipo in ["IMAGEN", "AUDIO", "DOC", "VIDEO"]: color_tipo = CYAN
    elif "SISTEMA" in tipo: color_tipo = ROJO
    else: color_tipo = RESET

    print(f"{color_tipo}[{hora}] 📥 {tipo} | User: {color_user}{usuario}{color_tipo} | {detalle}{RESET}")

def log_bot_response(agente, respuesta):
    hora = datetime.now().strftime("%H:%M:%S")
    # Limpiamos etiquetas técnicas para el log si existen
    import re
    limpio = re.sub(r'\[DATA:.*?\]', '', respuesta).strip()
    print(f"\n{VERDE}[{hora}] 🤖 RESPONSE | Agente: {agente} | {limpio}{RESET}\n")

def obtener_info_mensaje(update):
    """Extrae el tipo y contenido de cualquier mensaje de Telegram (Regla #7)"""
    msg = update.message
    if not msg: return "SISTEMA", "Acción de interfaz"
    
    if msg.text: return "TEXTO", msg.text
    if msg.contact: return "CONTACTO", f"WhatsApp: {msg.contact.phone_number}"
    if msg.photo: return "IMAGEN", f"Foto ID: {msg.photo[-1].file_id}"
    if msg.voice: return "AUDIO", f"Nota de voz ID: {msg.voice.file_id}"
    if msg.audio: return "MUSICA", f"Archivo audio: {msg.audio.file_name}"
    if msg.video: return "VIDEO", f"Video ID: {msg.video.file_id}"
    if msg.document: return "DOC", f"Documento: {msg.document.file_name}"
    
    return "OTRO", "Contenido no identificado"
