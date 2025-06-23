# load_balancer.py

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import requests
import itertools
import json
import re
from threading import Lock

# --- KONFIGURASI ---
# Alamat server-server game backend Anda.
# Jalankan beberapa instance server.py di port-port ini.
# Contoh: python server.py --port 8001
#         python server.py --port 8002
BACKEND_SERVERS = [
    "http://192.168.0.113:8000",
    # Tambahkan lebih banyak server jika perlu
    # "http://localhost:8003",
]

# Port tempat load balancer akan berjalan
LOAD_BALANCER_PORT = 6969

# --- State untuk Sticky Session ---
# Peta untuk melacak game_id -> server_url
# Ini adalah komponen kunci untuk memastikan statefulness
game_to_server_map = {}
map_lock = Lock() # Untuk memastikan thread-safety saat memodifikasi peta

# Membuat iterator siklus untuk distribusi round-robin pada game BARU
server_cycler = itertools.cycle(BACKEND_SERVERS)

def get_target_server(path):
    """
    Menentukan server backend mana yang harus menangani permintaan.
    Ini adalah inti dari logika sticky session.
    """
    # Mencari game_id dalam path, contoh: /join_game/A1B2C3/
    match = re.search(r'/(?:join_game|start_game|game_status|submit_fragment|check_turn)/([A-Z0-9]{6})', path)
    
    if match:
        game_id = match.group(1)
        with map_lock:
            # Jika game_id sudah ada di peta, kembalikan server yang sesuai
            if game_id in game_to_server_map:
                server = game_to_server_map[game_id]
                print(f"STICKY: Meneruskan permintaan untuk game {game_id} ke {server}")
                return server
            else:
                # Jika game_id tidak ditemukan, ini adalah kondisi error.
                # Seharusnya game sudah dibuat melalui /create_game terlebih dahulu.
                print(f"ERROR: Menerima permintaan untuk game {game_id} yang tidak dikenal.")
                return None
    elif path == '/create_game':
        # Untuk game baru, pilih server berikutnya dalam siklus (round-robin)
        server = next(server_cycler)
        print(f"NEW GAME: Memilih server {server} untuk game baru.")
        return server
    else:
        # Untuk permintaan stateless (seperti /, /static/*), gunakan round-robin
        server = next(server_cycler)
        print(f"STATELESS: Meneruskan permintaan '{path}' ke {server}")
        return server


class LoadBalancerHandler(BaseHTTPRequestHandler):
    
    def _forward_request(self, method):
        """Meneruskan permintaan ke server backend yang sesuai."""
        
        target_server = get_target_server(self.path)
        
        if not target_server:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Game not found or invalid path"}).encode('utf-8'))
            return
            
        try:
            # Membaca body dari permintaan asli
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None

            # Membuat permintaan baru ke server backend
            backend_url = f"{target_server}{self.path}"
            
            headers = {key: value for key, value in self.headers.items()}
            # `requests` menangani Host header sendiri
            
            resp = requests.request(
                method,
                backend_url,
                headers=headers,
                data=request_body,
                timeout=10, # Tambahkan timeout
                stream=True # Penting untuk respons besar
            )

            # --- Logika Kunci untuk Sticky Session ---
            # Jika ini adalah permintaan pembuatan game yang berhasil, simpan mappingnya
            if self.path == '/create_game' and resp.status_code == 200:
                # Baca respons untuk mendapatkan game_id
                response_data = resp.json()
                if response_data.get("success"):
                    game_id = response_data.get("game_id")
                    if game_id:
                        with map_lock:
                            game_to_server_map[game_id] = target_server
                        print(f"SUCCESS: Game {game_id} dibuat dan dipetakan ke {target_server}")
                # Kirim respons asli kembali ke klien
                self.send_response(resp.status_code)
                for key, value in resp.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                        self.send_header(key, value)
                # Kirimkan body yang sudah kita baca
                body_to_send = json.dumps(response_data).encode('utf-8')
                self.send_header('Content-Length', str(len(body_to_send)))
                self.end_headers()
                self.wfile.write(body_to_send)
                return

            # Meneruskan respons dari backend kembali ke klien asli
            self.send_response(resp.status_code)

            # Salin header dari respons backend ke respons yang akan dikirim ke klien
            for key, value in resp.headers.items():
                 # Hindari menyalin header ini karena bisa menyebabkan masalah
                if key.lower() not in ['content-encoding', 'transfer-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            
            # Tulis body dari respons backend ke klien
            for chunk in resp.iter_content(chunk_size=8192):
                self.wfile.write(chunk)

        except requests.exceptions.RequestException as e:
            print(f"ERROR: Tidak dapat terhubung ke server backend {target_server}. Error: {e}")
            self.send_error(503, "Service Unavailable")

    def do_GET(self):
        self._forward_request('GET')

    def do_POST(self):
        self._forward_request('POST')
        
    # Tambahkan metode lain jika diperlukan (PUT, DELETE, dll.)
    # def do_PUT(self):
    #     self._forward_request('PUT')

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