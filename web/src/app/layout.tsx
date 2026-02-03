import type { Metadata } from 'next'
import { ClientProviders } from '@/components/ClientProviders'
import { OnboardingProvider } from '@/components/onboarding'
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
