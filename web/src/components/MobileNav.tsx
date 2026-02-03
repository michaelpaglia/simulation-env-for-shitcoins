'use client'

import { useState, useCallback, ReactNode } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useWalletModal } from '@solana/wallet-adapter-react-ui'
import { HomeIcon, LabIcon } from './icons'
import styles from './MobileNav.module.css'

const WalletIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M21 18v1c0 1.1-.9 2-2 2H5c-1.11 0-2-.9-2-2V5c0-1.1.89-2 2-2h14c1.1 0 2 .9 2 2v1h-9c-1.11 0-2 .9-2 2v8c0 1.1.89 2 2 2h9zm-9-2h10V8H12v8zm4-2.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z" />
  </svg>
)

const ConfigIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M12 8c-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4-1.79-4-4-4zm0 6c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm8.94-3.03c.02-.16.06-.33.06-.5s-.04-.34-.06-.5l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.27-.18-.56-.35-.86-.5L16.9 2.27c-.03-.25-.25-.44-.5-.44h-3.84c-.25 0-.47.19-.5.44l-.36 2.54c-.3.15-.59.32-.86.5l-2.39-.96c-.22-.08-.47 0-.59.22L5.94 7.91c-.12.21-.06.47.12.61l2.03 1.58c-.02.16-.06.33-.06.5s.04.34.06.5L6.06 12.7c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.27.18.56.35.86.5l.36 2.54c.03.24.25.44.5.44h3.84c.25 0 .47-.19.5-.44l.36-2.54c.3-.15.59-.32.86-.5l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.06-.47-.12-.61l-2.03-1.58z" />
  </svg>
)

const CloseIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
  </svg>
)

interface MobileNavProps {
  isConnected: boolean
  balance: number
  configPanel: ReactNode
}

function formatBalance(n: number): string {
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toLocaleString()
}

export function MobileNav({ isConnected, balance, configPanel }: MobileNavProps) {
  const [configOpen, setConfigOpen] = useState(false)
  const pathname = usePathname()
  const { setVisible } = useWalletModal()

  const openConfig = useCallback(() => {
    setConfigOpen(true)
    document.body.style.overflow = 'hidden'
  }, [])

  const closeConfig = useCallback(() => {
    setConfigOpen(false)
    document.body.style.overflow = ''
  }, [])

  const handleWalletClick = useCallback(() => {
    setVisible(true)
  }, [setVisible])

  return (
    <>
      <nav className={styles.mobileNav} aria-label="Mobile navigation">
        <div className={styles.navItems}>
          <Link
            href="/"
            className={`${styles.navItem} ${pathname === '/' ? styles.active : ''}`}
          >
            <HomeIcon />
            <span className={styles.navLabel}>Home</span>
          </Link>

          <Link
            href="/lab"
            className={`${styles.navItem} ${pathname === '/lab' ? styles.active : ''}`}
          >
            <LabIcon />
            <span className={styles.navLabel}>Lab</span>
          </Link>

          <button
            className={`${styles.navItem} ${isConnected ? styles.connected : ''}`}
            onClick={handleWalletClick}
            aria-label={isConnected ? `Wallet: ${balance} HOPIUM` : 'Connect wallet'}
            data-onboarding="mobile-wallet"
          >
            <WalletIcon />
            <span className={styles.navLabel}>
              {isConnected ? formatBalance(balance) : 'Connect'}
            </span>
          </button>

          <button
            className={`${styles.navItem} ${styles.configToggle}`}
            onClick={openConfig}
            aria-label="Open configuration"
            aria-expanded={configOpen}
          >
            <ConfigIcon />
            <span className={styles.navLabel}>Config</span>
          </button>
        </div>
      </nav>

      {/* Config Sheet */}
      <div
        className={`${styles.configSheet} ${configOpen ? styles.open : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="Token configuration"
      >
        <div
          className={styles.configBackdrop}
          onClick={closeConfig}
          aria-hidden="true"
        />
        <div className={styles.configContent}>
          <div className={styles.configHandle}>
            <div className={styles.configHandleBar} />
          </div>
          <div className={styles.configHeader}>
            <span className={styles.configTitle}>Configure Token</span>
            <button
              className={styles.closeBtn}
              onClick={closeConfig}
              aria-label="Close configuration"
            >
              <CloseIcon />
            </button>
          </div>
          <div className={styles.configBody}>
            {configPanel}
          </div>
        </div>
      </div>
    </>
  )
}
