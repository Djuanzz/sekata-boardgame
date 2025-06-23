// sekata_game/static/js/main.js

import * as api from "./api.js";
import * as ui from "./ui.js";
import * as state from "./state.js";

// Ambil elemen DOM sekali di awal
const playerNameInput = document.getElementById("player-name-input");
const createGameBtn = document.getElementById("create-game-btn");
const joinGameIdInput = document.getElementById("join-game-id-input");
const joinGameBtn = document.getElementById("join-game-btn");
const startGameBtn = document.getElementById("start-game-btn");
const submitBeforeBtn = document.getElementById("submit-before-btn");
const submitAfterBtn = document.getElementById("submit-after-btn");
const checkTurnBtn = document.getElementById("check-turn-btn");
const useHelperBtn = document.getElementById("use-helper-btn");

let pollInterval = null;

// Global variables to track selections
let selectedHelperCard = null;
let selectedHelperPosition = null; // 'before' or 'after' the table card

// --- Polling Logic ---
const pollGameStatus = async () => {
  const currentGameId = state.getCurrentGameId();
  const currentPlayerId = state.getCurrentPlayerId();

  if (!currentGameId || !currentPlayerId) return;

  try {
    const data = await api.getGameStatus(currentGameId, currentPlayerId);
    if (data.success) {
      state.setGameData(data.data);
      if (data.data.winner) {
        clearInterval(pollInterval); // Hentikan polling jika ada pemenang
      }
    } else {
      state.setMessage(`Error fetching game status: ${data.message}`, "error");
      clearInterval(pollInterval);
    }
  } catch (error) {
    console.error("Network error during polling:", error);
    state.setMessage("Koneksi terputus ke server.", "error");
    clearInterval(pollInterval);
  }
};

const startPolling = () => {
  if (pollInterval) clearInterval(pollInterval);
  pollInterval = setInterval(pollGameStatus, 2000);
  pollGameStatus(); // Panggil segera setelah mulai
};

