# sekata_game/models.py
import random
import string

# --- Konfigurasi Game ---
# Contoh potongan kata (ini bisa sangat banyak dan bervariasi)
# Anda bisa menggunakan logika untuk memecah kata utuh menjadi potongan acak
POTONGAN_KATA = [
    "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
    "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    "BA", "AK", "KA", "AT", "SA", "AN", 
    "PA", "AR", "LA", "AH", "DO", "JI"
    "SE", "AS", "MA", "AM", "TA", "AL",
    "RA", "NG", "GA", "US", "SU", "IK",
    "DA", "AI", "KE", "UR", "KU", "TA",
    "TE", "UK", "BU", "UT", "SI", "AP",
    "JA", "UH", "PE", "RA", "PU", "IS",
    "BE", "RI", "BO", "OK", "GE", "MA",
    "LE", "IT", "TU", "SI", "BI", "IR",
    "CA", "UN", "TI", "IL", "HA", "IN",
    "DE", "ER", "KO", "SA", "KI", "ET",
    "NA", "DA", "PI", "TI", "LI", "ON",
    "LU", "EK", "PO", "EN", "AM", "OR",
    "MU", "PA", "RO", "DI", "CE", "LI",
    "AL", "IH", "AN", "AU", "RE", "LA",
    "AK", "YA", "GI", "BU", "MI", "TU",
    "TO", "GA", "WA", "NA", "AR", "ES",
    "GU", "EL", "IN", "KA", "ME", "WA",
    "SO", "UL", "AS", "NI", "DU", "UM",
    "JU", "IA", "GO", "IM", "LO", "KU",
    "MO", "DU", "RU", "TO", "DI", "PI",
    "CU", "BA", "FA", "RU", "JE", "TE",
    "AB", "OT", "CI", "LU", "EN", "AB",
    "FO", "RO", "RI", "LO", "HI", "OS",
    "NO", "EM", "UR", "JA", "AJ", "OL",

]

HAND_SIZE = 7 # Jumlah kartu di tangan pemain
MIN_PLAYERS_TO_START = 2 # Minimal pemain untuk memulai game

# --- Kelas CardDeck ---
class CardDeck:
    def __init__(self, card_list):
        self.cards = list(card_list)
        random.shuffle(self.cards)

    def draw_card(self):
        """Mengambil satu kartu dari deck."""
        if not self.cards:
            return None
        return self.cards.pop()

    def add_card(self, card):
        """Menambahkan kartu kembali ke deck (misal: kartu yang tidak terpakai/dibuang)."""
        self.cards.append(card)
        # Tidak perlu kocok ulang setiap kali add, cukup saat inisialisasi atau reshuffle besar
        # random.shuffle(self.cards) 

    def get_cards(self, num):
        """Mengambil beberapa kartu dari deck."""
        drawn_cards = []
        for _ in range(num):
            card = self.draw_card()
            if card:
                drawn_cards.append(card)
            else:
                break
        return drawn_cards
    
    def shuffle_remaining(self):
        """Mengocok ulang kartu yang tersisa di deck."""
        random.shuffle(self.cards)

# --- Kelas Player ---
class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.hand = [] # Kartu potongan kata di tangan pemain
        self.score = 0 # Skor mungkin tidak terlalu relevan jika menang berdasarkan kartu habis
        self.last_action_check = False # Untuk melacak aksi 'Check' berturut-turut

    def add_cards(self, cards):
        """Menambahkan kartu ke tangan pemain."""
        self.hand.extend(cards)

    def remove_card(self, card_to_remove):
        """Menghapus kartu tertentu dari tangan pemain."""
        try:
            self.hand.remove(card_to_remove)
            return True
        except ValueError:
            return False # Kartu tidak ada di tangan

