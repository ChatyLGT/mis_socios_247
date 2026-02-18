from flask import Flask, request
import subprocess
from socio_vc import board_247 # Importamos tu Crew ya configurada

app = Flask(__name__)

@app.route("/whatsapp", methods=['POST'])
def reply():
    # 1. Recibe el mensaje de tu WhatsApp
    user_msg = request.form.get('Body')
    
    # 2. Se lo pasa al Board de Socios
    # (Aquí haríamos que el Estratega tome tu duda como una nueva Task)
    resultado = board_247.kickoff(inputs={'pregunta_usuario': user_msg})
    
    # 3. Usa 'wacli' para mandarte la respuesta de vuelta
    # Nota: wacli ya está ready en tu sistema
    comando_wa = f"wacli send +5212206809011 '{resultado}'"
    subprocess.run(comando_wa, shell=True)
    
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
