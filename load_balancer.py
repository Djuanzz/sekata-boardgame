from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import requests
import itertools
import json
import re
from threading import Lock

BACKEND_SERVERS = [
    "http://192.168.0.113:8000",
]

LOAD_BALANCER_PORT = 6969

game_to_server_map = {}
map_lock = Lock()

server_cycler = itertools.cycle(BACKEND_SERVERS)

def get_target_server(path):
    match = re.search(r'/(?:join_game|start_game|game_status|submit_fragment|check_turn)/([A-Z0-9]{6})', path)
    
    if match:
        game_id = match.group(1)
        with map_lock:
            if game_id in game_to_server_map:
                server = game_to_server_map[game_id]
                print(f"STICKY: Meneruskan permintaan untuk game {game_id} ke {server}")
                return server
            else:
                print(f"ERROR: Menerima permintaan untuk game {game_id} yang tidak dikenal.")
                return None
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
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "message": "Game not found or invalid path"}).encode('utf-8'))
            return
            
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length) if content_length > 0 else None

            backend_url = f"{target_server}{self.path}"
            
            headers = {key: value for key, value in self.headers.items()}
            
            resp = requests.request(
                method,
                backend_url,
                headers=headers,
                data=request_body,
                timeout=10,
                stream=True
            )

            if self.path == '/create_game' and resp.status_code == 200:
                response_data = resp.json()
                if response_data.get("success"):
                    game_id = response_data.get("game_id")
                    if game_id:
                        with map_lock:
                            game_to_server_map[game_id] = target_server
                        print(f"SUCCESS: Game {game_id} dibuat dan dipetakan ke {target_server}")
                self.send_response(resp.status_code)
                for key, value in resp.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                        self.send_header(key, value)
                body_to_send = json.dumps(response_data).encode('utf-8')
                self.send_header('Content-Length', str(len(body_to_send)))
                self.end_headers()
                self.wfile.write(body_to_send)
                return

            self.send_response(resp.status_code)

            for key, value in resp.headers.items():
                if key.lower() not in ['content-encoding', 'transfer-encoding']:
                    self.send_header(key, value)
            self.end_headers()
            
            for chunk in resp.iter_content(chunk_size=8192):
                self.wfile.write(chunk)

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