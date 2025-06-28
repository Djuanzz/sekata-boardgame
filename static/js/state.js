// static/js/state.js (Diperbarui)
let _currentPlayerId = null;
let _currentGameId = null;
let _gameData = null;
let _message = { text: "", type: "" };

// State baru untuk UI
let _stagedCard = null;
let _stagedCardType = null;

const listeners = {
  gameData: [], message: [], stagedCard: [],
};

function notifyListeners(stateName, value) {
  listeners[stateName]?.forEach((callback) => callback(value));
}

// Getters
export const getCurrentPlayerId = () => _currentPlayerId;
export const getCurrentGameId = () => _currentGameId;
export const getGameData = () => _gameData;
export const getStagedCard = () => ({ stagedCard: _stagedCard, stagedCardType: _stagedCardType });

// Setters
export const setCurrentPlayerId = (id) => { _currentPlayerId = id; };
export const setCurrentGameId = (id) => { _currentGameId = id; };
export const setGameData = (data) => {
  _gameData = data;
  notifyListeners("gameData", _gameData);
};
export const setMessage = (text, type = "info") => {
  _message = { text, type };
  notifyListeners("message", _message);
};
export const setStagedCard = (card, type) => {
  _stagedCard = card;
  _stagedCardType = type;
  notifyListeners("stagedCard", { stagedCard: _stagedCard, stagedCardType: _stagedCardType });
};

// Subscribe
export const subscribe = (stateName, callback) => {
  if (listeners[stateName]) {
    listeners[stateName].push(callback);
  }
};