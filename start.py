# start_local_with_ngrok.py
import subprocess
import time
from pyngrok import ngrok

# === CONFIGURACIÓN ===
PORT = 8001
AUTHTOKEN = "35GDak2iE3ooylkazp0MBExOJg5_5VufkCFcp9uWEpL1koiAg"  # <-- Pega tu token de ngrok aquí

# === INICIO NGROK ===
print("⏳ Configurando ngrok...")
ngrok.set_auth_token(AUTHTOKEN)

# Crear túnel público
public_url = ngrok.connect(PORT).public_url
print(f"🌐 URL pública: {public_url}")
print(f"📘 Swagger docs: {public_url}/docs")

# === INICIO DEL SERVIDOR ===
print("🚀 Iniciando servidor local...")
server = subprocess.Popen(
    ["uvicorn", "servidor:app", "--host", "0.0.0.0", f"--port={PORT}"]
)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Deteniendo servidor...")
    server.terminate()
    ngrok.disconnect(public_url)
    ngrok.kill()
