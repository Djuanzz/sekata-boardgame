# http.py
import json
import os
import urllib.parse
from datetime import datetime
import logging

# Impor logika game dari models dan utils
# Pastikan file-file ini dapat diakses dari direktori kerja
try:
    from models import Game
    from utils import validate_word_formation, calculate_score_for_word
except ImportError:
    print("ERROR di http.py: Pastikan file 'models.py' dan 'utils.py' dapat diimpor.")
    exit()

class HttpServer:
    def __init__(self, games_dict, games_lock, dictionary_set):
        """
        Inisialisasi handler HTTP dengan state game dan kamus.
        State (GAMES, GAMES_LOCK) dikelola oleh server utama dan dioper ke sini.
        """
        self.GAMES = games_dict
        self.GAMES_LOCK = games_lock
        self.DICTIONARY = dictionary_set
        
        # Mapping Content-Type (MIME Type)
        self.mime_types = {
            ".html": "text/html",
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".txt": "text/plain",
            ".png": "image/png",
            ".jpg": "image/jpeg",
        }

    def build_response(self, status_code, status_text, headers, body):
        """Membangun response HTTP lengkap sebagai bytes."""
        response_line = f"HTTP/1.1 {status_code} {status_text}\r\n"
        
        # Header default
        headers['Server'] = "Sekata-Modular-Server/1.0"
        headers['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers['Connection'] = "close"
        headers['Access-Control-Allow-Origin'] = "*" # Penting untuk development
        
        if body:
            # Pastikan body adalah bytes sebelum menghitung panjangnya
            if not isinstance(body, bytes):
                body = body.encode('utf-8')
            headers['Content-Length'] = len(body)
        else:
            headers['Content-Length'] = 0
            body = b''

        headers_str = "".join([f"{k}: {v}\r\n" for k, v in headers.items()])
        
        # Gabungkan semua bagian, pastikan header di-encode
        return response_line.encode('utf-8') + headers_str.encode('utf-8') + b"\r\n" + body

    def json_response(self, status_code, status_text, data_dict):
        """Helper untuk membangun response JSON."""
        body = json.dumps(data_dict)
        headers = {"Content-Type": "application/json"}
        return self.build_response(status_code, status_text, headers, body)

    def proses(self, request_text):
        """
        Metode utama untuk memproses seluruh request HTTP mentah.
        Ini adalah satu-satunya metode yang dipanggil oleh server.py.
        """
        logging.info(f"Memproses request:\n--- REQ START ---\n{request_text.strip()}\n--- REQ END ---")
        try:
            # Parsing request
            request_line = request_text.split('\r\n', 1)[0]
            headers_raw, body = (request_text.split('\r\n\r\n', 1) + [''])[:2]

            method, full_path, _ = request_line.split(' ')
            
            # Routing
            if method == 'GET':
                return self.handle_get_request(full_path)
            elif method == 'POST':
                return self.handle_post_request(full_path, body)
            else:
                return self.json_response(405, "Method Not Allowed", {"success": False, "message": "Method not allowed"})
        except Exception as e:
            logging.error(f"Error saat mem-parsing atau me-routing request: {e}", exc_info=True)
            return self.json_response(500, "Internal Server Error", {"success": False, "message": f"Server error: {e}"})

    # --- ROUTING ---
    def handle_get_request(self, full_path):
        parsed_url = urllib.parse.urlparse(full_path)
        path = parsed_url.path
        query = parsed_url.query

        if path.startswith('/game_status/'):
            return self.handle_game_status(path, query)
        if path == '/':
            return self.serve_static_file('index.html')
        if path.startswith('/static/'):
            return self.serve_static_file(path[len('/static/'):], is_static=True)
        
        return self.json_response(404, "Not Found", {"success": False, "message": "Endpoint GET tidak ditemukan."})

    def handle_post_request(self, path, body):
        if path == '/create_game':
            return self.handle_create_game(body)
        if path.startswith('/join_game/'):
            return self.handle_join_game(path, body)
        if path.startswith('/start_game/'):
            return self.handle_start_game(path, body)
        if path.startswith('/submit_fragment/'):
            return self.handle_submit_fragment(path, body)
        if path.startswith('/check_turn/'):
            return self.handle_check_turn(path, body)
        
        return self.json_response(404, "Not Found", {"success": False, "message": "Endpoint POST tidak ditemukan."})
        
    # --- STATIC FILE SERVER ---
    def serve_static_file(self, requested_path, is_static=False):
        base_dir = os.path.dirname(__file__)
        rel_path = os.path.join('static', requested_path) if is_static else requested_path
        file_path = os.path.join(base_dir, rel_path)

        if not os.path.normpath(file_path).startswith(os.path.normpath(base_dir)):
            return self.json_response(403, "Forbidden", {"success": False, "message": "Akses dilarang."})

        if os.path.exists(file_path) and os.path.isfile(file_path):
            _, ext = os.path.splitext(file_path)
            content_type = self.mime_types.get(ext.lower(), "application/octet-stream")
            
            with open(file_path, 'rb') as f:
                body_bytes = f.read()
            
            return self.build_response(200, "OK", {"Content-Type": content_type}, body_bytes)
        else:
            return self.json_response(404, "Not Found", {"success": False, "message": f"File '{requested_path}' tidak ditemukan."})
            
    # --- API HANDLERS ---
    def _get_json_body(self, body):
        if not body: return {}
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def handle_create_game(self, body):
        request_data = self._get_json_body(body)
        if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})
        
        player_id = request_data.get('player_id')
        if not player_id: return self.json_response(400, "Bad Request", {"success": False, "message": "Player ID required."})

        game_id = ''.join(__import__('random').choices(__import__('string').ascii_uppercase + __import__('string').digits, k=6))
        new_game = Game(game_id, player_id)
        
        with self.GAMES_LOCK:
            self.GAMES[game_id] = new_game
        
        logging.info(f"Game baru dibuat: {game_id} oleh {player_id}")
        return self.json_response(200, "OK", {"success": True, "game_id": game_id})

    def handle_join_game(self, path, body):
        # ... Logika handle_join_game yang sudah ada, tapi gunakan self.GAMES_LOCK, self.GAMES, dan return self.json_response(...)
        # Contoh singkat:
        game_id = path.split('/')[2]
        request_data = self._get_json_body(body)
        if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})
        player_id = request_data.get('player_id')
        
        with self.GAMES_LOCK:
            game = self.GAMES.get(game_id)
            # ... (sisa logika)
        # return self.json_response(...)
        # (Logika lengkap disembunyikan untuk keringkasan, tetapi polanya sama dengan di atas dan di bawah)
        if not game_id or not player_id:
            return self.json_response(400, "Bad Request", {"success": False, "message": "Game ID and Player ID required."})

        with self.GAMES_LOCK:
            game = self.GAMES.get(game_id)
            if not game:
                return self.json_response(404, "Not Found", {"success": False, "message": "Game not found."})
            if game.game_started:
                return self.json_response(400, "Bad Request", {"success": False, "message": "Game sudah dimulai, tidak bisa bergabung."})
            
            if game.add_player(player_id):
                logging.info(f"Pemain {player_id} bergabung ke game {game_id}")
                return self.json_response(200, "OK", {"success": True, "message": "Joined game successfully."})
            else:
                return self.json_response(400, "Bad Request", {"success": False, "message": "Player sudah ada di game."})

    def handle_game_status(self, path, query_string):
        game_id = path.split('/')[2]
        query_params = urllib.parse.parse_qs(query_string)
        player_id = query_params.get('player_id', [None])[0]

        if not game_id or not player_id:
            return self.json_response(400, "Bad Request", {"success": False, "message": "Game ID and Player ID required."})

        with self.GAMES_LOCK:
            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game not found."})
            if player_id not in game.players: return self.json_response(403, "Forbidden", {"success": False, "message": "Player not in this game."})
            status = game.get_game_state_for_player(player_id)
        
        return self.json_response(200, "OK", {"success": True, "data": status})

    # ... (Implementasikan sisa handle_... method dengan pola yang sama)
    # Anda hanya perlu memindahkan kode dari `server.py` yang lama ke sini
    # dan mengubah `return self.send_json_response(...)` menjadi `return self.json_response(...)`
    # Pastikan juga menggunakan self.GAMES dan self.GAMES_LOCK
    # Berikut implementasi lengkapnya untuk kemudahan Anda:
    
    def handle_start_game(self, path, body):
        game_id = path.split('/')[2]
        request_data = self._get_json_body(body)
        if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})
        player_id = request_data.get('player_id')

        with self.GAMES_LOCK:
            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game tidak ditemukan."})
            if game.host_id != player_id: return self.json_response(403, "Forbidden", {"success": False, "message": "Hanya host yang bisa memulai game."})
            
            success, msg = game.start_game()
            if success:
                return self.json_response(200, "OK", {"success": True, "message": msg})
            else:
                return self.json_response(400, "Bad Request", {"success": False, "message": msg})

    def handle_submit_fragment(self, path, body):
        with self.GAMES_LOCK:
            game_id = path.split('/')[2]
            request_data = self._get_json_body(body)
            if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})

            player_id = request_data.get('player_id')
            submitted_fragment = request_data.get('fragment')
            position = request_data.get('position')
            helper_card = request_data.get('helper_card')

            if not all([player_id, submitted_fragment, position]):
                return self.json_response(400, "Bad Request", {"success": False, "message": "Data tidak lengkap."})

            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game tidak ditemukan."})
            if not game.game_started: return self.json_response(400, "Bad Request", {"success": False, "message": "Game belum dimulai."})
            if game.get_current_player_id() != player_id: return self.json_response(403, "Forbidden", {"success": False, "message": "Bukan giliran Anda."})
            
            player = game.players[player_id]

            if not player.remove_card(submitted_fragment.upper()):
                return self.json_response(400, "Bad Request", {"success": False, "message": f"Anda tidak memiliki kartu '{submitted_fragment}'."})

            effective_table_card = game.card_on_table
            used_helper = False
            if helper_card and helper_card.upper() in game.helper_cards:
                used_helper = True
                if position == 'before': effective_table_card = helper_card.upper() + game.card_on_table
                else: effective_table_card = game.card_on_table + helper_card.upper()
            
            is_valid, msg, formed_word = validate_word_formation(effective_table_card, submitted_fragment, position, self.DICTIONARY)

            if not is_valid:
                player.add_cards([submitted_fragment.upper()])
                return self.json_response(400, "Bad Request", {"success": False, "message": msg})

            if used_helper: game.use_helper_card(helper_card.upper())
            
            game.discard_pile.append(game.card_on_table)
            game.card_on_table = submitted_fragment.upper()
            score_earned = calculate_score_for_word(formed_word)
            player.score += score_earned
            
            if game.check_for_winner():
                return self.json_response(200, "OK", {"success": True, "message": f"Anda menang! Kata terakhir: {formed_word}.", "winner": player_id})

            game.next_turn(action_was_check=False)

            return self.json_response(200, "OK", {"success": True, "message": f"Berhasil menyambung kata menjadi '{formed_word}'.", "score_earned": score_earned, "helper_used": used_helper})

    def handle_check_turn(self, path, body):
        with self.GAMES_LOCK:
            game_id = path.split('/')[2]
            request_data = self._get_json_body(body)
            if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})
            player_id = request_data.get('player_id')

            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game tidak ditemukan."})
            if game.get_current_player_id() != player_id: return self.json_response(403, "Forbidden", {"success": False, "message": "Bukan giliran Anda."})
            
            game.next_turn(action_was_check=True)

            if game.winner:
                return self.json_response(200, "OK", {"success": True, "message": f"Giliran dilewati. Game berakhir! Pemenang: {game.winner}"})
            else:
                return self.json_response(200, "OK", {"success": True, "message": "Giliran dilewati."})