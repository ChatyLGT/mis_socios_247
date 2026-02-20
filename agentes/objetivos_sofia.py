def obtener_checklist():
    return """
    Analiza el historial de conversación y responde ÚNICAMENTE con la palabra 'COMPLETO' si tenemos estos 3 datos:
    1. Nombre real de la persona.
    2. Nombre de su negocio o proyecto.
    3. Email válido (que contenga @ y un dominio).
    
    Si falta algo, responde detallando qué falta (ej: 'FALTA: Email').
    """
