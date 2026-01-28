import http.server
import socketserver
import json
import os
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# CONFIGURACIÓN
PORT = 8000
DATA_DIR = "data"
LOG_FILE = "server.log"

# --- CONFIGURACIÓN DEL LOG ---
# Esto guardará un registro en 'server.log' con fecha, nivel y mensaje
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Asegurar que existe la carpeta de datos
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class PillTrackerHandler(http.server.SimpleHTTPRequestHandler):
    def log_action(self, user_id, action, status, details=""):
        """Función auxiliar para escribir en el log de forma ordenada"""
        logging.info(f"Usuario: {user_id} | Acción: {action} | Estado: {status} | Info: {details}")

    def do_GET(self):
        # 1. Manejar petición de API para LEER datos
        if self.path.startswith('/api/pastillas'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Obtener ID del usuario de la URL
            query = parse_qs(urlparse(self.path).query)
            user_id = query.get('id', ['default'])[0]
            # Limpiar ID por seguridad
            user_id = "".join(x for x in user_id if x.isalnum() or x in "_-")
            
            file_path = os.path.join(DATA_DIR, f"user_{user_id}.json")

            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'null')
                # Opcional: Loguear si un usuario intenta leer datos que no existen
                # self.log_action(user_id, "LEER", "No encontrado")
            return

        # 2. Si no es API, servir archivos normales (HTML, CSS, JS)
        super().do_GET()

    def do_POST(self):
        # 1. Manejar petición de API para GUARDAR datos
        if self.path.startswith('/api/pastillas'):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Obtener ID del usuario
            query = parse_qs(urlparse(self.path).query)
            user_id = query.get('id', ['default'])[0]
            user_id = "".join(x for x in user_id if x.isalnum() or x in "_-")
            
            file_path = os.path.join(DATA_DIR, f"user_{user_id}.json")

            try:
                # Verificar que es JSON válido
                json_data = json.loads(post_data.decode('utf-8'))
                
                # Guardar en disco
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                
                # --- LOG: REGISTRAR CAMBIO EXITOSO ---
                self.log_action(user_id, "GUARDAR", "Éxito", "Datos actualizados correctamente")

            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
                
                # --- LOG: REGISTRAR ERROR ---
                logging.error(f"Usuario: {user_id} | Acción: GUARDAR | Estado: ERROR | Error: {str(e)}")
            return

    # Permitir CORS para desarrollo local si fuera necesario
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# Iniciar el servidor
print(f"💊 Servidor Python corriendo en http://localhost:{PORT}")
print(f"📂 Los datos se guardarán en la carpeta: ./{DATA_DIR}/")
print(f"📝 Los registros (logs) se guardarán en: {LOG_FILE}")

with socketserver.TCPServer(("", PORT), PillTrackerHandler) as httpd:
    httpd.serve_forever()