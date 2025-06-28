# pygame_client/game_state.py
class GameState:
    def __init__(self):
        self.scene = "login"
        self.player_id = ""
        self.game_id = ""
        self.game_data = None 
        
        # BARU: State untuk kartu yang dipilih sebelum aksi
        self.staged_card = None
        self.staged_card_type = None # 'hand' atau 'helper'

        self.popup_message = ""
        self.popup_type = "info"
        self.popup_timer = 0

    def update_from_server(self, data):
        self.game_data = data
        if data.get("winner"): self.scene = "game_over"
        elif not data.get("game_started"): self.scene = "lobby"
        else: self.scene = "game"
        
    def set_popup(self, text, popup_type="info", duration_seconds=2.5):
        self.popup_message = text
        self.popup_type = popup_type
        self.popup_timer = 30 * duration_seconds

    def clear_turn_selections(self):
        """Mereset pilihan kartu yang di-stage."""
        self.staged_card = None
        self.staged_card_type = None