import Link from 'next/link'
import { ReactNode } from 'react'

const navItems = [
  { href: '/', label: 'Home' },
  { href: '/game', label: 'Play Game' },
  { href: '/ui', label: 'UI' },
  { href: '/auth', label: 'Auth' },
  { href: '/store', label: 'Store' },
  { href: '/lobby', label: 'Lobby' },
  { href: '/friends', label: 'Friends' },
  { href: '/inventory', label: 'Inventory' },
  { href: '/settings', label: 'Settings' },
  { href: '/engine', label: '3D Engine' }
]

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="container">
      <header>
        <h1>3D Ludo</h1>
        <nav>
          {navItems.map(item => (
            <Link key={item.href} href={item.href} className="navLink">
              {item.label}
            </Link>
          ))}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  )
}
