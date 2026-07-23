import Link from 'next/link'
import Head from 'next/head'
import Layout from '../components/Layout'

const sections = [
  { href: '/game', title: 'Play Game' },
  { href: '/ui', title: 'UI' },
  { href: '/auth', title: 'Authentication' },
  { href: '/store', title: 'Store' },
  { href: '/lobby', title: 'Lobby' },
  { href: '/friends', title: 'Friends' },
  { href: '/inventory', title: 'Inventory' },
  { href: '/settings', title: 'Settings' },
  { href: '/engine', title: '3D Engine' }
]

export default function Home() {
  return (
    <Layout>
      <Head>
        <title>3D Ludo Web</title>
      </Head>
      <section>
        <h1>3D Ludo Web App</h1>
        <p>Next.js scaffold for the 3D Ludo frontend.</p>
        <div className="grid">
          {sections.map(section => (
            <Link key={section.href} href={section.href} className="card">
              <h2>{section.title}</h2>
            </Link>
          ))}
        </div>
      </section>
    </Layout>
  )
}
