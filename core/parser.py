def parsear_evento(update):
    """Módulo Modular de Identidad y Contenido (Regla #2, #7 y Multi-usuario)"""
    user = update.effective_user
    
    # 1. Extracción de Identidad para el LOG
    user_data = {
        "id": None,
        "username": None,
        "first_name": None,
        "last_name": None,
        "language_code": None
    }

    if user:
        user_data = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code
        }
        nombre_completo = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username_log = f"(@{user.username})" if user.username else "Sin User"
        idioma = f"[{user.language_code or '??'}]"
        identidad = f"{nombre_completo} {username_log} {idioma} [ID:{user.id}]"
    else:
        identidad = "SISTEMA"

    # 2. Identificación de Contenido según Regla #7
    if update.callback_query:
        return identidad, "CALLBACK", f"🔘 Clic en: {update.callback_query.data}", user_data
    
    msg = update.message
    if not msg: return identidad, "SISTEMA", "Evento sin mensaje", user_data
    
    # Mapeo de contenidos para el LOG de la terminal
    tipo, contenido = "OTRO", "Contenido no identificado"
    if msg.text: tipo, contenido = "TEXTO", msg.text
    elif msg.contact: tipo, contenido = "CONTACTO", f"Tel: {msg.contact.phone_number}"
    elif msg.photo: tipo, contenido = "IMAGEN", f"Foto ID: {msg.photo[-1].file_id}"
    elif msg.voice: tipo, contenido = "AUDIO", f"Voz ID: {msg.voice.file_id}"
    elif msg.audio: tipo, contenido = "MUSICA", f"Archivo: {msg.audio.file_name}"
    elif msg.video: tipo, contenido = "VIDEO", f"Video ID: {msg.video.file_id}"
    elif msg.document: tipo, contenido = "DOC", f"Doc: {msg.document.file_name}"
    
    return identidad, tipo, contenido, user_data
