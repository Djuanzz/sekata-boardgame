// sekata_game/static/js/api.js

// const BASE_URL = "http://localhost:8000";
// Adjust if the server runs on a different port

export const createGame = async (playerId) => {
  const response = await fetch(`/create_game`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

export const joinGame = async (gameId, playerId) => {
  const response = await fetch(`/join_game/${gameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

export const startGame = async (gameId, playerId) => {
  const response = await fetch(`/start_game/${gameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

export const getGameStatus = async (gameId, playerId) => {
  const response = await fetch(
    `/game_status/${gameId}?player_id=${playerId}`
  );
  return response.json();
};

export const submitFragment = async (gameId, playerId, fragment, position) => {
  const response = await fetch(`/submit_fragment/${gameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId, fragment, position }),
  });
  return response.json();
};

export const checkTurn = async (gameId, playerId) => {
  const response = await fetch(`/check_turn/${gameId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};
