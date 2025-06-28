// static/js/main.js (Sedikit Penyesuaian)
import * as api from "./api.js";
import * as ui from "./ui.js";
import * as state from "./state.js";

// --- State Lokal untuk Giliran ---
let turnState = {
  turnMoves: [],
  previewWord: "",
  handCardUsedThisTurn: false,
  helperCardUsedThisTurn: false,
};

function resetTurnState() {
  const gameData = state.getGameData();
  turnState.turnMoves = [];
  turnState.previewWord = gameData ? gameData.card_on_table : "";
  turnState.handCardUsedThisTurn = false;
  turnState.helperCardUsedThisTurn = false;
  state.setStagedCard(null, null);
  ui.updateWordPreview(turnState.previewWord);
  ui.updateGameUI(gameData, turnState, handleCardClick);
}

// --- Logika Polling ---
let pollInterval = null;
const startPolling = () => {
  if (pollInterval) clearInterval(pollInterval);
  const poll = async () => {
    const gameId = state.getCurrentGameId();
    const playerId = state.getCurrentPlayerId();
    if (!gameId || !playerId) return;

    const response = await api.getGameStatus(gameId, playerId);
    if (response.success) {
      const oldTurn = state.getGameData()?.current_turn;
      state.setGameData(response.data);
      const newTurn = response.data.current_turn;

      if (oldTurn !== newTurn && newTurn === playerId) {
        resetTurnState();
      } else {
        if (newTurn !== playerId || !turnState.previewWord) {
          turnState.previewWord = response.data.card_on_table;
          ui.updateWordPreview(turnState.previewWord);
        }
      }
      
      ui.updateGameUI(response.data, turnState, handleCardClick);
      if (response.data.winner) clearInterval(pollInterval);
    } else {
      console.error("Polling failed:", response.message);
      clearInterval(pollInterval);
    }
  };
  pollInterval = setInterval(poll, 2000);
  poll();
};

// --- Event Handlers ---
function handleCardClick(cardValue, cardType) {
  const gameData = state.getGameData();
  if (!gameData || gameData.current_turn !== state.getCurrentPlayerId()) return;
  if (cardType === 'hand' && turnState.handCardUsedThisTurn) return;
  if (cardType === 'helper' && turnState.helperCardUsedThisTurn) return;
  
  const { stagedCard } = state.getStagedCard();
  if (stagedCard === cardValue) {
    state.setStagedCard(null, null);
  } else {
    state.setStagedCard(cardValue, cardType);
  }
}

function handleActionClick(position) {
    const { stagedCard, stagedCardType } = state.getStagedCard();
    if (!stagedCard) return;

    turnState.turnMoves.push({ card: stagedCard, type: stagedCardType, position: position });
    if (position === 'before') turnState.previewWord = stagedCard + turnState.previewWord;
    else turnState.previewWord = turnState.previewWord + stagedCard;

    if (stagedCardType === 'hand') turnState.handCardUsedThisTurn = true;
    if (stagedCardType === 'helper') turnState.helperCardUsedThisTurn = true;
    
    state.setStagedCard(null, null);
    ui.updateWordPreview(turnState.previewWord);
    ui.updateGameUI(state.getGameData(), turnState, handleCardClick);
}

async function handleSubmitWord() {
    const response = await api.submitTurn(state.getCurrentGameId(), state.getCurrentPlayerId(), turnState.turnMoves);
    if (response.success) {
        ui.showPopup(response.message, 'success');
    } else {
        ui.showPopup(response.message, 'error');
        resetTurnState();
    }
}

async function handleCheck() {
  const response = await api.checkTurn(state.getCurrentGameId(), state.getCurrentPlayerId());
  ui.showPopup(response.message, response.success ? 'info' : 'error');
}

// --- Inisialisasi Aplikasi ---
document.addEventListener("DOMContentLoaded", () => {
  const getElem = (id) => document.getElementById(id);
  
  // Listener koneksi
  getElem('create-game-btn').addEventListener('click', async () => {
    const playerId = getElem('player-name-input').value.trim();
    if (!playerId) { ui.showPopup('Nama tidak boleh kosong!', 'error'); return; }
    state.setCurrentPlayerId(playerId);
    const response = await api.createGame(playerId);
    if (response.success) {
      state.setCurrentGameId(response.game_id);
      startPolling();
    } else { ui.showPopup(response.message, 'error'); }
  });

  getElem('join-game-btn').addEventListener('click', async () => {
    const playerId = getElem('player-name-input').value.trim();
    const gameId = getElem('join-game-id-input').value.trim();
    if (!playerId || !gameId) { ui.showPopup('Nama dan ID Game tidak boleh kosong!', 'error'); return; }
    state.setCurrentPlayerId(playerId);
    state.setCurrentGameId(gameId);
    const response = await api.joinGame(gameId, playerId);
    if (response.success) {
      startPolling();
    } else { ui.showPopup(response.message, 'error'); }
  });
  
  // VVVV TAMBAHKAN LISTENER INI KEMBALI VVVV
  getElem('start-game-btn').addEventListener('click', async () => {
    const response = await api.startGame(state.getCurrentGameId(), state.getCurrentPlayerId());
    if (!response.success) ui.showPopup(response.message, 'error');
    // Polling akan menangani update UI secara otomatis
  });

  // Listener aksi utama
  getElem('action-before-btn').addEventListener('click', () => handleActionClick('before'));
  getElem('action-after-btn').addEventListener('click', () => handleActionClick('after'));

  // Listener aksi final
  getElem('submit-word-btn').addEventListener('click', handleSubmitWord);
  getElem('reset-turn-btn').addEventListener('click', resetTurnState);
  getElem('check-turn-btn').addEventListener('click', handleCheck);

  // Subscribe UI ke perubahan state
  state.subscribe('stagedCard', ({ stagedCard }) => {
    ui.updateStagedCard(stagedCard);
  });
});