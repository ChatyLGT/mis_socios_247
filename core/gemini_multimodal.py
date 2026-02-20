import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
# Usamos el cliente asíncrono para que el bot fluya
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

async def procesar_multimodal(file_path, prompt_agente):
    if not file_path or not os.path.exists(file_path):
        return ""
    
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    
    ext = os.path.splitext(file_path)[1].lower()
    mime_type = "image/jpeg"
    if ext == ".pdf": mime_type = "application/pdf"
    elif ext in [".ogg", ".wav", ".mp3"]: mime_type = "audio/ogg"

    try:
        # LLAMADA ASÍNCRONA REAL
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
                f"{prompt_agente}. Analizá esto y respondé breve."
            ]
        )
        return response.text
    except Exception as e:
        print(f"❌ Error en Gemini Multimodal: {e}")
        return f"Tuve un error con el archivo."

async def procesar_texto_puro(prompt_sistema, texto_usuario):
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{prompt_sistema}\n\nUsuario dice: {texto_usuario}"
        )
        return response.text
    except Exception as e:
        print(f"❌ Error en Gemini Texto: {e}")
        return "Tuve un desliz en mis neuronas, ¿podés repetir?"
