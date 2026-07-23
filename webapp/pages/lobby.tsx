import Head from 'next/head'
import Layout from '../components/Layout'

export default function Lobby() {
  return (
    <Layout>
      <Head>
        <title>Lobby — 3D Ludo</title>
      </Head>
      <h2>Lobby Module</h2>
      <p>Matchmaking, rooms, and multiplayer lobby.</p>
    </Layout>
  )
}
