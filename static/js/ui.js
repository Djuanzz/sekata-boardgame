// static/js/ui.js (Diperbaiki dengan Logika Lobi)
import * as state from './state.js';

// Cache elemen DOM
const getElem = (id) => document.getElementById(id);
const gameArea = getElem('game-area');
const connectionArea = getElem('connection-area');
const gameIdDisplay = getElem('game-id-display');
const currentTurnDisplay = getElem('current-turn-display');
const scoreList = getElem('score-list');
const lobbyArea = getElem('lobby-area');
const boardArea = getElem('board-area');
const lobbyPlayerList = getElem('lobby-player-list');
const startGameBtn = getElem('start-game-btn');
const wordPreviewDisplay = getElem('word-preview-display');
const stagedCardDisplay = getElem('staged-card-display');
const actionBeforeBtn = getElem('action-before-btn');
const actionAfterBtn = getElem('action-after-btn');
const helperCardsContainer = getElem('helper-cards-container');
const playerHandContainer = getElem('player-hand-container');
const submitWordBtn = getElem('submit-word-btn');
const resetTurnBtn = getElem('reset-turn-btn');
const checkTurnBtn = getElem('check-turn-btn');
const winnerDisplay = getElem('winner-display');
const winnerName = getElem('winner-name');
const popupOverlay = getElem('popup-overlay');
const popupMessage = getElem('popup-message');

function createCardElement(text, type, onClick) {
  const card = document.createElement('div');
  card.className = 'card';
  card.dataset.type = type;
  card.dataset.value = text;
  card.textContent = text;
  card.addEventListener('click', () => onClick(text, type));
  return card;
}

export function showPopup(message, type = 'info', duration = 2000) {
  popupMessage.textContent = message;
  popupMessage.className = type;
  popupOverlay.classList.remove('hidden');
  setTimeout(() => { popupOverlay.classList.add('hidden'); }, duration);
}

export function updateWordPreview(previewWord) {
  wordPreviewDisplay.textContent = previewWord;
}

export function updateStagedCard(stagedCard) {
  if (stagedCard) {
    stagedCardDisplay.textContent = stagedCard;
    stagedCardDisplay.classList.add('active');
  } else {
    stagedCardDisplay.textContent = 'Pilih Kartu';
    stagedCardDisplay.classList.remove('active');
  }
}

/**
 * Fungsi utama untuk merender seluruh UI game.
 */
export function updateGameUI(gameData, turnState, cardClickHandler) {
  if (!gameData || !state.getCurrentGameId()) {
    gameArea.classList.add('hidden');
    connectionArea.classList.remove('hidden');
    return;
  }
  
  gameArea.classList.remove('hidden');
  connectionArea.classList.add('hidden');

  const playerId = state.getCurrentPlayerId();
  const isMyTurn = gameData.current_turn === playerId;

  // Info Atas (Selalu tampil)
  gameIdDisplay.textContent = gameData.game_id;
  
  // Periksa apakah game sudah dimulai untuk menampilkan UI yang sesuai
  if (gameData.game_started) {
    // TAMPILKAN PAPAN PERMAINAN
    lobbyArea.classList.add('hidden');
    boardArea.classList.remove('hidden');

    currentTurnDisplay.textContent = `Giliran: ${gameData.current_turn || '-'}`;

    // Render kartu helper
    helperCardsContainer.innerHTML = '';
    gameData.helper_cards.forEach(cardText => {
      const card = createCardElement(cardText, 'helper', cardClickHandler);
      if (turnState.helperCardUsedThisTurn) card.classList.add('disabled');
      helperCardsContainer.appendChild(card);
    });

    // Render kartu tangan
    playerHandContainer.innerHTML = '';
    const myHand = gameData.players[playerId]?.hand || [];
    myHand.forEach(cardText => {
      const card = createCardElement(cardText, 'hand', cardClickHandler);
      if (turnState.handCardUsedThisTurn) card.classList.add('disabled');
      playerHandContainer.appendChild(card);
    });
    
    const { stagedCard } = state.getStagedCard();
    document.querySelectorAll('.card.selected').forEach(c => c.classList.remove('selected'));
    if (stagedCard) {
      const selectedCardElem = document.querySelector(`.card[data-value="${stagedCard}"]`);
      if (selectedCardElem) selectedCardElem.classList.add('selected');
    }
    
    actionBeforeBtn.disabled = !isMyTurn || !stagedCard;
    actionAfterBtn.disabled = !isMyTurn || !stagedCard;

    submitWordBtn.disabled = !isMyTurn || !turnState.handCardUsedThisTurn;
    resetTurnBtn.disabled = !isMyTurn || turnState.turnMoves.length === 0;
    checkTurnBtn.disabled = !isMyTurn || turnState.turnMoves.length > 0;
    
  } else {
    // TAMPILKAN LOBI
    lobbyArea.classList.remove('hidden');
    boardArea.classList.add('hidden');

    currentTurnDisplay.textContent = 'Menunggu Permainan Dimulai';

    // Render daftar pemain di lobi
    lobbyPlayerList.innerHTML = '';
    Object.keys(gameData.players).forEach(pId => {
      const li = document.createElement('li');
      li.textContent = `${pId} ${pId === gameData.host_id ? '(Host)' : ''}`;
      lobbyPlayerList.appendChild(li);
    });
    
    // Tampilkan tombol Start untuk host jika kondisi terpenuhi
    if (playerId === gameData.host_id && gameData.current_players_count >= gameData.min_players_to_start) {
        startGameBtn.classList.remove('hidden');
    } else {
        startGameBtn.classList.add('hidden');
    }
  }

  // Info Pemain/Skor (Selalu tampil)
  scoreList.innerHTML = '';
  Object.entries(gameData.players).forEach(([id, data]) => {
    const li = document.createElement('li');
    li.textContent = `${id}: ${data.hand_size} kartu`;
    if (id === playerId) li.style.fontWeight = 'bold';
    scoreList.appendChild(li);
  });

  // Handle Pemenang
  if (gameData.winner) {
    winnerDisplay.classList.remove('hidden');
    winnerName.textContent = gameData.winner;
    boardArea.classList.add('hidden'); // Sembunyikan board saat ada pemenang
    lobbyArea.classList.add('hidden');
  } else {
    winnerDisplay.classList.add('hidden');
  }
}