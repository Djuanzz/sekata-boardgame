// sekata_game/static/js/state.js

let _currentPlayerId = null;
let _currentGameId = null;
let _gameData = null; // Menampung seluruh data game dari API
let _message = { text: "", type: "" };
let _selectedHandCard = null;
let _helperCard = [];

// Objek untuk menyimpan fungsi-fungsi listener
const listeners = {
  currentPlayerId: [],
  currentGameId: [],
  gameData: [],
  message: [],
  selectedHandCard: [],
  helperCard: [],
  usedHelperCard: [],
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
  // Sinkronkan helper card jika ada
  if (data) {
    if (data.helper_cards) {
      setHelperCard(data.helper_cards);
    } else {
      setHelperCard([]);
    }

    if (data.used_helper_cards) {
      setUsedHelperCard(data.used_helper_cards);
    } else {
      setUsedHelperCard([]);
    }
  }
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

export const getHelperCard = () => _helperCard;
export const setHelperCard = (cards) => {
  _helperCard = Array.isArray(cards) ? cards : [];
  notifyListeners("helperCard", _helperCard);
};

let _usedHelperCard = [];

export const getUsedHelperCard = () => _usedHelperCard;
export const setUsedHelperCard = (cards) => {
  _usedHelperCard = Array.isArray(cards) ? cards : [];
  notifyListeners("usedHelperCard", _usedHelperCard);
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
      case "helperCard":
        callback(_helperCard);
        break;
      case "usedHelperCard":
        callback(_usedHelperCard);
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
  _helperCard = [];
  _usedHelperCard = [];
  // Notify all listeners of reset
  notifyListeners("currentPlayerId", _currentPlayerId);
  notifyListeners("currentGameId", _currentGameId);
  notifyListeners("gameData", _gameData);
  notifyListeners("message", _message);
  notifyListeners("selectedHandCard", _selectedHandCard);
  notifyListeners("helperCard", _helperCard);
  notifyListeners("usedHelperCard", _usedHelperCard);
};
