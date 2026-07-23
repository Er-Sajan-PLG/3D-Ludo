import Head from 'next/head'
import Layout from '../components/Layout'

export default function Auth() {
  return (
    <Layout>
      <Head>
        <title>Authentication — 3D Ludo</title>
      </Head>
      <h2>Authentication Module</h2>
      <p>Login, registration, and provider auth flow.</p>
    </Layout>
  )
}
