# sekata_game/server.py
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import random
import string
import os
import urllib.parse
import threading # <-- IMPOR BARU untuk multithreading
from socketserver import ThreadingMixIn # <-- IMPOR BARU untuk membuat server multithreaded

# IMPOR DARI MODELS DAN UTILS
from models import Game, Player, POTONGAN_KATA, HAND_SIZE, MIN_PLAYERS_TO_START
from utils import is_word_in_dictionary, validate_word_formation, calculate_score_for_word

# --- Kelas Server Multithreaded ---
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """
    Server HTTP yang menangani setiap request di thread terpisah.
    Ini mencegah server terblokir oleh satu koneksi.
    """
    daemon_threads = True       # Memastikan thread-child akan mati saat server utama berhenti
    allow_reuse_address = True  # Mencegah error "Address already in use" saat server di-restart cepat

# --- Global Game State dan Lock ---
GAMES = {} # {game_id: GameInstance}
GAMES_LOCK = threading.Lock() # <-- LOCK BARU untuk melindungi akses ke dictionary GAMES

# --- Load Dictionary ---
DICTIONARY = set()
try:
    dictionary_path = os.path.join(os.path.dirname(__file__), 'static', 'dictionary.txt')
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        for line in f:
            DICTIONARY.add(line.strip().upper())
    print(f"Kamus berhasil dimuat: {len(DICTIONARY)} kata.")
except FileNotFoundError:
    print(f"WARNING: File dictionary.txt tidak ditemukan di '{dictionary_path}'. Validasi kata mungkin tidak berfungsi.")
    print("Memuat kata-kata dari POTONGAN_KATA sebagai kamus fallback.")
    DICTIONARY.update(set(word.upper() for word in POTONGAN_KATA)) # Fallback
    DICTIONARY.update({"KULIT", "RUMAH", "KOTA", "MATA", "HATI", "BUKU", "PENA", "PINTAR", "AKAN"})