// --- Event Handlers ---
const handleCreateGame = async () => {
  state.clearMessage();
  const playerName = playerNameInput.value.trim();
  if (!playerName) {
    state.setMessage("Nama pemain tidak boleh kosong!", "error");
    return;
  }
  state.setCurrentPlayerId(playerName);

  try {
    const data = await api.createGame(playerName);
    if (data.success) {
      state.setCurrentGameId(data.game_id);
      state.setMessage(
        `Game baru dibuat dengan ID: ${data.game_id}. Anda adalah host. Tunggu pemain lain bergabung.`,
        "success"
      );
      startPolling();
    } else {
      state.setMessage(`Gagal membuat game: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error creating game:", error);
    state.setMessage(
      "Terjadi kesalahan saat membuat game. Coba lagi.",
      "error"
    );
  }
};

const handleJoinGame = async () => {
  state.clearMessage();
  const playerName = playerNameInput.value.trim();
  const gameIdToJoin = joinGameIdInput.value.trim();
  if (!playerName || !gameIdToJoin) {
    state.setMessage("Nama pemain dan ID Game tidak boleh kosong!", "error");
    return;
  }
  state.setCurrentPlayerId(playerName);

  try {
    const data = await api.joinGame(gameIdToJoin, playerName);
    if (data.success) {
      state.setCurrentGameId(gameIdToJoin);
      state.setMessage(
        `Berhasil bergabung ke game ${gameIdToJoin}.`,
        "success"
      );
      startPolling();
    } else {
      state.setMessage(`Gagal bergabung: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error joining game:", error);
    state.setMessage(
      "Terjadi kesalahan saat bergabung game. Coba lagi.",
      "error"
    );
  }
};

const handleStartGame = async () => {
  state.clearMessage();
  const currentGameId = state.getCurrentGameId();
  const currentPlayerId = state.getCurrentPlayerId();

  if (!currentGameId || !currentPlayerId) {
    state.setMessage("Anda belum di game!", "error");
    return;
  }

  try {
    const data = await api.startGame(currentGameId, currentPlayerId);
    if (data.success) {
      state.setMessage(data.message, "success");
    } else {
      state.setMessage(`Gagal memulai game: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error starting game:", error);
    state.setMessage(
      "Terjadi kesalahan saat memulai game. Coba lagi.",
      "error"
    );
  }
};

// Replace the existing handleSubmitFragment function
const handleSubmitFragment = async (position) => {
  state.clearMessage();
  const currentGameId = state.getCurrentGameId();
  const currentPlayerId = state.getCurrentPlayerId();
  const selectedCard = state.getSelectedHandCard();
  const gameData = state.getGameData();
  
  if (!currentGameId || !currentPlayerId || !selectedCard || !gameData) return;
  
  if (gameData.current_turn !== currentPlayerId) {
    state.setMessage("Bukan giliran Anda!", "error");
    return;
  }
  
  try {
    const requestData = { 
      player_id: currentPlayerId,
      fragment: selectedCard,
      position: position
    };
    
    // Add helper card data if selected (with its own position)
    if (selectedHelperCard && selectedHelperPosition) {
      requestData.helper_card = selectedHelperCard;
      requestData.helper_position = selectedHelperPosition;
    } else if (selectedHelperCard) {
      state.setMessage("Silakan pilih posisi untuk kartu helper terlebih dahulu", "error");
      return;
    }
    
    const response = await api.submitFragment(
      currentGameId,
      requestData
    );
    
    // Update the handleSubmitFragment function
    if (response.success) {
      state.setMessage(`${response.message} ${response.score_earned ? `+${response.score_earned} poin!` : ""}`, "success");
      state.setSelectedHandCard(null);
      selectedHelperCard = null;
      selectedHelperPosition = null;
      document.getElementById('remove-helper-btn').style.display = 'none';
      document.getElementById('helper-action-buttons').style.display = 'none';
      ui.resetCardSelectionUI(state.getGameData()?.card_on_table);
    } else {
      state.setMessage(response.message, "error");
    }
  } catch (error) {
    console.error("Error submitting fragment:", error);
    state.setMessage("Terjadi kesalahan saat mengirim potongan kata.", "error");
  }
};

const handleCheckTurn = async () => {
  state.clearMessage();
  const currentGameId = state.getCurrentGameId();
  const currentPlayerId = state.getCurrentPlayerId();

  if (!currentGameId || !currentPlayerId) {
    state.setMessage("Anda belum di game!", "error");
    return;
  }

  try {
    const data = await api.checkTurn(currentGameId, currentPlayerId);
    // Update the handleCheckTurn function
    if (data.success) {
      state.setMessage(data.message, "info");
      state.setSelectedHandCard(null); // Reset selected card in state
      ui.resetCardSelectionUI(state.getGameData()?.card_on_table); // Pass the table card
    } else {
      state.setMessage(`Gagal melewati giliran: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error checking turn:", error);
    state.setMessage(
      "Terjadi kesalahan saat melewati giliran. Coba lagi.",
      "error"
    );
  }
};

const handleUseHelper = async () => {
  const currentGameId = state.getCurrentGameId();
  const currentPlayerId = state.getCurrentPlayerId();
  const helperCard = state.getHelperCard();
  if (!currentGameId || !currentPlayerId || !helperCard) return;
  // Misal helper hanya bisa digunakan untuk sambung depan
  await handleSubmitFragment("before", helperCard);
};

const handleCardClick = (cardValue) => {
  state.setSelectedHandCard(cardValue);
};

// Replace the existing handleHelperCardClick function
const handleHelperCardClick = async (helperCard) => {
  const currentGameId = state.getCurrentGameId();
  const currentPlayerId = state.getCurrentPlayerId();
  const gameData = state.getGameData();
  
  if (!currentGameId || !currentPlayerId || !gameData) return;
  
  // Only allow helper card use if it's your turn
  if (gameData.current_turn !== currentPlayerId) {
    state.setMessage("Bukan giliran Anda untuk menggunakan kartu helper!", "error");
    return;
  }
  
  // Toggle selection of helper card
  if (selectedHelperCard === helperCard) {
    // Deselect the helper card
    selectedHelperCard = null;
    selectedHelperPosition = null;
    document.querySelectorAll('.helper-card-btn').forEach(btn => {
      btn.classList.remove('selected-helper');
    });
    document.getElementById('remove-helper-btn').style.display = 'none';
    document.getElementById('helper-action-buttons').style.display = 'none';
  } else {
    // Select the helper card
    selectedHelperCard = helperCard;
    
    // Update UI to show it's selected
    document.querySelectorAll('.helper-card-btn').forEach(btn => {
      btn.classList.remove('selected-helper');
      if (btn.textContent === helperCard) {
        btn.classList.add('selected-helper');
      }
    });
    
    // Show the helper controls with a more forceful style
    document.getElementById('remove-helper-btn').style.display = 'inline-block';
    document.getElementById('helper-action-buttons').style.display = 'block';
    
    // For debugging, add:
    console.log('Helper controls should be visible now');
  }
  
  // Update the word preview
  updateWordPreview();
};

// Update the updateWordPreview function

const updateWordPreview = () => {
  console.log(`Updating word preview with helper position: ${selectedHelperPosition}`);
  ui.updateWordPreview(
    state.getGameData()?.card_on_table,
    selectedHelperCard,
    selectedHelperPosition,
    state.getSelectedHandCard(),
    null
  );
};

// Add this function to handle removing helper card
const handleRemoveHelperCard = () => {
  selectedHelperCard = null;
  document.querySelectorAll('.helper-card-btn').forEach(btn => {
    btn.classList.remove('selected-helper');
  });
  document.getElementById('remove-helper-btn').style.display = 'none';
  
  // Update word preview
  updateWordPreview();
};

// Replace or update the handleHelperPlacement function

const handleHelperPlacement = (position) => {
  console.log(`Helper placement called with position: ${position}, card: ${selectedHelperCard}`);
  
  if (!selectedHelperCard) {
    console.log('No helper card selected');
    return;
  }
  
  // Set the helper position
  selectedHelperPosition = position;
  console.log(`Setting selectedHelperPosition to: ${selectedHelperPosition}`);
  
  // Update UI to show the selected position
  document.querySelectorAll('#helper-action-buttons button').forEach(btn => {
    btn.classList.remove('active-position');
  });
  
  const activeBtn = position === 'before' ? 
    document.getElementById('helper-before-btn') : 
    document.getElementById('helper-after-btn');
  
  if (activeBtn) {
    activeBtn.classList.add('active-position');
    console.log('Added active-position class to button');
  } else {
    console.log('Button not found');
  }
  
  // Update preview with the selected position
  updateWordPreview();
  
  // Inform the user to select their playing card if not already selected
  if (!state.getSelectedHandCard()) {
    state.setMessage("Sekarang pilih kartu dari tangan Anda", "info");
  }
};

// --- Subscriptions and Initial Setup ---
document.addEventListener("DOMContentLoaded", () => {
  // Subscribe UI functions to state changes
  state.subscribe("message", (msg) => ui.showMessage(msg.text, msg.type));
  state.subscribe("gameData", (gameData) => {
    const currentPlayerId = state.getCurrentPlayerId();
    const selectedHandCard = state.getSelectedHandCard();
    ui.updateGameUI(
      gameData,
      currentPlayerId,
      selectedHandCard,
      handleCardClick,
      handleHelperCardClick // handler baru untuk helper card
    );
  });
  state.subscribe("currentPlayerId", (id) => {
    // Ketika player ID berubah, mungkin perlu update UI tertentu
    // atau hanya untuk logging
  });
  state.subscribe("currentGameId", (id) => {
    // Ketika game ID berubah, mungkin perlu update UI tertentu
  });
  state.subscribe("selectedHandCard", (card) => {
    // Update preview kartu yang dipilih
    if (card) {
      document.getElementById("selected-card-preview").textContent = card;
    } else {
      document.getElementById("selected-card-preview").textContent =
        "Pilih Kartu";
    }
    // Perbarui status tombol aksi
    const gameData = state.getGameData();
    if (gameData) {
      const isMyTurn = gameData.current_turn === state.getCurrentPlayerId();
      const isGameStarted = gameData.game_started;
      ui.updateActionButtons(isMyTurn, card !== null, isGameStarted);
    } else {
      ui.updateActionButtons(false, false, false); // Disable all if no game data
    }
  });
  // Subscribe helperCard ke UI
  state.subscribe("helperCard", (helperCard) => {
    ui.renderHelperCard(helperCard);
  });

  // Add Event Listeners
  createGameBtn.addEventListener("click", handleCreateGame);
  joinGameBtn.addEventListener("click", handleJoinGame);
  startGameBtn.addEventListener("click", handleStartGame);
  submitBeforeBtn.addEventListener("click", () =>
    handleSubmitFragment("before")
  );
  submitAfterBtn.addEventListener("click", () => handleSubmitFragment("after"));
  checkTurnBtn.addEventListener("click", handleCheckTurn);

  // Helper position buttons
  const helperBeforeBtn = document.getElementById('helper-before-btn');
  const helperAfterBtn = document.getElementById('helper-after-btn');
  
  if (helperBeforeBtn) {
    helperBeforeBtn.addEventListener('click', function() {
      console.log('Helper before button clicked'); // Debugging
      handleHelperPlacement('before');
    });
  } else {
    console.error('helper-before-btn element not found');
  }
  
  if (helperAfterBtn) {
    helperAfterBtn.addEventListener('click', function() {
      console.log('Helper after button clicked'); // Debugging
      handleHelperPlacement('after');
    });
  } else {
    console.error('helper-after-btn element not found');
  }

  // Set up helper position buttons
  document.querySelectorAll('.helper-position-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      handleHelperPositionSelect(btn.dataset.position);
      
      // Update the word formation preview
      ui.updateWordPreview(
        state.getGameData()?.card_on_table,
        selectedHelperCard,
        selectedHelperPosition,
        state.getSelectedHandCard(),
        null // This will be set when they click before/after buttons
      );
    });
  });

  // Update event listeners for before/after buttons to update word preview
  submitBeforeBtn.addEventListener("click", () => {
    // Update preview with final position
    ui.updateWordPreview(
      state.getGameData()?.card_on_table,
      selectedHelperCard,
      selectedHelperPosition,
      state.getSelectedHandCard(),
      'before'
    );
    
    // Small delay to show preview before submitting
    setTimeout(() => {
      handleSubmitFragment("before");
    }, 500);
  });

  submitAfterBtn.addEventListener("click", () => {
    // Update preview with final position
    ui.updateWordPreview(
      state.getGameData()?.card_on_table,
      selectedHelperCard,
      selectedHelperPosition,
      state.getSelectedHandCard(),
      'after'
    );
    
    // Small delay to show preview before submitting
    setTimeout(() => {
      handleSubmitFragment("after");
    }, 500);
  });
  
  // Initial UI state
  ui.updateGameUI(state.getGameData()); // Sembunyikan area game sampai pemain membuat/bergabung
  ui.updateActionButtons(false, false, false); // Nonaktifkan tombol aksi awal
  
  // Add event listener for the remove helper button
  const removeHelperBtn = document.getElementById('remove-helper-btn');
  if (removeHelperBtn) {
    removeHelperBtn.addEventListener('click', handleRemoveHelperCard);
  }
});
