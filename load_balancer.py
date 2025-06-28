# load_balancer.py (Versi Final yang Diperbaiki dan Disederhanakan)

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import requests
import itertools
import json
import re
from threading import Lock

# --- KONFIGURASI ---
BACKEND_SERVERS = [
    "http://192.168.0.113:8000",
    #"http://127.0.0.1:8001",
]
LOAD_BALANCER_PORT = 6969

# --- Logika Inti ---
game_to_server_map = {}
map_lock = Lock()
server_cycler = itertools.cycle(BACKEND_SERVERS)

def get_target_server(path):
    match = re.search(r'/(?:join_game|start_game|game_status|submit_turn|check_turn)/([A-Z0-9]{6})', path)
    if match:
        game_id = match.group(1)
        with map_lock:
            server = game_to_server_map.get(game_id)
            if server:
                print(f"STICKY: Meneruskan permintaan game {game_id} ke {server}")
                return server
            else:
                print(f"WARNING: Game {game_id} tidak dikenal. Mencoba round-robin.")
                return next(server_cycler)
    elif path == '/create_game':
        server = next(server_cycler)
        print(f"NEW GAME: Memilih server {server} untuk game baru.")
        return server
    else:
        server = next(server_cycler)
        print(f"STATELESS: Meneruskan permintaan '{path}' ke {server}")
        return server

class LoadBalancerHandler(BaseHTTPRequestHandler):
    
    def _forward_request(self, method):
        target_server = get_target_server(self.path)
        
        if not target_server:
            self.send_error(404, "Game not found or invalid path")
            return
            
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None
            backend_url = f"{target_server}{self.path}"
            headers = {key: value for key, value in self.headers.items()}
            
            # --- PERUBAHAN UTAMA: Hapus `stream=True` ---
            # Biarkan `requests` mengunduh seluruh respons terlebih dahulu.
            resp = requests.request(
                method, backend_url, headers=headers, data=request_body, timeout=15
            )

            # --- LOGIKA YANG DISATUKAN ---
            # Dapatkan body mentah dari backend sebagai bytes.
            backend_body_bytes = resp.content

            # Cek apakah ini request pembuatan game yang sukses untuk pemetaan.
            if self.path == '/create_game' and resp.status_code == 200:
                try:
                    response_data = json.loads(backend_body_bytes.decode('utf-8'))
                    if response_data.get("success"):
                        game_id = response_data.get("game_id")
                        if game_id:
                            with map_lock:
                                game_to_server_map[game_id] = target_server
                            print(f"SUCCESS: Game {game_id} dibuat dan dipetakan ke {target_server}")
                except json.JSONDecodeError:
                    print("ERROR: Gagal mem-parsing JSON dari respons /create_game")

            # Teruskan header dari backend ke klien
            self.send_response(resp.status_code)
            for key, value in resp.headers.items():
                # Hapus header hop-by-hop yang tidak boleh diteruskan
                if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection', 'content-length']:
                    self.send_header(key, value)
            
            # Kirim Content-Length yang benar berdasarkan body yang kita terima
            self.send_header('Content-Length', str(len(backend_body_bytes)))
            self.end_headers()
            
            # Tulis seluruh body ke klien dalam satu operasi
            self.wfile.write(backend_body_bytes)

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Tidak dapat terhubung ke server backend {target_server}. Error: {e}")
            self.send_error(503, "Service Unavailable")

    def do_GET(self):
        self._forward_request('GET')

    def do_POST(self):
        self._forward_request('POST')

def run_load_balancer(server_class=ThreadingHTTPServer, handler_class=LoadBalancerHandler, port=LOAD_BALANCER_PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Memulai Load Balancer di http://localhost:{port}/")
    print(f"Meneruskan permintaan ke: {BACKEND_SERVERS}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Load Balancer dihentikan.")

if __name__ == '__main__':
    run_load_balancer()