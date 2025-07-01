# http.py (Versi Final yang Sudah Dikoreksi)
import json
import os
import urllib.parse
from datetime import datetime
import logging

try:
    from models import Game
    from utils import validate_word_formation, calculate_score_for_word
except ImportError:
    print("ERROR di http.py: Pastikan file 'models.py' dan 'utils.py' dapat diimpor.")
    exit()

class HttpServer:
    def __init__(self, games_dict, games_lock, dictionary_set):
        self.GAMES = games_dict
        self.GAMES_LOCK = games_lock
        self.DICTIONARY = dictionary_set
        self.mime_types = { ".html": "text/html", ".css": "text/css", ".js": "application/javascript", ".json": "application/json", ".txt": "text/plain" }

    def build_response(self, status_code, status_text, headers, body):
        response_line = f"HTTP/1.1 {status_code} {status_text}\r\n"
        headers.update({'Server': 'Sekata-Modular-Server/1.0', 'Date': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'), 'Connection': 'close', 'Access-Control-Allow-Origin': '*'})
        if body:
            if not isinstance(body, bytes): body = body.encode('utf-8')
            headers['Content-Length'] = len(body)
        else:
            headers['Content-Length'] = 0
            body = b''
        headers_str = "".join([f"{k}: {v}\r\n" for k, v in headers.items()])
        return response_line.encode('utf-8') + headers_str.encode('utf-8') + b"\r\n" + body

    def json_response(self, status_code, status_text, data_dict):
        return self.build_response(status_code, status_text, {"Content-Type": "application/json"}, json.dumps(data_dict))

    def proses(self, request_text):
        logging.info(f"Memproses request:\n{request_text.strip()}")
        try:
            request_line, rest = request_text.split('\r\n', 1)
            headers_raw, body = (rest.split('\r\n\r\n', 1) + [''])[:2]
            method, full_path, _ = request_line.split(' ')
            if method == 'GET': return self.handle_get_request(full_path)
            if method == 'POST': return self.handle_post_request(full_path, body)
            return self.json_response(405, "Method Not Allowed", {"success": False, "message": "Method not allowed"})
        except Exception as e:
            logging.error(f"Error parsing request: {e}", exc_info=True)
            return self.json_response(500, "Internal Server Error", {"success": False, "message": f"Server error: {e}"})
            
    def handle_get_request(self, full_path):
        parsed_url = urllib.parse.urlparse(full_path)
        if parsed_url.path.startswith('/game_status/'): return self.handle_game_status(parsed_url.path, parsed_url.query)
        if parsed_url.path == '/': return self.serve_static_file('index.html')
        if parsed_url.path.startswith('/static/'): return self.serve_static_file(parsed_url.path[len('/static/'):], is_static=True)
        return self.json_response(404, "Not Found", {"success": False, "message": "Endpoint GET tidak ditemukan."})

    def handle_post_request(self, path, body):
        if path == '/create_game': return self.handle_create_game(body)
        if path.startswith('/join_game/'): return self.handle_join_game(path, body)
        if path.startswith('/start_game/'): return self.handle_start_game(path, body)
        if path.startswith('/submit_turn/'): return self.handle_submit_turn(path, body)
        if path.startswith('/check_turn/'): return self.handle_check_turn(path, body)
        return self.json_response(404, "Not Found", {"success": False, "message": "ENDPOINT POST tidak ditemukan."})
        
    def serve_static_file(self, requested_path, is_static=False):
        base_dir = os.path.dirname(__file__); rel_path = os.path.join('static', requested_path) if is_static else requested_path
        file_path = os.path.join(base_dir, rel_path)
        if not os.path.normpath(file_path).startswith(os.path.normpath(base_dir)):
            return self.json_response(403, "Forbidden", {"success": False, "message": "Akses dilarang."})
        if os.path.exists(file_path) and os.path.isfile(file_path):
            _, ext = os.path.splitext(file_path); content_type = self.mime_types.get(ext.lower(), "application/octet-stream")
            with open(file_path, 'rb') as f: body_bytes = f.read()
            return self.build_response(200, "OK", {"Content-Type": content_type}, body_bytes)
        return self.json_response(404, "Not Found", {"success": False, "message": f"File '{requested_path}' tidak ditemukan."})
            
    def _get_json_body(self, body):
        if not body: return {}
        try: return json.loads(body)
        except json.JSONDecodeError: return None

    # (Handler untuk create, join, start, status, check tidak berubah)
    def handle_create_game(self, body):
        request_data = self._get_json_body(body)
        if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})
        player_id = request_data.get('player_id')
        if not player_id: return self.json_response(400, "Bad Request", {"success": False, "message": "Player ID required."})
        game_id = ''.join(__import__('random').choices(__import__('string').ascii_uppercase + __import__('string').digits, k=6))
        new_game = Game(game_id, player_id)
        with self.GAMES_LOCK: self.GAMES[game_id] = new_game
        logging.info(f"Game baru dibuat: {game_id} oleh {player_id}")
        return self.json_response(200, "OK", {"success": True, "game_id": game_id})

    def handle_join_game(self, path, body):
        game_id = path.split('/')[2]; request_data = self._get_json_body(body)
        if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})
        player_id = request_data.get('player_id')
        with self.GAMES_LOCK: game = self.GAMES.get(game_id)
        if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game not found."})
        if game.add_player(player_id): return self.json_response(200, "OK", {"success": True, "message": "Joined game successfully."})
        return self.json_response(400, "Bad Request", {"success": False, "message": "Player sudah ada atau game sudah mulai."})

    def handle_start_game(self, path, body):
        game_id = path.split('/')[2]; request_data = self._get_json_body(body); player_id = request_data.get('player_id')
        with self.GAMES_LOCK:
            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game tidak ditemukan."})
            if game.host_id != player_id: return self.json_response(403, "Forbidden", {"success": False, "message": "Hanya host yang bisa memulai."})
            success, msg = game.start_game()
            if success: return self.json_response(200, "OK", {"success": True, "message": msg})
            return self.json_response(400, "Bad Request", {"success": False, "message": msg})
    
    def handle_game_status(self, path, query_string):
        game_id = path.split('/')[2]; query_params = urllib.parse.parse_qs(query_string); player_id = query_params.get('player_id', [None])[0]
        with self.GAMES_LOCK: game = self.GAMES.get(game_id)
        if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game not found."})
        status = game.get_game_state_for_player(player_id)
        return self.json_response(200, "OK", {"success": True, "data": status})

    def handle_check_turn(self, path, body):
        game_id = path.split('/')[2]; request_data = self._get_json_body(body); player_id = request_data.get('player_id')
        with self.GAMES_LOCK:
            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game tidak ditemukan."})
            if game.get_current_player_id() != player_id: return self.json_response(403, "Forbidden", {"success": False, "message": "Bukan giliran Anda."})
            game.next_turn(action_was_check=True)
            if game.winner: return self.json_response(200, "OK", {"success": True, "message": f"Giliran dilewati. Pemenang: {game.winner}"})
            return self.json_response(200, "OK", {"success": True, "message": "Giliran dilewati."})
            
    def handle_submit_turn(self, path, body):
        with self.GAMES_LOCK:
            game_id = path.split('/')[2]
            request_data = self._get_json_body(body)
            if request_data is None: return self.json_response(400, "Bad Request", {"success": False, "message": "Invalid JSON."})

            player_id = request_data.get('player_id')
            moves = request_data.get('moves')

            if not all([game_id, player_id, isinstance(moves, list)]):
                return self.json_response(400, "Bad Request", {"success": False, "message": "Data tidak lengkap (membutuhkan game_id, player_id, moves)."})
            
            if not moves:
                return self.json_response(400, "Bad Request", {"success": False, "message": "Tidak ada langkah yang dikirim."})

            game = self.GAMES.get(game_id)
            if not game: return self.json_response(404, "Not Found", {"success": False, "message": "Game tidak ditemukan."})
            if game.get_current_player_id() != player_id: return self.json_response(403, "Forbidden", {"success": False, "message": "Bukan giliran Anda."})
            
            player = game.players[player_id]

            hand_card_in_move = None
            helper_card_in_move = None
            for move in moves:
                card_type = move.get('type')
                card_value = move.get('card', '').upper()
                if card_type == 'hand':
                    if hand_card_in_move: return self.json_response(400, "Bad Request", {"success": False, "message": "Hanya boleh menggunakan 1 kartu tangan per giliran."})
                    if card_value not in player.hand: return self.json_response(400, "Bad Request", {"success": False, "message": f"Kartu '{card_value}' tidak ada di tangan Anda."})
                    hand_card_in_move = card_value
                elif card_type == 'helper':
                    if helper_card_in_move: return self.json_response(400, "Bad Request", {"success": False, "message": "Hanya boleh menggunakan 1 kartu helper per giliran."})
                    if card_value not in game.helper_cards: return self.json_response(400, "Bad Request", {"success": False, "message": f"Kartu helper '{card_value}' tidak valid."})
                    helper_card_in_move = card_value

            if not hand_card_in_move:
                 return self.json_response(400, "Bad Request", {"success": False, "message": "Anda harus menggunakan setidaknya 1 kartu dari tangan."})

            current_word = game.card_on_table
            for move in moves:
                card = move.get('card', '').upper()
                position = move.get('position')
                if position == 'before':
                    current_word = card + current_word
                elif position == 'after':
                    current_word = current_word + card
            
            final_word = current_word

            if final_word not in self.DICTIONARY:
                return self.json_response(400, "Bad Request", {"success": False, "message": f"Kata '{final_word}' tidak ada dalam kamus."})

            player.remove_card(hand_card_in_move)
            if helper_card_in_move:
                game.use_helper_card(helper_card_in_move)

            game.discard_pile.append(game.card_on_table)
            

            game.card_on_table = hand_card_in_move
            
            score_earned = calculate_score_for_word(final_word)
            player.score += score_earned
            
            if game.check_for_winner():
                return self.json_response(200, "OK", {"success": True, "message": f"Anda menang! Kata terakhir: {final_word}.", "winner": player_id})

            game.next_turn(action_was_check=False)
            
            success_msg = f"Berhasil membentuk kata '{final_word}'! (+{score_earned} poin)"
            logging.info(f"[{player_id}] {success_msg}")
            return self.json_response(200, "OK", {"success": True, "message": success_msg, "score_earned": score_earned})