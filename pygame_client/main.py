# pygame_client/main.py (Versi Final dengan UI yang Direkomendasikan)
import pygame
import queue
from game_state import GameState
from network_client import NetworkClient
from ui_elements import Button, Card, TextInputBox, FONT_BOLD, FONT_NORMAL, FONT_SMALL, FONT_CARD, COLOR_SUCCESS, COLOR_DANGER, COLOR_INFO, COLOR_WARNING, COLOR_PRIMARY, COLOR_DARK_GRAY, COLOR_WHITE

# Konfigurasi
SCREEN_WIDTH, SCREEN_HEIGHT = 900, 750
SERVER_HOST, SERVER_PORT = "localhost", 8000

# State Lokal Giliran
turn_moves = []
preview_word = ""
hand_card_used_this_turn = False
helper_card_used_this_turn = False

# Inisialisasi
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sekata - Klien Pygame")
clock = pygame.time.Clock()
state = GameState()
received_queue = queue.Queue()
network = NetworkClient(SERVER_HOST, SERVER_PORT, received_queue)

def reset_turn_state():
    global turn_moves, preview_word, hand_card_used_this_turn, helper_card_used_this_turn
    turn_moves.clear()
    preview_word = state.game_data.get('card_on_table', '') if state.game_data else ''
    hand_card_used_this_turn = False
    helper_card_used_this_turn = False
    state.clear_turn_selections()

def draw_text(text, font, color, x, y, center_x=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center_x else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)

