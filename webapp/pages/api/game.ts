import type { NextApiRequest, NextApiResponse } from 'next'

let gameState = {
  status: 'waiting',
  currentPlayer: 'Player 1',
  lastRoll: null,
  message: 'Game has not started yet.',
  turn: 0
}

function getState() {
  return {
    status: gameState.status,
    currentPlayer: gameState.currentPlayer,
    lastRoll: gameState.lastRoll,
    message: gameState.message
  }
}

function startGame() {
  gameState = {
    status: 'playing',
    currentPlayer: 'Player 1',
    lastRoll: null,
    message: 'Game started. Roll the dice to begin.',
    turn: 1
  }
}

function nextTurn() {
  const currentPlayerId = parseInt(gameState.currentPlayer.split(' ')[1] || '1', 10)
  const nextPlayer = `Player ${currentPlayerId % 4 + 1}`
  const roll = Math.floor(Math.random() * 6) + 1

  gameState = {
    ...gameState,
    status: 'playing',
    currentPlayer: nextPlayer,
    lastRoll: roll,
    message: `Rolled a ${roll}. It is now ${nextPlayer}'s turn.`,
    turn: gameState.turn + 1
  }
}

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const proxyUrl = `${BACKEND_URL}/api/game`

  if (req.method === 'GET') {
    const response = await fetch(proxyUrl)
    const data = await response.json()
    return res.status(response.status).json(data)
  }

  if (req.method === 'POST') {
    const response = await fetch(proxyUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(req.body)
    })
    const data = await response.json()
    return res.status(response.status).json(data)
  }

  res.setHeader('Allow', ['GET', 'POST'])
  res.status(405).end(`Method ${req.method} Not Allowed`)
}
