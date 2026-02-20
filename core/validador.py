import re

def es_email_valido(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email) is not None

def extraer_datos(texto):
    # Usamos lógica simple o podrías usar Gemini para extraer JSON
    # Por ahora, devolvemos lo que encontramos para que Sofía lo confirme
    return texto
