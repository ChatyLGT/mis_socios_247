from datetime import datetime
import re

AZUL, VERDE, AMARILLO, ROJO, CYAN, RESET = "\033[94m", "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[0m"

def log_terminal(tipo, usuario, detalle):
    """Pinta la actividad en la terminal con colores (Regla #7)"""
    hora = datetime.now().strftime("%H:%M:%S")
    color_user = ROJO if "DESCONOCIDO" in usuario else CYAN
    
    # Colores por tipo de acción
    if any(x in tipo for x in ["COMANDO", "CALLBACK", "TYC"]): color_tipo = AMARILLO
    elif any(x in tipo for x in ["TEXTO", "WHATSAPP", "CONTACTO"]): color_tipo = AZUL
    elif any(x in tipo for x in ["IMAGEN", "AUDIO", "DOC", "VIDEO", "MUSICA"]): color_tipo = CYAN
    elif "SISTEMA" in tipo: color_tipo = ROJO
    else: color_tipo = RESET

    print(f"{color_tipo}[{hora}] 📥 {tipo} | User: {color_user}{usuario}{color_tipo} | {detalle}{RESET}")

def log_bot_response(agente, respuesta):
    """Registra las respuestas de los agentes en verde"""
    hora = datetime.now().strftime("%H:%M:%S")
    limpio = re.sub(r'\[DATA:.*?\]', '', respuesta).strip()
    print(f"\n{VERDE}[{hora}] 🤖 RESPONSE | Agente: {agente} | {limpio}{RESET}\n")
