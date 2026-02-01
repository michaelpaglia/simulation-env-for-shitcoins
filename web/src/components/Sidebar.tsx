'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { HomeIcon, SearchIcon, BellIcon, MessageIcon, LabIcon, WhitepaperIcon, FeatherIcon } from './icons'
import { ConnectWalletButton } from './ConnectWalletButton'
import { WalletDisplay } from './WalletDisplay'
import styles from './Sidebar.module.css'

interface SidebarProps {
  isConnected: boolean
  balance: number
  pendingStake: number
  onClaimFaucet: () => void
}

export function Sidebar({ isConnected, balance, pendingStake, onClaimFaucet }: SidebarProps) {
  const pathname = usePathname()

  return (
    <aside className={styles.sidebar}>
      <button
        className={styles.logo}
        title="Hopium Lab"
        aria-label="Hopium Lab home"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      >
        <span className={styles.logoIcon}>&#129514;</span>
      </button>

      {/* Wallet Connection */}
      <div className={styles.walletSection}>
        <ConnectWalletButton compact />
      </div>

      {/* $HOPIUM Balance */}
      {isConnected && (
        <div className={styles.walletBalanceSection}>
          <WalletDisplay balance={balance} pendingStake={pendingStake} compact />
          {balance <= 0 && (
            <button onClick={onClaimFaucet} className={styles.faucetBtn}>
              Claim 1,000 $HOPIUM
            </button>
          )}
        </div>
      )}

      <nav className={styles.nav} aria-label="Main navigation">
        <Link
          href="/"
          className={`${styles.navItem} ${pathname === '/' ? styles.active : ''}`}
        >
          <HomeIcon />
          <span className={styles.navLabel}>Home</span>
        </Link>

        <button
          className={`${styles.navItem} ${styles.disabled}`}
          disabled
          aria-label="Explore (coming soon)"
          title="Coming soon"
        >
          <SearchIcon />
          <span className={styles.navLabel}>Explore</span>
          <span className={styles.comingSoon}>Soon</span>
        </button>

        <button
          className={`${styles.navItem} ${styles.disabled}`}
          disabled
          aria-label="Notifications (coming soon)"
          title="Coming soon"
        >
          <BellIcon />
          <span className={styles.navLabel}>Notifications</span>
          <span className={styles.comingSoon}>Soon</span>
        </button>

        <button
          className={`${styles.navItem} ${styles.disabled}`}
          disabled
          aria-label="Messages (coming soon)"
          title="Coming soon"
        >
          <MessageIcon />
          <span className={styles.navLabel}>Messages</span>
          <span className={styles.comingSoon}>Soon</span>
        </button>

        <Link
          href="/lab"
          className={`${styles.navItem} ${pathname === '/lab' ? styles.active : ''}`}
        >
          <LabIcon />
          <span className={styles.navLabel}>Harness Lab</span>
        </Link>

        <Link
          href="/whitepaper"
          className={`${styles.navItem} ${pathname === '/whitepaper' ? styles.active : ''}`}
        >
          <WhitepaperIcon />
          <span className={styles.navLabel}>Whitepaper</span>
        </Link>
      </nav>

      <button
        className={styles.postBtn}
        title="This is decorative - you can't actually post"
        aria-label="Shill (decorative)"
      >
        <span className={styles.postBtnLabel}>Shill</span>
        <FeatherIcon />
      </button>
    </aside>
  )
}
