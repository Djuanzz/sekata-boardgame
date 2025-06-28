// static/js/api.js (Diperbarui)
export const createGame = async (playerId) => {
  const response = await fetch('/create_game', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

export const joinGame = async (gameId, playerId) => {
  const response = await fetch(`/join_game/${gameId}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

export const startGame = async (gameId, playerId) => {
  const response = await fetch(`/start_game/${gameId}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

export const getGameStatus = async (gameId, playerId) => {
  const response = await fetch(`/game_status/${gameId}?player_id=${playerId}`);
  return response.json();
};

export const checkTurn = async (gameId, playerId) => {
  const response = await fetch(`/check_turn/${gameId}`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId }),
  });
  return response.json();
};

// ENDPOINT BARU
export const submitTurn = async (gameId, playerId, moves) => {
  const response = await fetch(`/submit_turn/${gameId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ player_id: playerId, moves: moves }),
  });
  return response.json();
};