# --- HTTP Request Handler (tidak ada perubahan di dalam kelas ini, hanya penggunaannya yang berbeda) ---
class SeKataHTTPHandler(SimpleHTTPRequestHandler):

    def read_request_body(self):
        """Membaca body request POST dan mengurai JSON."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))

    def send_json_response(self, status_code, data):
        """Mengirim respons JSON."""
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        # ... (Isi fungsi do_GET tetap sama, tidak perlu diubah) ...
        # ... Kita hanya akan memodifikasi handler API di bawahnya ...
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/game_status/'):
            self.handle_game_status(path, parsed_path.query)
        elif path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            try:
                with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "index.html not found.")
        elif path.startswith('/static/'):
            requested_file = os.path.normpath(path[len('/static/'):])
            
            if requested_file.startswith('..') or os.path.isabs(requested_file):
                self.send_error(403, "Forbidden")
                return

            filepath = os.path.join(os.path.dirname(__file__), 'static', requested_file)

            if os.path.exists(filepath) and os.path.isfile(filepath):
                self.send_response(200)
                if filepath.endswith('.css'):
                    self.send_header("Content-type", "text/css")
                elif filepath.endswith('.js'):
                    self.send_header("Content-type", "application/javascript")
                elif filepath.endswith('.txt'):
                    self.send_header("Content-type", "text/plain")
                else:
                    self.send_header("Content-type", "application/octet-stream")
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")
        else:
            self.send_error(404, "Not Found")


    def do_POST(self):
        # ... (Isi fungsi do_POST tetap sama, tidak perlu diubah) ...
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/create_game':
            self.handle_create_game()
        elif path.startswith('/join_game/'):
            self.handle_join_game(path)
        elif path.startswith('/start_game/'):
            self.handle_start_game(path)
        elif path.startswith('/submit_fragment/'):
            self.handle_submit_fragment(path)
        elif path.startswith('/check_turn/'):
            self.handle_check_turn(path)
        else:
            self.send_error(404, "Not Found")

    # --- Handler Metode API (sekarang menggunakan lock) ---

    def handle_create_game(self):
        try:
            request_data = self.read_request_body()
            player_id = request_data.get('player_id')
            if not player_id:
                self.send_json_response(400, {"success": False, "message": "Player ID required."})
                return

            game_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            new_game = Game(game_id, player_id)
            
            # Melindungi operasi penulisan ke dictionary global GAMES
            with GAMES_LOCK:
                GAMES[game_id] = new_game
            
            print(f"Game baru dibuat: {game_id} oleh {player_id}")
            self.send_json_response(200, {"success": True, "game_id": game_id})

        except Exception as e:
            print(f"Error creating game: {e}")
            self.send_json_response(500, {"success": False, "message": "Internal server error."})

    def handle_join_game(self, path):
        try:
            game_id = path.split('/')[2]
            request_data = self.read_request_body()
            player_id = request_data.get('player_id')

            if not game_id or not player_id:
                self.send_json_response(400, {"success": False, "message": "Game ID and Player ID required."})
                return

            # Melindungi operasi baca dan tulis pada state game
            with GAMES_LOCK:
                game = GAMES.get(game_id)
                if not game:
                    # Rilis lock sebelum mengirim respons
                    self.send_json_response(404, {"success": False, "message": "Game not found."})
                    return
                
                if game.game_started:
                    self.send_json_response(400, {"success": False, "message": "Game sudah dimulai, tidak bisa bergabung."})
                    return

                if game.add_player(player_id):
                    print(f"Pemain {player_id} bergabung ke game {game_id}")
                    self.send_json_response(200, {"success": True, "message": "Joined game successfully."})
                else:
                    self.send_json_response(400, {"success": False, "message": "Player sudah ada di game."})

        except Exception as e:
            print(f"Error joining game: {e}")
            self.send_json_response(500, {"success": False, "message": "Internal server error."})

    def handle_start_game(self, path):
        try:
            game_id = path.split('/')[2]
            request_data = self.read_request_body()
            player_id = request_data.get('player_id')

            with GAMES_LOCK:
                game = GAMES.get(game_id)
                if not game:
                    self.send_json_response(404, {"success": False, "message": "Game tidak ditemukan."})
                    return

                if game.host_id != player_id:
                    self.send_json_response(403, {"success": False, "message": "Hanya host yang bisa memulai game."})
                    return
                
                success, msg = game.start_game()
                if success:
                    self.send_json_response(200, {"success": True, "message": msg})
                else:
                    self.send_json_response(400, {"success": False, "message": msg})
        except Exception as e:
            print(f"Error starting game: {e}")
            self.send_json_response(500, {"success": False, "message": "Internal server error."})

    def handle_game_status(self, path, query_string):
        try:
            game_id = path.split('/')[2]
            query_params = urllib.parse.parse_qs(query_string)
            player_id = query_params.get('player_id', [None])[0]

            if not game_id or not player_id:
                self.send_json_response(400, {"success": False, "message": "Game ID and Player ID required."})
                return

            # Melindungi operasi pembacaan state game agar tidak terjadi "dirty read"
            with GAMES_LOCK:
                game = GAMES.get(game_id)
                if not game:
                    self.send_json_response(404, {"success": False, "message": "Game not found."})
                    return

                if player_id not in game.players:
                     self.send_json_response(403, {"success": False, "message": "Player not in this game."})
                     return

                # Mengambil state di dalam lock untuk memastikan data konsisten
                status = game.get_game_state_for_player(player_id)
            
            # Mengirim respons di luar lock
            self.send_json_response(200, {"success": True, "data": status})

        except Exception as e:
            print(f"Error getting game status: {e}")
            self.send_json_response(500, {"success": False, "message": "Internal server error."})

    def handle_submit_fragment(self, path):
        # Fungsi ini melakukan banyak modifikasi state, jadi harus dilindungi lock
        with GAMES_LOCK:
            try:
                game_id = path.split('/')[2]
                request_data = self.read_request_body()
                player_id = request_data.get('player_id')
                submitted_fragment = request_data.get('fragment')
                position = request_data.get('position')

                if not all([game_id, player_id, submitted_fragment, position]):
                    self.send_json_response(400, {"success": False, "message": "Data tidak lengkap."})
                    return
                
                game = GAMES.get(game_id)
                if not game:
                    self.send_json_response(404, {"success": False, "message": "Game tidak ditemukan."})
                    return
                
                if not game.game_started:
                     self.send_json_response(400, {"success": False, "message": "Game belum dimulai."})
                     return

                if game.current_turn_index is None or game.get_current_player_id() != player_id:
                    self.send_json_response(403, {"success": False, "message": "Bukan giliran Anda."})
                    return
                
                player = game.players[player_id]

                is_helper_used = (
                    hasattr(game, "helper_cards")
                    and game.helper_cards
                    and submitted_fragment.upper() in [h.upper() for h in game.helper_cards]
                )
                if not is_helper_used and not player.remove_card(submitted_fragment.upper()):
                    self.send_json_response(400, {"success": False, "message": f"Anda tidak memiliki kartu '{submitted_fragment}' di tangan maupun sebagai helper."})
                    return

                if is_helper_used:
                    game.helper_cards.remove(submitted_fragment.upper())

                if not game.card_on_table:
                     self.send_json_response(500, {"success": False, "message": "Tidak ada kartu di meja untuk disambung."})
                     return

                is_valid, msg, formed_word = validate_word_formation(
                    game.card_on_table,
                    submitted_fragment,
                    position,
                    DICTIONARY
                )

                if not is_valid:
                    player.add_cards([submitted_fragment.upper()])
                    self.send_json_response(400, {"success": False, "message": msg})
                    return
                
                game.discard_pile.append(game.card_on_table)
                game.card_on_table = submitted_fragment.upper()
                score_earned = calculate_score_for_word(formed_word)
                player.score += score_earned
                
                if game.check_for_winner():
                    self.send_json_response(200, {"success": True, "message": f"Anda menang! Kata terakhir: {formed_word}.", "winner": player_id})
                    return

                game.next_turn(action_was_check=False)

                print(f"Pemain {player_id} menyambung '{submitted_fragment}'. Kata terbentuk: '{formed_word}'.")
                self.send_json_response(200, {"success": True, "message": f"Berhasil menyambung kata menjadi '{formed_word}'.", "score_earned": score_earned})

            except Exception as e:
                print(f"Error submitting fragment: {e}")
                self.send_json_response(500, {"success": False, "message": f"Internal server error: {e}"})

    def handle_check_turn(self, path):
        # Fungsi ini juga memodifikasi state (giliran pemain), jadi perlu lock
        with GAMES_LOCK:
            try:
                game_id = path.split('/')[2]
                request_data = self.read_request_body()
                player_id = request_data.get('player_id')

                if not all([game_id, player_id]):
                    self.send_json_response(400, {"success": False, "message": "Data tidak lengkap."})
                    return

                game = GAMES.get(game_id)
                if not game:
                    self.send_json_response(404, {"success": False, "message": "Game tidak ditemukan."})
                    return

                if not game.game_started:
                     self.send_json_response(400, {"success": False, "message": "Game belum dimulai."})
                     return

                if game.current_turn_index is None or game.get_current_player_id() != player_id:
                    self.send_json_response(403, {"success": False, "message": "Bukan giliran Anda."})
                    return
                
                game.next_turn(action_was_check=True)

                if game.winner:
                    self.send_json_response(200, {"success": True, "message": f"Giliran dilewati. Game berakhir! Pemenang: {game.winner}"})
                else:
                    self.send_json_response(200, {"success": True, "message": "Giliran dilewati."})

                print(f"Pemain {player_id} melewati giliran di game {game_id}.")

            except Exception as e:
                print(f"Error passing turn: {e}")
                self.send_json_response(500, {"success": False, "message": f"Internal server error: {e}"})

# --- Main Server Setup (Menggunakan server multithreaded) ---
def run_server(server_class=ThreadingHTTPServer, handler_class=SeKataHTTPHandler, port=8000): # <-- UBAH KELAS SERVER DEFAULT
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Memulai HTTP server SeKata (Multithreaded) di http://localhost:{port}/")
    print(f"Tekan Ctrl+C untuk menghentikan server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("Server dihentikan.")

if __name__ == '__main__':
    run_server()