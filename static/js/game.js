// sekata_game/static/js/game.js
const playerNameInput = document.getElementById("player-name-input");
const createGameBtn = document.getElementById("create-game-btn");
const joinGameIdInput = document.getElementById("join-game-id-input");
const joinGameBtn = document.getElementById("join-game-btn");

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

let currentPlayerId = null;
let currentGameId = null;
let pollInterval = null;
let selectedHandCard = null; // Kartu dari tangan yang sedang dipilih

// --- Helper Functions ---
function showMessage(msg, type = "info") {
  messagesDiv.textContent = msg;
  messagesDiv.className = `messages ${type}`;
}

function clearMessage() {
  messagesDiv.textContent = "";
  messagesDiv.className = "";
}

// Render kartu di tangan
function renderPlayerHand(handCards) {
  playerHandDiv.innerHTML = "";
  if (handCards.length === 0) {
    playerHandDiv.innerHTML = "<p>Tidak ada kartu di tangan.</p>";
    // Jika tangan kosong, ini mungkin berarti pemain menang
    return;
  }
  handCards.forEach((cardText) => {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("card");
    cardDiv.textContent = cardText;
    cardDiv.dataset.cardValue = cardText; // Untuk menyimpan nilai kartu
    cardDiv.addEventListener("click", () => {
      // Hapus seleksi dari kartu lain
      document
        .querySelectorAll("#player-hand .card.selected")
        .forEach((c) => c.classList.remove("selected"));
      cardDiv.classList.add("selected");
      selectedHandCard = cardText;
      selectedCardPreviewDiv.textContent = cardText; // Tampilkan di preview
      updateActionButtons();
    });
    playerHandDiv.appendChild(cardDiv);
  });
}

// Render kartu di meja
function renderCardOnTable(cardValue) {
  cardOnTableDiv.innerHTML = "";
  if (cardValue) {
    const cardDiv = document.createElement("div");
    cardDiv.classList.add("card", "table-card"); // Tambah kelas khusus untuk kartu meja
    cardDiv.textContent = cardValue;
    cardOnTableDiv.appendChild(cardDiv);
  } else {
    cardOnTableDiv.innerHTML = "<p>Menunggu kartu awal...</p>";
  }
}

// Render jumlah kartu pemain lain
function renderPlayerScores(playersData, currentPlayerId) {
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
}

// Update status tombol aksi
function updateActionButtons() {
  const isMyTurn = currentTurnDisplay.textContent === currentPlayerId;
  const isCardSelected = selectedHandCard !== null;
  const isGameStarted = startGameBtn.style.display === "none"; // Indikator game dimulai

  submitBeforeBtn.disabled = !(isMyTurn && isCardSelected && isGameStarted);
  submitAfterBtn.disabled = !(isMyTurn && isCardSelected && isGameStarted);
  checkTurnBtn.disabled = !(isMyTurn && isGameStarted);
}

// Reset seleksi kartu dan tombol
function resetActionState() {
  selectedHandCard = null;
  selectedCardPreviewDiv.textContent = "Pilih Kartu";
  document
    .querySelectorAll("#player-hand .card.selected")
    .forEach((c) => c.classList.remove("selected"));
  updateActionButtons();
}

