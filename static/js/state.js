// sekata_game/static/js/state.js

let _currentPlayerId = null;
let _currentGameId = null;
let _gameData = null; // Menampung seluruh data game dari API
let _message = { text: "", type: "" };
let _selectedHandCard = null;

// Objek untuk menyimpan fungsi-fungsi listener
const listeners = {
  currentPlayerId: [],
  currentGameId: [],
  gameData: [],
  message: [],
  selectedHandCard: [],
};

// Fungsi untuk memberi tahu listener tentang perubahan state
function notifyListeners(stateName, value) {
  listeners[stateName].forEach((callback) => callback(value));
}

// Getter dan Setter untuk state
export const getCurrentPlayerId = () => _currentPlayerId;
export const setCurrentPlayerId = (id) => {
  _currentPlayerId = id;
  notifyListeners("currentPlayerId", _currentPlayerId);
};

export const getCurrentGameId = () => _currentGameId;
export const setCurrentGameId = (id) => {
  _currentGameId = id;
  notifyListeners("currentGameId", _currentGameId);
};

export const getGameData = () => _gameData;
export const setGameData = (data) => {
  _gameData = data;
  notifyListeners("gameData", _gameData);
};

export const getMessage = () => _message;
export const setMessage = (text, type = "info") => {
  _message = { text, type };
  notifyListeners("message", _message);
};
export const clearMessage = () => {
  _message = { text: "", type: "" };
  notifyListeners("message", _message);
};

export const getSelectedHandCard = () => _selectedHandCard;
export const setSelectedHandCard = (card) => {
  _selectedHandCard = card;
  notifyListeners("selectedHandCard", _selectedHandCard);
};

// Fungsi untuk mendaftar listener
export const subscribe = (stateName, callback) => {
  if (listeners[stateName]) {
    listeners[stateName].push(callback);
    // Panggil callback segera dengan nilai state saat ini
    switch (stateName) {
      case "currentPlayerId":
        callback(_currentPlayerId);
        break;
      case "currentGameId":
        callback(_currentGameId);
        break;
      case "gameData":
        callback(_gameData);
        break;
      case "message":
        callback(_message);
        break;
      case "selectedHandCard":
        callback(_selectedHandCard);
        break;
    }
  } else {
    console.warn(`State '${stateName}' tidak memiliki listener.`);
  }
};

// Fungsi untuk membatalkan pendaftaran listener (opsional, untuk cleanup)
export const unsubscribe = (stateName, callback) => {
  if (listeners[stateName]) {
    listeners[stateName] = listeners[stateName].filter((cb) => cb !== callback);
  }
};

// Fungsi untuk mereset semua state (misalnya, saat keluar game)
export const resetAllState = () => {
  _currentPlayerId = null;
  _currentGameId = null;
  _gameData = null;
  _message = { text: "", type: "" };
  _selectedHandCard = null;
  // Notify all listeners of reset
  notifyListeners("currentPlayerId", _currentPlayerId);
  notifyListeners("currentGameId", _currentGameId);
  notifyListeners("gameData", _gameData);
  notifyListeners("message", _message);
  notifyListeners("selectedHandCard", _selectedHandCard);
};
