// sekata_game/static/js/ui.js

const gameArea = document.getElementById("game-area");
const gameIdDisplay = document.getElementById("game-id-display");
const hostIdDisplay = document.getElementById("host-id-display");
const currentPlayersCountSpan = document.getElementById(
  "current-players-count"
);
const minPlayersToStartSpan = document.getElementById("min-players-to-start");
const startGameBtn = document.getElementById("start-game-btn");
const currentTurnDisplay = document.getElementById("current-turn-display");
const winnerDisplay = document.getElementById("winner-display");
const winnerNameSpan = document.getElementById("winner-name");
const cardOnTableDiv = document.getElementById("card-on-table");
const playerHandDiv = document.getElementById("player-hand");
const submitBeforeBtn = document.getElementById("submit-before-btn");
const submitAfterBtn = document.getElementById("submit-after-btn");
const selectedCardPreviewDiv = document.getElementById("selected-card-preview");
const checkTurnBtn = document.getElementById("check-turn-btn");
const scoreList = document.getElementById("score-list");
const messagesDiv = document.getElementById("messages");
const connectionArea = document.getElementById("connection-area");
const helperCardValueSpan = document.getElementById("helper-card-value");
const useHelperBtn = document.getElementById("use-helper-btn");

// --- Helper UI Functions ---
export const showMessage = (msg, type = "info") => {
  messagesDiv.textContent = msg;
  messagesDiv.className = `messages ${type}`;
};

export const clearMessageUI = () => {
  messagesDiv.textContent = "";
  messagesDiv.className = "";
};

// Render kartu di tangan
export const renderPlayerHand = (handCards, onCardClick, selectedHandCard) => {
  playerHandDiv.innerHTML = "";
  if (!handCards || handCards.length === 0) {
    playerHandDiv.innerHTML = "<p>Tidak ada kartu di tangan.</p>";
    return;
  }
  handCards.forEach((cardText) => {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("card");
    if (cardText === selectedHandCard) {
      cardDiv.classList.add("selected");
    }
    cardDiv.textContent = cardText;
    cardDiv.dataset.cardValue = cardText;
    cardDiv.addEventListener("click", () => onCardClick(cardText));
    playerHandDiv.appendChild(cardDiv);
  });
};

// Render kartu di meja
export const renderCardOnTable = (cardValue) => {
  cardOnTableDiv.innerHTML = "";
  if (cardValue) {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("card", "table-card");
    cardDiv.textContent = cardValue;
    cardOnTableDiv.appendChild(cardDiv);
  } else {
    cardOnTableDiv.innerHTML = "<p>Menunggu kartu awal...</p>";
  }
};

// Render jumlah kartu pemain lain
export const renderPlayerScores = (playersData, currentPlayerId) => {
  scoreList.innerHTML = "";
  for (const pId in playersData) {
    const li = document.createElement("li");
    const player = playersData[pId];
    li.textContent = `${pId}: ${player.hand_size} kartu`;
    if (pId === currentPlayerId) {
      li.style.fontWeight = "bold";
      li.style.color = "#007bff";
    }
    scoreList.appendChild(li);
  }
};

// Render kartu helper (banyak)
export const renderHelperCard = (helperCards, usedHelperCards, onHelperClick) => {
  helperCardValueSpan.innerHTML = "";
  
  // Render available helper cards
  if (Array.isArray(helperCards) && helperCards.length > 0) {
    const availableLabel = document.createElement("div");
    availableLabel.textContent = "Available Helper Cards:";
    availableLabel.className = "helper-card-label";
    helperCardValueSpan.appendChild(availableLabel);
    
    helperCards.forEach((card) => {
      const cardBtn = document.createElement("button");
      cardBtn.textContent = card;
      cardBtn.className = "helper-card-btn";
      cardBtn.addEventListener("click", () => onHelperClick(card));
      helperCardValueSpan.appendChild(cardBtn);
    });
  }
  
  // Render used helper cards (displayed but not clickable)
  if (Array.isArray(usedHelperCards) && usedHelperCards.length > 0) {
    const usedLabel = document.createElement("div");
    usedLabel.textContent = "Used Helper Cards:";
    usedLabel.className = "helper-card-label";
    usedLabel.style.marginTop = "10px";
    helperCardValueSpan.appendChild(usedLabel);
    
    usedHelperCards.forEach((card) => {
      const usedCard = document.createElement("span");
      usedCard.textContent = card;
      usedCard.className = "helper-card-used";
      helperCardValueSpan.appendChild(usedCard);
    });
  }
  
  // If no cards at all
  if ((!helperCards || helperCards.length === 0) && 
      (!usedHelperCards || usedHelperCards.length === 0)) {
    helperCardValueSpan.textContent = "-";
  }
};

// Update status tombol aksi
export const updateActionButtons = (
  isMyTurn,
  isCardSelected,
  isGameStarted
) => {
  submitBeforeBtn.disabled = !(isMyTurn && isCardSelected && isGameStarted);
  submitAfterBtn.disabled = !(isMyTurn && isCardSelected && isGameStarted);
  checkTurnBtn.disabled = !(isMyTurn && isGameStarted);
};

// Reset seleksi kartu di UI
export const resetCardSelectionUI = () => {
  selectedCardPreviewDiv.textContent = "Pilih Kartu";
  document
    .querySelectorAll("#player-hand .card.selected")
    .forEach((c) => c.classList.remove("selected"));
  
  // Also reset helper card selection
  document.querySelectorAll('.helper-card-btn').forEach(btn => {
    btn.classList.remove('selected-helper');
  });
  
  document.getElementById('helper-position-buttons').style.display = 'none';
  
  // Reset word preview
  updateWordPreview(state.getGameData()?.card_on_table, null, null, null, null);
};

