import type { Metadata } from 'next'
import { ClientProviders } from '@/components/ClientProviders'
import { OnboardingProvider } from '@/components/onboarding'
import './globals.css'

export const metadata: Metadata = {
  title: 'Hopium Lab - Token CT Simulation',
  description: 'Simulate how your token performs on Crypto Twitter before launch. AI personas predict viral spread, sentiment & FUD.',
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <ClientProviders>
          <OnboardingProvider>
            {children}
          </OnboardingProvider>
        </ClientProviders>
      </body>
    </html>
  )
}
