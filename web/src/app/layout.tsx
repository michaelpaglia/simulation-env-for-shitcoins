import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Hopium Lab',
  description: 'Synthesize fictional shitcoins and simulate CT reactions',
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
