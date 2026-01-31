'use client'

import { useState } from 'react'
import { STAKE_TIERS as DEMO_STAKE_TIERS, StakeTier as DemoStakeTier } from '@/hooks/useWallet'
import {
  STAKE_TIERS as ONCHAIN_STAKE_TIERS,
  StakeTier as OnchainStakeTier,
  toDisplayAmount,
  BURN_RATE_BPS,
} from '@/lib/solana/constants'
import { StakingStatus } from '@/hooks/useStaking'

export type StakingMode = 'demo' | 'onchain'

interface BaseStakingGateProps {
  balance: number
  onCancel: () => void
  isStaking?: boolean
}

interface DemoStakingGateProps extends BaseStakingGateProps {
  mode: 'demo'
  onStake: (amount: number, hours: number) => void
}

interface OnchainStakingGateProps extends BaseStakingGateProps {
  mode: 'onchain'
  onStake: (tier: OnchainStakeTier) => void
  stakingStatus?: StakingStatus
  statusMessage?: string
}

type StakingGateProps = DemoStakingGateProps | OnchainStakingGateProps

export function StakingGate(props: StakingGateProps) {
  const { balance, onCancel, isStaking = false, mode } = props

  // For demo mode, use the old tier system (100, 500, 1000)
  // For on-chain, use tier indices (0, 1, 2)
  const [selectedDemoTier, setSelectedDemoTier] = useState<DemoStakeTier>(100)
  const [selectedOnchainTier, setSelectedOnchainTier] = useState<OnchainStakeTier>(0)

  const isOnchain = mode === 'onchain'

  // Get status for on-chain mode
  const stakingStatus = isOnchain ? (props as OnchainStakingGateProps).stakingStatus : undefined
  const statusMessage = isOnchain ? (props as OnchainStakingGateProps).statusMessage : undefined

  // Get display balance
  const displayBalance = isOnchain
    ? balance // Already in display units for on-chain
    : balance // Demo uses whole numbers

  // Build tier display data
  const tierOptions = isOnchain
    ? Object.entries(ONCHAIN_STAKE_TIERS).map(([tierStr, config]) => ({
        tier: parseInt(tierStr) as OnchainStakeTier,
        amount: toDisplayAmount(config.amount),
        hours: config.simHours,
        lockDays: config.lockDays,
        label: config.label,
      }))
    : Object.entries(DEMO_STAKE_TIERS).map(([amountStr, config]) => ({
        tier: parseInt(amountStr) as DemoStakeTier,
        amount: parseInt(amountStr),
        hours: config.hours,
        lockDays: config.lockDays,
        label: config.label,
      }))

  const selectedTierData = isOnchain
    ? tierOptions.find(t => t.tier === selectedOnchainTier)!
    : tierOptions.find(t => t.tier === selectedDemoTier)!

  const canAfford = displayBalance >= selectedTierData.amount

  const handleStake = () => {
    if (isOnchain) {
      (props as OnchainStakingGateProps).onStake(selectedOnchainTier)
    } else {
      const demoConfig = DEMO_STAKE_TIERS[selectedDemoTier]
      ;(props as DemoStakingGateProps).onStake(selectedDemoTier, demoConfig.hours)
    }
  }

  const getStatusText = () => {
    if (!isOnchain || !stakingStatus) return isStaking ? 'Staking...' : `Stake ${selectedTierData.amount.toLocaleString()} $HOPIUM`

    switch (stakingStatus) {
      case 'building':
        return 'Building transaction...'
      case 'signing':
        return 'Approve in wallet...'
      case 'confirming':
        return 'Confirming on chain...'
      case 'success':
        return 'Stake confirmed!'
      case 'error':
        return statusMessage || 'Staking failed'
      default:
        return `Stake ${selectedTierData.amount.toLocaleString()} $HOPIUM`
    }
  }

  const isProcessing = isStaking || (stakingStatus && !['idle', 'success', 'error'].includes(stakingStatus))

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
          <h2 style={{ margin: 0, fontSize: '20px' }}>Stake to Simulate</h2>
          <span style={{
            padding: '2px 8px',
            background: isOnchain ? 'var(--success)' : 'var(--warning)',
            color: '#000',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
          }}>
            {isOnchain ? 'On-Chain' : 'Demo Mode'}
          </span>
        </div>
        <p style={{ color: 'var(--text-secondary)', margin: '0 0 20px 0', fontSize: '14px' }}>
          Stake $HOPIUM to run this simulation. Your stake is locked for a period based on tier, then returned minus 5% burn.
          {!isOnchain && (
            <>
              <br />
              <span style={{ fontSize: '12px', fontStyle: 'italic' }}>
                Higher stake = shorter lock period. Demo mode: lock periods are simulated.
              </span>
            </>
          )}
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
          <span style={{ fontSize: '24px' }}>{isOnchain ? '💎' : '💰'}</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: '18px' }}>{displayBalance.toLocaleString()}</div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
              {isOnchain ? 'Wallet Balance' : 'Demo Balance'}
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600, fontSize: '14px' }}>
            Select Tier
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {tierOptions.map((option) => {
              const affordable = displayBalance >= option.amount
              const isSelected = isOnchain
                ? selectedOnchainTier === option.tier
                : selectedDemoTier === option.tier

              return (
                <button
                  key={option.tier}
                  onClick={() => {
                    if (!affordable) return
                    if (isOnchain) {
                      setSelectedOnchainTier(option.tier as OnchainStakeTier)
                    } else {
                      setSelectedDemoTier(option.tier as DemoStakeTier)
                    }
                  }}
                  disabled={!affordable || !!isProcessing}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '12px 16px',
                    background: isSelected ? 'var(--accent)' : 'var(--bg-tertiary)',
                    border: isSelected ? '2px solid var(--accent)' : '2px solid transparent',
                    borderRadius: '8px',
                    color: isSelected ? 'white' : affordable ? 'var(--text-primary)' : 'var(--text-secondary)',
                    cursor: affordable && !isProcessing ? 'pointer' : 'not-allowed',
                    opacity: affordable ? 1 : 0.5,
                    textAlign: 'left',
                  }}
                >
                  <div>
                    <div style={{ fontWeight: 600 }}>{option.amount.toLocaleString()} $HOPIUM</div>
                    <div style={{ fontSize: '12px', opacity: 0.8 }}>{option.label}</div>
                  </div>
                  <div style={{
                    textAlign: 'center',
                    fontSize: '11px',
                    padding: '4px 8px',
                    background: isSelected ? 'rgba(255,255,255,0.2)' : 'var(--bg-secondary)',
                    borderRadius: '4px',
                  }}>
                    <div>{option.lockDays} day lock</div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '12px' }}>
                    <div>Returns: {(option.amount * 0.95).toLocaleString()}</div>
                    <div style={{ color: isSelected ? 'rgba(255,255,255,0.7)' : 'var(--danger)' }}>
                      Burns: {(option.amount * 0.05).toLocaleString()}
                    </div>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        {/* Status message for on-chain mode */}
        {isOnchain && stakingStatus && stakingStatus !== 'idle' && (
          <div style={{
            padding: '12px',
            marginBottom: '16px',
            borderRadius: '8px',
            background: stakingStatus === 'error' ? 'var(--danger-bg)' : stakingStatus === 'success' ? 'var(--success-bg)' : 'var(--bg-tertiary)',
            color: stakingStatus === 'error' ? 'var(--danger)' : stakingStatus === 'success' ? 'var(--success)' : 'var(--text-primary)',
            fontSize: '14px',
          }}>
            {stakingStatus === 'building' && '🔧 Building transaction...'}
            {stakingStatus === 'signing' && '✍️ Please approve the transaction in your wallet...'}
            {stakingStatus === 'confirming' && '⏳ Confirming on the blockchain...'}
            {stakingStatus === 'success' && '✅ Stake confirmed!'}
            {stakingStatus === 'error' && `❌ ${statusMessage || 'Transaction failed'}`}
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={onCancel}
            disabled={!!isProcessing}
            style={{
              flex: 1,
              padding: '12px',
              background: 'var(--bg-tertiary)',
              border: 'none',
              borderRadius: '8px',
              color: 'var(--text-primary)',
              fontWeight: 600,
              cursor: isProcessing ? 'not-allowed' : 'pointer',
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleStake}
            disabled={!canAfford || !!isProcessing}
            style={{
              flex: 2,
              padding: '12px',
              background: canAfford && !isProcessing ? 'var(--accent)' : 'var(--bg-tertiary)',
              border: 'none',
              borderRadius: '8px',
              color: canAfford && !isProcessing ? 'white' : 'var(--text-secondary)',
              fontWeight: 700,
              cursor: canAfford && !isProcessing ? 'pointer' : 'not-allowed',
            }}
          >
            {isProcessing ? '🔄 ' : '🔒 '}
            {getStatusText()}
          </button>
        </div>
      </div>
    </div>
  )
}