// Update tampilan game berdasarkan gameData
export const updateGameUI = (
  gameData,
  currentPlayerId,
  selectedHandCard,
  onCardClick,
  onHelperClick
) => {
  if (!gameData) {
    gameArea.style.display = "none";
    connectionArea.style.display = "flex";
    return;
  }

  gameArea.style.display = "block";
  connectionArea.style.display = "none";

  gameIdDisplay.textContent = gameData.game_id;
  hostIdDisplay.textContent = gameData.host_id;

  // Tampilkan pemenang jika ada
  if (gameData.winner) {
    winnerDisplay.style.display = "block";
    winnerNameSpan.textContent = gameData.winner;
    // Nonaktifkan semua tombol aksi setelah game berakhir
    submitBeforeBtn.disabled = true;
    submitAfterBtn.disabled = true;
    checkTurnBtn.disabled = true;
    startGameBtn.style.display = "none";
    showMessage(`Game berakhir! Pemenang: ${gameData.winner}!`, "success");
    return; // Berhenti update UI jika game sudah selesai
  } else {
    winnerDisplay.style.display = "none";
  }

  // Update UI utama
  renderCardOnTable(gameData.card_on_table);
  renderPlayerHand(
    gameData.players[currentPlayerId]?.hand || [],
    onCardClick,
    selectedHandCard
  );
  // Update helper cards with both available and used cards
  renderHelperCard(
    gameData.helper_cards,
    gameData.used_helper_cards,
    onHelperClick
  );
  currentTurnDisplay.textContent = gameData.current_turn;
  renderPlayerScores(gameData.players, currentPlayerId);

  // Tampilkan info lobi sebelum game dimulai
  if (!gameData.game_started) {
    currentPlayersCountSpan.textContent = gameData.current_players_count;
    minPlayersToStartSpan.textContent = gameData.min_players_to_start;
    document.querySelector("#game-area > p:nth-child(3)").style.display =
      "block"; // Show current players count
    // Hanya host yang bisa melihat dan menekan tombol Start
    if (
      gameData.host_id === currentPlayerId &&
      gameData.current_players_count >= gameData.min_players_to_start
    ) {
      startGameBtn.style.display = "block";
      startGameBtn.disabled = false;
    } else {
      startGameBtn.style.display = "none";
    }
  } else {
    // Sembunyikan info lobi setelah game dimulai
    startGameBtn.style.display = "none";
    document.querySelector("#game-area > p:nth-child(3)").style.display =
      "none"; // Hide current players count
  }

  const isMyTurn = gameData.current_turn === currentPlayerId;
  const isCardSelected = selectedHandCard !== null;
  const isGameStarted = gameData.game_started;
  updateActionButtons(isMyTurn, isCardSelected, isGameStarted);
};

// Add a word formation preview UI component
export const updateWordPreview = (tableCard, helperCard, helperPos, handCard, handPos) => {
  const previewDiv = document.getElementById('word-formation-preview');
  if (!previewDiv) return;
  
  previewDiv.innerHTML = '';
  
  if (!tableCard) {
    previewDiv.textContent = 'Menunggu kartu meja...';
    return;
  }
  
  // Create the table card element
  const tableCardElem = document.createElement('span');
  tableCardElem.textContent = tableCard;
  tableCardElem.className = 'preview-card table-preview';
  
  // Add helper card if selected
  const helperCardElem = helperCard ? document.createElement('span') : null;
  if (helperCardElem) {
    helperCardElem.textContent = helperCard;
    helperCardElem.className = 'preview-card helper-preview';
  }
  
  // Add playing card if selected
  const handCardElem = handCard ? document.createElement('span') : null;
  if (handCardElem) {
    handCardElem.textContent = handCard;
    handCardElem.className = 'preview-card hand-preview';
  }
  
  // Create final preview based on positioning
  if (helperCard && helperPos === 'before' && handCard && handPos === 'before') {
    previewDiv.appendChild(handCardElem);
    previewDiv.appendChild(helperCardElem);
    previewDiv.appendChild(tableCardElem);
  } else if (helperCard && helperPos === 'before' && handCard && handPos === 'after') {
    previewDiv.appendChild(helperCardElem);
    previewDiv.appendChild(tableCardElem);
    previewDiv.appendChild(handCardElem);
  } else if (helperCard && helperPos === 'after' && handCard && handPos === 'before') {
    previewDiv.appendChild(handCardElem);
    previewDiv.appendChild(tableCardElem);
    previewDiv.appendChild(helperCardElem);
  } else if (helperCard && helperPos === 'after' && handCard && handPos === 'after') {
    previewDiv.appendChild(tableCardElem);
    previewDiv.appendChild(helperCardElem);
    previewDiv.appendChild(handCardElem);
  } else if (handCard && handPos === 'before') {
    previewDiv.appendChild(handCardElem);
    previewDiv.appendChild(tableCardElem);
  } else if (handCard && handPos === 'after') {
    previewDiv.appendChild(tableCardElem);
    previewDiv.appendChild(handCardElem);
  } else if (helperCard && helperPos === 'before') {
    previewDiv.appendChild(helperCardElem);
    previewDiv.appendChild(tableCardElem);
  } else if (helperCard && helperPos === 'after') {
    previewDiv.appendChild(tableCardElem);
    previewDiv.appendChild(helperCardElem);
  } else {
    previewDiv.appendChild(tableCardElem);
  }
};
