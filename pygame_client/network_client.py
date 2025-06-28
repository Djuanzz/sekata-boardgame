# pygame_client/network_client.py
import socket
import threading
import json
import queue

class NetworkClient:
    def __init__(self, host, port, received_queue):
        self.host = host
        self.port = port
        self.received_queue = received_queue
        self.polling = False

    def _parse_response(self, response_data):
        try:
            # Mengatasi kasus di mana server mungkin tidak mengirim body
            if b'\r\n\r\n' in response_data:
                _, body = response_data.split(b'\r\n\r\n', 1)
                if body:
                    return json.loads(body.decode('utf-8'))
            return {"success": False, "message": "No JSON body in response"}
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error parsing response: {e}")
            return {"success": False, "message": "Invalid response from server"}

    def _request_response(self, method, path, body=None):
        """Helper untuk aksi tunggal yang membutuhkan respons langsung."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.host, self.port))
                
                body_str = json.dumps(body) if body else ""
                request = (
                    f"{method} {path} HTTP/1.1\r\n"
                    f"Host: {self.host}\r\n"
                    f"Content-Type: application/json\r\n"
                    f"Content-Length: {len(body_str)}\r\n\r\n"
                    f"{body_str}"
                )
                sock.sendall(request.encode('utf-8'))
                response_data = sock.recv(4096)
                return self._parse_response(response_data)
        except ConnectionRefusedError:
            return {"success": False, "message": "Koneksi ke server ditolak. Pastikan server berjalan."}
        except Exception as e:
            return {"success": False, "message": f"Error jaringan: {e}"}

    # --- Metode Aksi Game ---
    
    def create_game(self, player_id):
        self.received_queue.put(self._request_response("POST", "/create_game", {"player_id": player_id}))

    def join_game(self, game_id, player_id):
        self.received_queue.put(self._request_response("POST", f"/join_game/{game_id}", {"player_id": player_id}))

    def send_game_action(self, path, body):
        """Mengirim aksi (submit, check, start) dan langsung mendapatkan feedback."""
        # Menjalankan di thread agar UI tidak freeze selama request
        threading.Thread(target=lambda: self.received_queue.put(
            {"type": "action_response", "data": self._request_response("POST", path, body)}
        ), daemon=True).start()

    # --- Polling ---

    def start_polling(self, game_id, player_id):
        self.polling = True
        self.poll_thread = threading.Thread(
            target=self._poll_status, args=(game_id, player_id), daemon=True
        )
        self.poll_thread.start()

    def stop_polling(self):
        self.polling = False

    def _poll_status(self, game_id, player_id):
        import time
        while self.polling:
            path = f"/game_status/{game_id}?player_id={player_id}"
            response = self._request_response("GET", path)
            self.received_queue.put({"type": "game_status", "data": response})
            
            # Jika ada pemenang, polling berhenti sendiri
            if response.get('data', {}).get('winner'):
                self.stop_polling()
            
            time.sleep(2)