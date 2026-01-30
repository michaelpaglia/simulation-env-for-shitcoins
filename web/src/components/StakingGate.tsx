'use client'

import { useState } from 'react'
import { STAKE_TIERS, StakeTier } from '@/hooks/useWallet'

interface StakingGateProps {
  balance: number
  onStake: (amount: number, hours: number) => void
  onCancel: () => void
  isStaking?: boolean
}

export function StakingGate({ balance, onStake, onCancel, isStaking = false }: StakingGateProps) {
  const [selectedTier, setSelectedTier] = useState<StakeTier>(100)
  const tiers = Object.entries(STAKE_TIERS) as [string, { hours: number; lockDays: number; label: string; lockLabel: string }][]

  const canAfford = balance >= selectedTier

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        background: 'var(--bg-secondary)',
        borderRadius: '16px',
        padding: '24px',
        maxWidth: '400px',
        width: '90%',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <h2 style={{ margin: 0, fontSize: '20px' }}>🔒 Stake to Simulate</h2>
          <span style={{
            padding: '2px 8px',
            background: 'var(--warning)',
            color: '#000',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
          }}>
            Demo Mode
          </span>
        </div>
        <p style={{ color: 'var(--text-secondary)', margin: '0 0 20px 0', fontSize: '14px' }}>
          Stake $HOPIUM to run this simulation. Your stake is locked for a period based on tier, then returned minus 5% burn.
          <br />
          <span style={{ fontSize: '12px', fontStyle: 'italic' }}>
            Higher stake = shorter lock period. Demo mode: lock periods are simulated.
          </span>
        </p>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '12px',
          background: 'var(--bg-tertiary)',
          borderRadius: '8px',
          marginBottom: '20px',
        }}>
          <span style={{ fontSize: '24px' }}>💰</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: '18px' }}>{balance.toLocaleString()}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Available Balance</div>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '14px' }}>
            Select Tier
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {tiers.map(([amount, tier]) => {
              const amountNum = parseInt(amount)
              const affordable = balance >= amountNum
              const isSelected = selectedTier === amountNum

              return (
                <button
                  key={amount}
                  onClick={() => affordable && setSelectedTier(amountNum as StakeTier)}
                  disabled={!affordable}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px 16px',
                    background: isSelected ? 'var(--accent)' : 'var(--bg-tertiary)',
                    border: isSelected ? '2px solid var(--accent)' : '2px solid transparent',
                    borderRadius: '8px',
                    color: isSelected ? 'white' : affordable ? 'var(--text-primary)' : 'var(--text-secondary)',
                    cursor: affordable ? 'pointer' : 'not-allowed',
                    opacity: affordable ? 1 : 0.5,
                    textAlign: 'left',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>{amountNum.toLocaleString()} $HOPIUM</div>
                    <div style={{ fontSize: '12px', opacity: 0.8 }}>{tier.label}</div>
                  </div>
                  <div style={{ textAlign: 'center', fontSize: '11px', padding: '4px 8px', background: isSelected ? 'rgba(255,255,255,0.2)' : 'var(--bg-secondary)', borderRadius: '4px' }}>
                    <div>🔒 {tier.lockLabel}</div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>
                    <div>Returns: {(amountNum * 0.95).toLocaleString()}</div>
                    <div style={{ color: isSelected ? 'rgba(255,255,255,0.7)' : 'var(--danger)' }}>Burns: {(amountNum * 0.05).toLocaleString()}</div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={onCancel}
            disabled={isStaking}
            style={{
              flex: 1,
              padding: '12px',
              background: 'var(--bg-tertiary)',
              border: 'none',
              borderRadius: '8px',
              color: 'var(--text-primary)',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            onClick={() => onStake(selectedTier, STAKE_TIERS[selectedTier].hours)}
            disabled={!canAfford || isStaking}
            style={{
              flex: 2,
              padding: '12px',
              background: canAfford ? 'linear-gradient(90deg, #1d9bf0, #9333ea)' : 'var(--bg-tertiary)',
              border: 'none',
              borderRadius: '8px',
              color: canAfford ? 'white' : 'var(--text-secondary)',
              fontWeight: 700,
              cursor: canAfford ? 'pointer' : 'not-allowed',
            }}
          >
            {isStaking ? '🔄 Staking...' : `🔒 Stake ${selectedTier.toLocaleString()} $HOPIUM`}
          </button>
        </div>
      </div>
    </div>
  )
}
