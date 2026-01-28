import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Shitcoin Simulator',
  description: 'Simulate how your token performs on CT before launch',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
