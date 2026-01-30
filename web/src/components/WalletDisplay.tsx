'use client'

interface WalletDisplayProps {
  balance: number
  pendingStake: number | null
  compact?: boolean
  showDemo?: boolean
}

export function WalletDisplay({ balance, pendingStake, compact = false, showDemo = true }: WalletDisplayProps) {
  const demoBadge = showDemo && (
    <span style={{
      padding: '2px 6px',
      background: 'var(--warning)',
      color: '#000',
      borderRadius: '4px',
      fontSize: '10px',
      fontWeight: 700,
      textTransform: 'uppercase',
    }}>
      Demo
    </span>
  )

  if (compact) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '6px 12px',
        background: 'var(--bg-secondary)',
        borderRadius: '9999px',
        fontSize: '14px',
      }}>
        <span>💰</span>
        <span style={{ fontWeight: 600 }}>{balance.toLocaleString()}</span>
        <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>$HOPIUM</span>
        {demoBadge}
        {pendingStake !== null && (
          <span style={{ color: 'var(--warning)', fontSize: '12px' }}>
            (-{pendingStake} staked)
          </span>
        )}
      </div>
    )
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px 16px',
      background: 'var(--bg-secondary)',
      borderRadius: '9999px',
    }}>
      <span style={{ fontSize: '20px' }}>💰</span>
      <span style={{ fontWeight: 700, fontSize: '18px' }}>{balance.toLocaleString()}</span>
      <span style={{ color: 'var(--text-secondary)' }}>$HOPIUM</span>
      {demoBadge}
      {pendingStake !== null && (
        <span style={{ color: 'var(--warning)', marginLeft: '8px' }}>
          🔒 {pendingStake} staked
        </span>
      )}
    </div>
  )
}