// Polling status game
async function pollGameStatus() {
  if (!currentGameId || !currentPlayerId) return;

  try {
    const response = await fetch(
      `/game_status/${currentGameId}?player_id=${currentPlayerId}`
    );
    const data = await response.json();

    if (data.success) {
      const gameData = data.data;

      // Tampilkan pemenang jika ada
      if (gameData.winner) {
        winnerDisplay.style.display = "block";
        winnerNameSpan.textContent = gameData.winner;
        clearInterval(pollInterval); // Hentikan polling
        // Nonaktifkan semua tombol aksi setelah game berakhir
        submitBeforeBtn.disabled = true;
        submitAfterBtn.disabled = true;
        checkTurnBtn.disabled = true;
        startGameBtn.style.display = "none";
        showMessage(`Game berakhir! Pemenang: ${gameData.winner}!`, "success");
        return;
      } else {
        winnerDisplay.style.display = "none";
      }

      // Update UI utama
      renderCardOnTable(gameData.card_on_table);
      renderPlayerHand(gameData.players[currentPlayerId].hand || []);
      currentTurnDisplay.textContent = gameData.current_turn;
      renderPlayerScores(gameData.players, currentPlayerId);

      // Tampilkan info lobi sebelum game dimulai
      if (!gameData.game_started) {
        currentPlayersCountSpan.textContent = gameData.current_players_count;
        minPlayersToStartSpan.textContent = gameData.min_players_to_start;
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

      updateActionButtons(); // Perbarui status tombol setelah data baru
    } else {
      showMessage(`Error fetching game status: ${data.message}`, "error");
      clearInterval(pollInterval);
    }
  } catch (error) {
    console.error("Network error during polling:", error);
    showMessage("Koneksi terputus ke server.", "error");
    clearInterval(pollInterval);
  }
}

// --- Event Listeners ---

// Tombol "Buat Game Baru"
createGameBtn.addEventListener("click", async () => {
  clearMessage();
  const playerName = playerNameInput.value.trim();
  if (!playerName) {
    showMessage("Nama pemain tidak boleh kosong!", "error");
    return;
  }
  currentPlayerId = playerName;

  try {
    const response = await fetch("/create_game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: currentPlayerId }),
    });
    const data = await response.json();

    if (data.success) {
      currentGameId = data.game_id;
      gameIdDisplay.textContent = currentGameId;
      hostIdDisplay.textContent = currentPlayerId; // Host adalah yang membuat game
      gameArea.style.display = "block";
      document.getElementById("connection-area").style.display = "none";
      showMessage(
        `Game baru dibuat dengan ID: ${currentGameId}. Anda adalah host. Tunggu pemain lain bergabung.`,
        "success"
      );

      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(pollGameStatus, 2000);
      pollGameStatus();
    } else {
      showMessage(`Gagal membuat game: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error creating game:", error);
    showMessage("Terjadi kesalahan saat membuat game. Coba lagi.", "error");
  }
});

// Tombol "Gabung Game"
joinGameBtn.addEventListener("click", async () => {
  clearMessage();
  const playerName = playerNameInput.value.trim();
  const gameIdToJoin = joinGameIdInput.value.trim();
  if (!playerName || !gameIdToJoin) {
    showMessage("Nama pemain dan ID Game tidak boleh kosong!", "error");
    return;
  }
  currentPlayerId = playerName;

  try {
    const response = await fetch(`/join_game/${gameIdToJoin}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: currentPlayerId }),
    });
    const data = await response.json();

    if (data.success) {
      currentGameId = gameIdToJoin;
      gameIdDisplay.textContent = currentGameId;
      // Host ID akan diisi saat pollGameStatus
      gameArea.style.display = "block";
      document.getElementById("connection-area").style.display = "none";
      showMessage(`Berhasil bergabung ke game ${currentGameId}.`, "success");

      if (pollInterval) clearInterval(pollInterval);
      pollInterval = setInterval(pollGameStatus, 2000);
      pollGameStatus();
    } else {
      showMessage(`Gagal bergabung: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error joining game:", error);
    showMessage("Terjadi kesalahan saat bergabung game. Coba lagi.", "error");
  }
});

// Tombol "Mulai Game" (hanya untuk Host)
startGameBtn.addEventListener("click", async () => {
  clearMessage();
  if (!currentGameId || !currentPlayerId) {
    showMessage("Anda belum di game!", "error");
    return;
  }

  try {
    const response = await fetch(`/start_game/${currentGameId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: currentPlayerId }),
    });
    const data = await response.json();

    if (data.success) {
      showMessage(data.message, "success");
      startGameBtn.style.display = "none"; // Sembunyikan tombol setelah mulai
    } else {
      showMessage(`Gagal memulai game: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error starting game:", error);
    showMessage("Terjadi kesalahan saat memulai game. Coba lagi.", "error");
  }
});

// Tombol "Sambung Depan"
submitBeforeBtn.addEventListener("click", async () => {
  clearMessage();
  if (!selectedHandCard) {
    showMessage("Pilih kartu dari tangan Anda terlebih dahulu.", "error");
    return;
  }
  await submitFragment(selectedHandCard, "before");
});

// Tombol "Sambung Belakang"
submitAfterBtn.addEventListener("click", async () => {
  clearMessage();
  if (!selectedHandCard) {
    showMessage("Pilih kartu dari tangan Anda terlebih dahulu.", "error");
    return;
  }
  await submitFragment(selectedHandCard, "after");
});

async function submitFragment(fragment, position) {
  if (!currentGameId || !currentPlayerId) {
    showMessage("Anda belum di game!", "error");
    return;
  }

  try {
    const response = await fetch(`/submit_fragment/${currentGameId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        player_id: currentPlayerId,
        fragment: fragment,
        position: position,
      }),
    });
    const data = await response.json();

    if (data.success) {
      showMessage(data.message, "success");
      resetActionState(); // Reset seleksi setelah submit
    } else {
      showMessage(`Gagal menyambung kata: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error submitting fragment:", error);
    showMessage("Terjadi kesalahan saat menyambung kata. Coba lagi.", "error");
  }
}

// Tombol "Check (Lewati Giliran)"
checkTurnBtn.addEventListener("click", async () => {
  clearMessage();
  if (!currentGameId || !currentPlayerId) {
    showMessage("Anda belum di game!", "error");
    return;
  }

  try {
    const response = await fetch(`/check_turn/${currentGameId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_id: currentPlayerId }),
    });
    const data = await response.json();

    if (data.success) {
      showMessage(data.message, "info");
      resetActionState(); // Reset seleksi setelah check
    } else {
      showMessage(`Gagal melewati giliran: ${data.message}`, "error");
    }
  } catch (error) {
    console.error("Error checking turn:", error);
    showMessage("Terjadi kesalahan saat melewati giliran. Coba lagi.", "error");
  }
});

// Sembunyikan area game sampai pemain membuat/bergabung saat startup
gameArea.style.display = "none";

// Inisialisasi awal tombol aksi
updateActionButtons();