# --- Drawing Functions ---
def draw_login_scene(elements): # (Tidak berubah)
    screen.fill((248, 249, 250)); draw_text("Sekata", FONT_BOLD, COLOR_PRIMARY, SCREEN_WIDTH // 2, 50, center_x=True)
    for element in elements.values(): element.draw(screen)
    if state.popup_timer > 0: draw_popup()

def draw_lobby_scene(elements): # (Tidak berubah)
    screen.fill((248, 249, 250));
    if not state.game_data: return
    draw_text(f"Lobi Game: {state.game_id}", FONT_BOLD, COLOR_DARK_GRAY, SCREEN_WIDTH//2, 100, center_x=True)
    players = state.game_data.get('players', {}); draw_text(f"Pemain: {len(players)}/{state.game_data.get('min_players_to_start')}", FONT_NORMAL, COLOR_DARK_GRAY, SCREEN_WIDTH//2, 150, center_x=True)
    y_offset = 200
    for p_id in players: draw_text(p_id, FONT_NORMAL, COLOR_DARK_GRAY, SCREEN_WIDTH//2, y_offset, center_x=True); y_offset += 30
    if state.player_id == state.game_data.get('host_id') and len(players) >= state.game_data.get('min_players_to_start'):
        elements['start_game_btn'].draw(screen)

def draw_game_scene(elements):
    screen.fill((248, 249, 250))
    if not state.game_data: return
    is_my_turn = state.game_data.get('current_turn') == state.player_id
    
    draw_word_preview()
    draw_main_action_area(elements, is_my_turn)
    draw_player_hand(elements, is_my_turn)
    draw_helper_area(elements, is_my_turn)
    draw_final_turn_actions(elements, is_my_turn)
    draw_score_list()
    
    if state.game_data.get('winner'):
        draw_text(f"Pemenang: {state.game_data['winner']}!", pygame.font.SysFont("Segoe UI", 50, bold=True), COLOR_SUCCESS, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center_x=True)

def draw_word_preview():
    draw_text("Kata yang Dibangun:", FONT_BOLD, COLOR_PRIMARY, SCREEN_WIDTH // 2, 20, center_x=True)
    preview_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, 80)
    pygame.draw.rect(screen, (220, 220, 220), preview_rect, border_radius=8)
    draw_text(preview_word, FONT_CARD, COLOR_DARK_GRAY, SCREEN_WIDTH // 2, 90, center_x=True)

def draw_main_action_area(elements, is_my_turn):
    draw_text("Area Aksi", FONT_BOLD, COLOR_PRIMARY, SCREEN_WIDTH//2, 160, center_x=True)
    
    staged_card_text = state.staged_card if state.staged_card else "Pilih Kartu"
    staged_card_color = COLOR_DANGER if state.staged_card is None else COLOR_SUCCESS
    draw_text(f"Kartu Aktif: {staged_card_text}", FONT_NORMAL, staged_card_color, SCREEN_WIDTH//2, 200, center_x=True)
    
    elements['action_before_btn'].disabled = not is_my_turn or state.staged_card is None
    elements['action_after_btn'].disabled = not is_my_turn or state.staged_card is None
    
    elements['action_before_btn'].draw(screen)
    elements['action_after_btn'].draw(screen)

def draw_player_hand(elements, is_my_turn):
    draw_text("Tangan Anda:", FONT_BOLD, COLOR_PRIMARY, SCREEN_WIDTH // 2, 480, center_x=True)
    player_hand = state.game_data.get('players', {}).get(state.player_id, {}).get('hand', [])
    elements['hand_cards'] = []
    
    card_width = 120
    start_x = (SCREEN_WIDTH - len(player_hand) * card_width) / 2
    for i, card_text in enumerate(player_hand):
        is_selected = (state.staged_card == card_text and state.staged_card_type == 'hand')
        card_ui = Card(start_x + i * card_width, 510, card_text, is_selected=is_selected)
        if hand_card_used_this_turn:
            # Jika sudah dipakai, gambar kartu tapi jangan tambahkan ke elemen interaktif
            pygame.draw.rect(screen, (0,0,0,150), card_ui.rect, border_radius=8)
        else:
            elements['hand_cards'].append(card_ui)
        card_ui.draw(screen)

def draw_helper_area(elements, is_my_turn):
    draw_text("Kartu Helper:", FONT_BOLD, COLOR_PRIMARY, SCREEN_WIDTH // 2, 320, center_x=True)
    helper_cards = state.game_data.get('helper_cards', [])
    elements['helper_cards'] = []
    
    card_width = 120
    start_x = (SCREEN_WIDTH - len(helper_cards) * card_width) / 2
    for i, card_text in enumerate(helper_cards):
        is_selected = (state.staged_card == card_text and state.staged_card_type == 'helper')
        card_ui = Card(start_x + i * card_width, 350, card_text, is_selected=is_selected, is_helper=True)
        if helper_card_used_this_turn:
            pygame.draw.rect(screen, (0,0,0,150), card_ui.rect, border_radius=8)
        else:
            elements['helper_cards'].append(card_ui)
        card_ui.draw(screen)

def draw_final_turn_actions(elements, is_my_turn):
    elements['submit_word_btn'].disabled = not is_my_turn or not hand_card_used_this_turn
    elements['reset_turn_btn'].disabled = not is_my_turn or len(turn_moves) == 0
    elements['check_turn_btn'].disabled = not is_my_turn or len(turn_moves) > 0

    elements['submit_word_btn'].draw(screen)
    elements['reset_turn_btn'].draw(screen)
    elements['check_turn_btn'].draw(screen)

def draw_score_list():
    draw_text("Info Pemain:", FONT_BOLD, COLOR_PRIMARY, 750, 160)
    players_info = state.game_data.get('players', {})
    y_offset = 200
    for p_id, p_data in players_info.items():
        text = f"{p_id}: {p_data['hand_size']} kartu"
        font = FONT_BOLD if p_id == state.player_id else FONT_NORMAL
        draw_text(text, font, COLOR_DARK_GRAY, 750, y_offset); y_offset += 30

def draw_popup(): # (Tidak berubah)
    if state.popup_timer > 0:
        popup_color = COLOR_SUCCESS if state.popup_type == 'success' else COLOR_DANGER; overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 128)); screen.blit(overlay, (0, 0)); popup_rect = pygame.Rect(0, 0, 500, 150); popup_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2); pygame.draw.rect(screen, COLOR_WHITE, popup_rect, border_radius=15); pygame.draw.rect(screen, popup_color, popup_rect, 5, border_radius=15); draw_text(state.popup_message, FONT_BOLD, popup_color, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center_x=True)

def main():
    running = True
    login_elements = {
        'name_input': TextInputBox(SCREEN_WIDTH // 2 - 220, 150, 200, 50, "Nama Pemain"), 'create_btn': Button(SCREEN_WIDTH // 2 + 20, 150, 200, 50, "Buat Game"),
        'game_id_input': TextInputBox(SCREEN_WIDTH // 2 - 220, 220, 200, 50, "ID Game"), 'join_btn': Button(SCREEN_WIDTH // 2 + 20, 220, 200, 50, "Gabung Game", color=COLOR_SUCCESS),
    }
    game_elements = {
        'start_game_btn': Button(SCREEN_WIDTH//2-100, 400, 200, 50, "Mulai Game"),
        'action_before_btn': Button(SCREEN_WIDTH // 2 - 200, 240, 180, 50, "Sambung Depan", COLOR_INFO),
        'action_after_btn': Button(SCREEN_WIDTH // 2 + 20, 240, 180, 50, "Sambung Belakang", COLOR_INFO),
        'submit_word_btn': Button(SCREEN_WIDTH // 2 - 100, 650, 200, 50, "Kirim Kata", COLOR_PRIMARY),
        'reset_turn_btn': Button(SCREEN_WIDTH // 2 - 220, 710, 150, 30, "Reset Giliran", COLOR_WARNING),
        'check_turn_btn': Button(SCREEN_WIDTH // 2 + 70, 710, 150, 30, "Check", COLOR_DARK_GRAY),
    }

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False
            if state.popup_timer > 0: continue

            if state.scene == 'login':
                for el in login_elements.values():
                    if isinstance(el, TextInputBox): el.handle_event(event)
                if login_elements['create_btn'].is_clicked(event) and login_elements['name_input'].text:
                    state.player_id = login_elements['name_input'].text; network.create_game(state.player_id)
                if login_elements['join_btn'].is_clicked(event) and login_elements['name_input'].text and login_elements['game_id_input'].text:
                    state.player_id = login_elements['name_input'].text; state.game_id = login_elements['game_id_input'].text; network.join_game(state.game_id, state.player_id)

            elif state.scene == 'lobby':
                if game_elements['start_game_btn'].is_clicked(event): network.send_game_action(f"/start_game/{state.game_id}", {"player_id": state.player_id})

            elif state.scene == 'game':
                is_my_turn = state.game_data.get('current_turn') == state.player_id
                if not is_my_turn: continue

                if event.type == pygame.MOUSEBUTTONDOWN:
                    global preview_word, hand_card_used_this_turn, helper_card_used_this_turn
                    # Pilih kartu tangan
                    if not hand_card_used_this_turn:
                        for card_ui in game_elements.get('hand_cards', []):
                            if card_ui.is_clicked(event):
                                if state.staged_card == card_ui.text: state.clear_turn_selections()
                                else: state.staged_card, state.staged_card_type = card_ui.text, 'hand'
                    # Pilih kartu helper
                    if not helper_card_used_this_turn:
                        for card_ui in game_elements.get('helper_cards', []):
                            if card_ui.is_clicked(event):
                                if state.staged_card == card_ui.text: state.clear_turn_selections()
                                else: state.staged_card, state.staged_card_type = card_ui.text, 'helper'
                    
                    # Aksi utama
                    def apply_action(position):
                        global preview_word, hand_card_used_this_turn, helper_card_used_this_turn
                        turn_moves.append({'card': state.staged_card, 'type': state.staged_card_type, 'position': position})
                        if position == 'before': preview_word = state.staged_card + preview_word
                        else: preview_word = preview_word + state.staged_card
                        if state.staged_card_type == 'hand': hand_card_used_this_turn = True
                        elif state.staged_card_type == 'helper': helper_card_used_this_turn = True
                        state.clear_turn_selections()
                    
                    if game_elements['action_before_btn'].is_clicked(event): apply_action('before')
                    if game_elements['action_after_btn'].is_clicked(event): apply_action('after')
                    
                    # Aksi final giliran
                    if game_elements['reset_turn_btn'].is_clicked(event): reset_turn_state()
                    if game_elements['check_turn_btn'].is_clicked(event): network.send_game_action(f"/check_turn/{state.game_id}", {"player_id": state.player_id})
                    if game_elements['submit_word_btn'].is_clicked(event):
                        network.send_game_action(f"/submit_turn/{state.game_id}", {"player_id": state.player_id, "moves": turn_moves})

        try:
            response = received_queue.get_nowait()
            if response.get("type") == "game_status":
                if response['data'].get('success'):
                    old_turn = state.game_data.get('current_turn') if state.game_data else None
                    state.update_from_server(response['data']['data'])
                    if old_turn != state.game_data.get('current_turn') and state.game_data.get('current_turn') == state.player_id:
                        reset_turn_state()
            elif response.get("type") == "action_response":
                if response['data'].get('success'):
                    state.set_popup(response['data'].get('message', 'Berhasil!'), 'success')
                else:
                    state.set_popup(response['data'].get('message', 'Gagal!'), 'error'); reset_turn_state()
            elif "game_id" in response:
                if response.get("success"): state.game_id = response['game_id']; network.start_polling(state.game_id, state.player_id); reset_turn_state()
                else: state.set_popup(response.get("message", "Gagal buat game"), 'error')
            elif response.get("message") == "Joined game successfully.":
                if response.get("success"): network.start_polling(state.game_id, state.player_id); reset_turn_state()
                else: state.set_popup(response.get("message", "Gagal gabung"), 'error')
        except queue.Empty: pass

        screen.fill((240, 240, 240))
        if state.scene == 'login': draw_login_scene(login_elements)
        elif state.scene == 'lobby': draw_lobby_scene(game_elements)
        elif state.scene in ['game', 'game_over']: draw_game_scene(game_elements)
        if state.popup_timer > 0: draw_popup(); state.popup_timer -= 1
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    network.stop_polling()

if __name__ == "__main__":
    main()