import Head from 'next/head'
import Layout from '../components/Layout'
import { useEffect, useState } from 'react'

type GameState = {
  status: string
  currentPlayer: string
  lastRoll?: number
  message?: string
}

export default function GamePage() {
  const [gameState, setGameState] = useState<GameState | null>(null)
  const [loading, setLoading] = useState(false)

  async function fetchGameState() {
    setLoading(true)
    const res = await fetch('/api/game')
    const data: GameState = await res.json()
    setGameState(data)
    setLoading(false)
  }

  async function playTurn() {
    setLoading(true)
    const res = await fetch('/api/game', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'play_turn' })
    })
    const data: GameState = await res.json()
    setGameState(data)
    setLoading(false)
  }

  useEffect(() => {
    fetchGameState()
  }, [])

  return (
    <Layout>
      <Head>
        <title>Play Game — 3D Ludo</title>
      </Head>
      <h2>Play Game</h2>
      <p>Use the backend API to advance the game state.</p>
      <div className="card">
        <button onClick={playTurn} disabled={loading}>
          {loading ? 'Processing...' : 'Roll / Play Turn'}
        </button>
      </div>
      {gameState ? (
        <div className="card">
          <p><strong>Status:</strong> {gameState.status}</p>
          <p><strong>Current Player:</strong> {gameState.currentPlayer}</p>
          {gameState.lastRoll !== undefined && <p><strong>Last Roll:</strong> {gameState.lastRoll}</p>}
          {gameState.message && <p><strong>Message:</strong> {gameState.message}</p>}
        </div>
      ) : (
        <p>Loading game state...</p>
      )}
    </Layout>
  )
}
