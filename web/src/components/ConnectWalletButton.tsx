'use client'

import { useWalletModal } from '@solana/wallet-adapter-react-ui'
import { useAuth } from '@/hooks/useAuth'

interface ConnectWalletButtonProps {
  compact?: boolean
}

const styles = {
  base: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    border: 'none',
    color: 'white',
    fontWeight: 600,
    transition: 'all 0.2s',
    justifyContent: 'center',
  },
  compact: {
    padding: '8px 16px',
    borderRadius: '9999px',
    fontSize: '14px',
    width: '100%',
  },
  full: {
    padding: '12px 20px',
    borderRadius: '12px',
    fontSize: '15px',
    boxShadow: '0 4px 14px rgba(124, 77, 255, 0.3)',
  },
} as const

export function ConnectWalletButton({ compact = false }: ConnectWalletButtonProps) {
  const { isConnected, isConnecting, truncatedAddress, disconnect } = useAuth()
  const { setVisible } = useWalletModal()

  const handleClick = () => {
    if (isConnected) {
      disconnect()
    } else {
      setVisible(true)
    }
  }

  const getBackground = () => {
    if (compact) {
      return isConnected ? 'var(--bg-secondary)' : 'var(--accent)'
    }
    return isConnected
      ? 'linear-gradient(135deg, #512da8, #7c4dff)'
      : 'linear-gradient(135deg, #ab47bc, #7c4dff)'
  }

  const getLabel = () => {
    if (isConnecting) return 'Connecting...'
    if (isConnected) return truncatedAddress
    return compact ? 'Connect Wallet' : 'Connect Phantom'
  }

  const style = {
    ...styles.base,
    ...(compact ? styles.compact : styles.full),
    background: getBackground(),
    border: compact && isConnected ? '1px solid var(--border-color)' : 'none',
    cursor: isConnecting ? 'wait' : 'pointer',
  }

  return (
    <button onClick={handleClick} disabled={isConnecting} style={style}>
      <WalletIcon size={compact ? 16 : 20} />
      {getLabel()}
    </button>
  )
}

function WalletIcon({ size = 20 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M21 7H3a1 1 0 00-1 1v12a1 1 0 001 1h18a1 1 0 001-1V8a1 1 0 00-1-1zm-1 12H4v-2h16v2zm0-4H4v-2h16v2zm0-4H4V9h16v2zM5 5h14a1 1 0 000-2H5a1 1 0 000 2z"/>
    </svg>
  )
}
