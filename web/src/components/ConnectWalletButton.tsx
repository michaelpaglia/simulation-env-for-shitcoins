'use client'

import { useWalletModal } from '@solana/wallet-adapter-react-ui'
import { useAuth } from '@/hooks/useAuth'

interface ConnectWalletButtonProps {
  compact?: boolean
}

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

  if (compact) {
    return (
      <button
        onClick={handleClick}
        disabled={isConnecting}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '8px 16px',
          background: isConnected ? 'var(--bg-secondary)' : 'var(--accent)',
          border: isConnected ? '1px solid var(--border-color)' : 'none',
          borderRadius: '9999px',
          color: 'white',
          fontSize: '14px',
          fontWeight: 600,
          cursor: isConnecting ? 'wait' : 'pointer',
          transition: 'all 0.2s',
          width: '100%',
          justifyContent: 'center',
        }}
      >
        {isConnecting ? (
          'Connecting...'
        ) : isConnected ? (
          <>
            <PhantomIcon />
            {truncatedAddress}
          </>
        ) : (
          <>
            <PhantomIcon />
            Connect Wallet
          </>
        )}
      </button>
    )
  }

  return (
    <button
      onClick={handleClick}
      disabled={isConnecting}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '12px 20px',
        background: isConnected
          ? 'linear-gradient(135deg, #512da8, #7c4dff)'
          : 'linear-gradient(135deg, #ab47bc, #7c4dff)',
        border: 'none',
        borderRadius: '12px',
        color: 'white',
        fontSize: '15px',
        fontWeight: 600,
        cursor: isConnecting ? 'wait' : 'pointer',
        transition: 'all 0.2s',
        boxShadow: '0 4px 14px rgba(124, 77, 255, 0.3)',
      }}
    >
      <PhantomIcon />
      {isConnecting ? (
        'Connecting...'
      ) : isConnected ? (
        truncatedAddress
      ) : (
        'Connect Phantom'
      )}
    </button>
  )
}

function PhantomIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 128 128" fill="none">
      <circle cx="64" cy="64" r="64" fill="url(#phantom-gradient)" />
      <path
        d="M110.584 64.914H99.142C99.142 41.053 79.404 21.632 55.142 21.632C31.281 21.632 11.86 40.453 11.416 63.914C10.962 87.974 31.521 108.632 55.982 108.632H61.142C85.603 108.632 110.584 88.574 110.584 64.914Z"
        fill="url(#phantom-gradient2)"
      />
      <circle cx="39.142" cy="62.632" r="8" fill="#ffffff" />
      <circle cx="67.142" cy="62.632" r="8" fill="#ffffff" />
      <defs>
        <linearGradient id="phantom-gradient" x1="0" y1="0" x2="128" y2="128" gradientUnits="userSpaceOnUse">
          <stop stopColor="#534BB1" />
          <stop offset="1" stopColor="#551BF9" />
        </linearGradient>
        <linearGradient id="phantom-gradient2" x1="11" y1="22" x2="111" y2="109" gradientUnits="userSpaceOnUse">
          <stop stopColor="#534BB1" />
          <stop offset="1" stopColor="#551BF9" />
        </linearGradient>
      </defs>
    </svg>
  )
}