# --- Kelas Game ---
class Game:
    def __init__(self, game_id, host_id):
        self.game_id = game_id
        self.host_id = host_id
        self.players = {host_id: Player(host_id)} # {player_id: Player_object}
        self.player_order = [host_id] # Urutan giliran pemain
        self.main_deck = CardDeck(POTONGAN_KATA) # Deck utama potongan kata
        self.discard_pile = [] # Tumpukan buangan

        self.card_on_table = None # Hanya satu kartu terbuka di meja
        self.current_turn_index = 0 # Indeks pemain yang gilirannya saat ini

        self.game_started = False
        self.check_count = 0 # Menghitung berapa kali 'Check' berturut-turut
        self.winner = None

    def add_player(self, player_id):
        """Menambahkan pemain baru ke game."""
        if player_id not in self.players:
            new_player = Player(player_id)
            self.players[player_id] = new_player
            self.player_order.append(player_id)
            return True
        return False

    def start_game(self):
        """Memulai permainan."""
        if len(self.players) < MIN_PLAYERS_TO_START:
            return False, f"Membutuhkan minimal {MIN_PLAYERS_TO_START} pemain untuk memulai."
        
        if self.game_started:
            return False, "Game sudah dimulai."

        self.game_started = True
        random.shuffle(self.player_order) # Kocok urutan pemain
        self.current_turn_index = 0
        self.players[self.player_order[self.current_turn_index]].last_action_check = False # Reset

        # Bagikan kartu awal ke semua pemain
        for player_obj in self.players.values():
            cards = self.main_deck.get_cards(HAND_SIZE)
            player_obj.add_cards(cards)

        # Letakkan kartu pertama di meja
        self.card_on_table = self.main_deck.draw_card()
        if not self.card_on_table: # Jika deck kosong di awal (sangat jarang)
            return False, "Deck kata kosong, tidak bisa memulai game."
        
        print(f"Game {self.game_id} dimulai! Giliran {self.get_current_player_id()}")
        return True, "Game dimulai!"

    def get_current_player_id(self):
        """Mengembalikan ID pemain yang gilirannya saat ini."""
        if not self.game_started or not self.player_order:
            return None
        return self.player_order[self.current_turn_index]

    def next_turn(self, action_was_check=False):
        """Mengganti giliran ke pemain berikutnya."""
        if not self.game_started or not self.player_order:
            return

        current_player_obj = self.players[self.get_current_player_id()]
        current_player_obj.last_action_check = action_was_check

        if action_was_check:
            self.check_count += 1
            if self.check_count >= len(self.player_order): # Semua pemain 'Check'
                print(f"Semua pemain 'Check'. Melakukan reshuffle meja.")
                self.reshuffle_table_card()
                self.check_count = 0 # Reset hitungan 'Check'
        else:
            self.check_count = 0 # Reset jika ada pemain yang bergerak

        self.current_turn_index = (self.current_turn_index + 1) % len(self.player_order)
        print(f"Giliran berikutnya: {self.get_current_player_id()}")

    def reshuffle_table_card(self):
        """Mengganti kartu di meja dengan yang baru dari deck."""
        if self.card_on_table:
            self.discard_pile.append(self.card_on_table) # Buang kartu lama ke discard
        
        new_card = self.main_deck.draw_card()
        if not new_card and self.discard_pile: # Jika deck utama kosong, kocok ulang discard pile
            print("Deck utama kosong. Mengocok ulang discard pile.")
            self.main_deck.cards.extend(self.discard_pile)
            self.main_deck.shuffle_remaining()
            self.discard_pile = []
            new_card = self.main_deck.draw_card() # Coba ambil lagi

        self.card_on_table = new_card
        print(f"Kartu di meja di-reshuffle menjadi: {self.card_on_table}")
        if not self.card_on_table:
            self.winner = self.get_current_player_id() # Atau kondisi game over lain
            print(f"Game {self.game_id} berakhir karena deck kosong total.")


    def check_for_winner(self):
        """Mengecek apakah ada pemain yang kehabisan kartu."""
        for player_id, player_obj in self.players.items():
            if not player_obj.hand:
                self.winner = player_id
                self.game_started = False # Hentikan game
                print(f"Pemenang: {player_id}! Game berakhir.")
                return True
        return False


    def get_game_state_for_player(self, viewer_player_id):
        """Mengembalikan representasi status game yang aman untuk dikirim ke client."""
        players_data = {}
        for pid, player_obj in self.players.items():
            players_data[pid] = {
                "score": player_obj.score, # Mungkin tidak digunakan untuk game ini
                "hand_size": len(player_obj.hand),
                "hand": player_obj.hand if pid == viewer_player_id else [] # Hanya kirim tangan pemain yang sedang melihat
            }
        
        return {
            "game_id": self.game_id,
            "host_id": self.host_id,
            "card_on_table": self.card_on_table,
            "current_turn": self.get_current_player_id(),
            "players": players_data,
            "main_deck_count": len(self.main_deck.cards),
            "game_started": self.game_started,
            "check_count": self.check_count,
            "winner": self.winner,
            "min_players_to_start": MIN_PLAYERS_TO_START,
            "current_players_count": len(self.players)
        }