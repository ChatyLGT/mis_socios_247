import db
from core.ui import obtener_teclado_por_estado
from core.grabadora import log_terminal

async def manejar_paso_registro(update, context):
    user = update.effective_user
    if not user: return
    
    db_user = db.obtener_usuario(user.id)
    if not db_user:
        db.crear_usuario(user.id)
        db_user = db.obtener_usuario(user.id)

    # Determinamos el estado para la UI
    if not db_user.get('telefono_whatsapp'):
        estado = "WHATSAPP"
    elif not db_user.get('status_legal'):
        estado = "TYC"
    else:
        estado = "DATOS_GENERALES"

    teclado = obtener_teclado_por_estado(estado)
    textos = {
        "WHATSAPP": "Che, antes de seguir necesito tu WhatsApp para validarte. ¡Dale al botón!",
        "TYC": "Falta que firmes los términos legales para entrar a la bóveda:",
        "DATOS_GENERALES": "¡Ya estás adentro! Pasame tu nombre, email y negocio."
    }
    
    target = update.message if update.message else update.callback_query.message
    await target.reply_text(textos.get(estado, "Continuemos:"), reply_markup=teclado)
