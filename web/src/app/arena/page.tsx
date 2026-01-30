'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { config } from '@/config'
import { useWallet, STAKE_TIERS, StakeTier } from '@/hooks/useWallet'
import { WalletDisplay } from '@/components/WalletDisplay'

const API_URL = config.apiUrl

const OUTCOMES = ['moon', 'cult_classic', 'pump_and_dump', 'slow_bleed', 'rug'] as const
type Outcome = typeof OUTCOMES[number]

const OUTCOME_DISPLAY: Record<Outcome, { emoji: string; label: string; color: string }> = {
  moon: { emoji: '🌕', label: 'Moon', color: 'var(--success)' },
  cult_classic: { emoji: '⭐', label: 'Cult Classic', color: 'var(--accent)' },
  pump_and_dump: { emoji: '📈', label: 'Pump & Dump', color: 'var(--warning)' },
  slow_bleed: { emoji: '📉', label: 'Slow Bleed', color: 'var(--text-secondary)' },
  rug: { emoji: '💀', label: 'Rug', color: 'var(--danger)' },
}

interface SimHistory {
  id: string
  tokenName: string
  ticker: string
  stake: number
  burned: number
  outcome: Outcome
  score: number
  timestamp: number
}

export default function Arena() {
  const wallet = useWallet()

  // History
  const [history, setHistory] = useState<SimHistory[]>([])

  // Simulation state
  const [tokenName, setTokenName] = useState('')
  const [ticker, setTicker] = useState('')
  const [market, setMarket] = useState('crab')
  const [stake, setStake] = useState<StakeTier>(100)

  // Phases
  const [phase, setPhase] = useState<'setup' | 'simulating' | 'result'>('setup')
  const [simProgress, setSimProgress] = useState(0)
  const [result, setResult] = useState<{ outcome: Outcome; score: number } | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Load history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('hopium_sim_history')
    if (saved) {
      try {
        setHistory(JSON.parse(saved))
      } catch { /* ignore */ }
    }
  }, [])

  // Save history
  useEffect(() => {
    localStorage.setItem('hopium_sim_history', JSON.stringify(history))
  }, [history])

  const canSimulate = tokenName.trim() && ticker.trim() && wallet.canAfford(stake)

  const handleRunSimulation = async () => {
    if (!canSimulate) return

    // Stake tokens
    if (!wallet.stake(stake)) {
      setError('Insufficient balance')
      return
    }

    setPhase('simulating')
    setSimProgress(0)
    setError(null)

    try {
      const tier = STAKE_TIERS[stake]
      const simHours = tier.hours

      const response = await fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: {
            name: tokenName,
            ticker: ticker.toUpperCase(),
            narrative: `A ${market} market meme token`,
            meme_style: 'absurd',
            market_condition: market,
          },
          hours: simHours,
        }),
      })

      if (!response.ok) throw new Error('Simulation failed')

      // Simulate progress
      for (let i = 0; i <= 100; i += 5) {
        setSimProgress(i)
        await new Promise(r => setTimeout(r, 100))
      }

      const data = await response.json()
      const actualOutcome = data.result.predicted_outcome as Outcome
      const score = data.result.confidence

      setResult({ outcome: actualOutcome, score })

      // Complete simulation - stake returned minus burn
      wallet.completeSimulation()

      const burnAmount = Math.floor(stake * wallet.BURN_RATE)

      // Add to history
      setHistory(prev => [{
        id: `sim_${Date.now()}`,
        tokenName,
        ticker: ticker.toUpperCase(),
        stake,
        burned: burnAmount,
        outcome: actualOutcome,
        score,
        timestamp: Date.now(),
      }, ...prev.slice(0, 49)])

      setPhase('result')
    } catch (err) {
      console.error('Simulation error:', err)
      setError('Simulation failed. Refunding stake.')
      wallet.refundStake()
      setPhase('setup')
    }
  }

  const handleNewSimulation = () => {
    setPhase('setup')
    setTokenName('')
    setTicker('')
    setResult(null)
    setSimProgress(0)
  }

  return (
    <div className="lab-container">
      {/* Header */}
      <header className="lab-header">
        <div className="lab-header-left">
          <span className="lab-logo">🔬</span>
          <h1>Simulation Arena</h1>
          <span className="lab-badge" style={{ background: 'linear-gradient(90deg, #9333ea, #f91880)', color: 'white' }}>
            Stake to Simulate
          </span>
          <span style={{
            padding: '4px 8px',
            background: 'var(--warning)',
            color: '#000',
            borderRadius: '4px',
            fontSize: '11px',
            fontWeight: 700,
            marginLeft: '8px',
          }}>
            DEMO MODE
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <WalletDisplay balance={wallet.balance} pendingStake={wallet.pendingStake} />
          <Link href="/lab" className="nav-link">
            <span>🧪</span>
            <span>Lab</span>
          </Link>
          <Link href="/" className="nav-link">
            <span>🏠</span>
            <span>Home</span>
          </Link>
        </div>
      </header>

      {/* Demo Notice */}
      <div style={{
        background: 'rgba(255, 212, 0, 0.1)',
        border: '1px solid var(--warning)',
        borderRadius: '8px',
        padding: '12px 16px',
        margin: '0 16px 16px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
      }}>
        <span style={{ fontSize: '20px' }}>⚠️</span>
        <div style={{ fontSize: '13px' }}>
          <strong>Demo Mode:</strong> $HOPIUM tokens are synthetic and stored in your browser.
          This demonstrates the staking economy that will be implemented when $HOPIUM launches.
        </div>
      </div>

      <div className="lab-content">
        {/* Left Panel - Stats & History */}
        <aside className="lab-controls">
          {/* Wallet Stats */}
          <div className="control-card">
            <div className="control-card-header">
              <span>📊</span>
              <span>Your Stats</span>
            </div>
            <div style={{ padding: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700 }}>{wallet.simulationsRun}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Simulations</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--danger)' }}>🔥 {wallet.totalBurned}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Burned</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px', gridColumn: 'span 2' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700 }}>{wallet.totalStaked.toLocaleString()}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Staked</div>
                </div>
              </div>
              {wallet.balance <= 0 && (
                <button
                  onClick={wallet.claimFaucet}
                  style={{
                    width: '100%',
                    marginTop: '16px',
                    padding: '12px',
                    background: 'var(--accent)',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  🎁 Claim 1,000 $HOPIUM
                </button>
              )}
            </div>
          </div>

          {/* Recent Simulations */}
          <div className="control-card">
            <div className="control-card-header">
              <span>📜</span>
              <span>Recent Simulations</span>
            </div>
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {history.length === 0 ? (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  No simulations yet
                </div>
              ) : (
                history.slice(0, 10).map(sim => (
                  <div key={sim.id} style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}>
                    <div>
                      <div style={{ fontWeight: 600 }}>${sim.ticker}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {OUTCOME_DISPLAY[sim.outcome].emoji} {OUTCOME_DISPLAY[sim.outcome].label}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Staked: {sim.stake}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--danger)' }}>
                        Burned: {sim.burned}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Main Area - Simulation Interface */}
        <main className="lab-feed">
          {error && (
            <div className="error-banner" style={{ marginBottom: '16px' }}>
              {error}
            </div>
          )}

          {/* Setup Phase */}
          {phase === 'setup' && (
            <div className="control-card" style={{ maxWidth: '500px', margin: '0 auto' }}>
              <div className="control-card-header" style={{ textAlign: 'center', fontSize: '20px' }}>
                <span>🔬</span>
                <span>Run Simulation</span>
              </div>

              <div style={{ padding: '24px' }}>
                {/* Token Details */}
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Token Name</label>
                  <input
                    type="text"
                    value={tokenName}
                    onChange={e => setTokenName(e.target.value)}
                    placeholder="e.g., PepeCoin"
                    style={{
                      width: '100%',
                      padding: '12px',
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      color: 'var(--text-primary)',
                      fontSize: '16px',
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Ticker</label>
                  <div style={{ position: 'relative' }}>
                    <span style={{
                      position: 'absolute',
                      left: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      color: 'var(--text-secondary)',
                    }}>$</span>
                    <input
                      type="text"
                      value={ticker}
                      onChange={e => setTicker(e.target.value.toUpperCase().slice(0, 6))}
                      placeholder="PEPE"
                      style={{
                        width: '100%',
                        padding: '12px 12px 12px 28px',
                        background: 'var(--bg-primary)',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        color: 'var(--text-primary)',
                        fontSize: '16px',
                        textTransform: 'uppercase',
                      }}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Market Condition</label>
                  <select
                    value={market}
                    onChange={e => setMarket(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      color: 'var(--text-primary)',
                      fontSize: '16px',
                    }}
                  >
                    <option value="bear">🐻 Bear Market</option>
                    <option value="crab">🦀 Crab Market</option>
                    <option value="bull">🐂 Bull Market</option>
                    <option value="euphoria">🚀 Euphoria</option>
                  </select>
                </div>

                {/* Stake Selection */}
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Simulation Tier</label>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {(Object.entries(STAKE_TIERS) as [string, { hours: number; label: string }][]).map(([amount, tier]) => {
                      const amountNum = parseInt(amount) as StakeTier
                      const affordable = wallet.canAfford(amountNum)
                      const isSelected = stake === amountNum
                      const burnAmount = Math.floor(amountNum * 0.05)

                      return (
                        <button
                          key={amount}
                          onClick={() => affordable && setStake(amountNum)}
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
                          <div style={{ textAlign: 'right', fontSize: '12px' }}>
                            <div>Returns: {(amountNum - burnAmount).toLocaleString()}</div>
                            <div style={{ color: isSelected ? 'rgba(255,255,255,0.7)' : 'var(--danger)' }}>
                              Burns: {burnAmount.toLocaleString()}
                            </div>
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>

                {/* Run Button */}
                <button
                  onClick={handleRunSimulation}
                  disabled={!canSimulate}
                  style={{
                    width: '100%',
                    padding: '16px',
                    background: canSimulate ? 'linear-gradient(90deg, #1d9bf0, #9333ea)' : 'var(--bg-tertiary)',
                    border: 'none',
                    borderRadius: '9999px',
                    color: canSimulate ? 'white' : 'var(--text-secondary)',
                    fontSize: '18px',
                    fontWeight: 700,
                    cursor: canSimulate ? 'pointer' : 'not-allowed',
                  }}
                >
                  {!tokenName || !ticker ? 'Enter Token Details' :
                   !wallet.canAfford(stake) ? 'Insufficient Balance' :
                   `🔒 Stake ${stake.toLocaleString()} & Simulate`}
                </button>

                <div style={{ textAlign: 'center', marginTop: '12px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Stake returned after simulation • 5% burned
                </div>
              </div>
            </div>
          )}

          {/* Simulating Phase */}
          {phase === 'simulating' && (
            <div className="control-card" style={{ maxWidth: '500px', margin: '0 auto', textAlign: 'center' }}>
              <div style={{ padding: '48px 24px' }}>
                <div style={{ fontSize: '64px', marginBottom: '24px' }}>🔮</div>
                <h2 style={{ marginBottom: '8px' }}>Simulating ${ticker}...</h2>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
                  Running through CT reactions in {market} market
                </p>

                <div style={{
                  height: '8px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: '4px',
                  overflow: 'hidden',
                  marginBottom: '16px',
                }}>
                  <div style={{
                    height: '100%',
                    width: `${simProgress}%`,
                    background: 'linear-gradient(90deg, #1d9bf0, #9333ea)',
                    transition: 'width 0.1s ease-out',
                  }} />
                </div>

                <p style={{ fontWeight: 600, color: 'var(--warning)' }}>
                  🔒 {stake.toLocaleString()} $HOPIUM staked
                </p>
              </div>
            </div>
          )}

          {/* Result Phase */}
          {phase === 'result' && result && (
            <div className="control-card" style={{ maxWidth: '500px', margin: '0 auto', textAlign: 'center' }}>
              <div style={{ padding: '48px 24px' }}>
                <div style={{ fontSize: '80px', marginBottom: '16px' }}>
                  {OUTCOME_DISPLAY[result.outcome].emoji}
                </div>
                <h2 style={{ color: OUTCOME_DISPLAY[result.outcome].color, fontSize: '28px', marginBottom: '8px' }}>
                  {OUTCOME_DISPLAY[result.outcome].label}
                </h2>
                <p style={{ fontSize: '18px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
                  ${ticker} simulation complete
                </p>

                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '24px',
                  marginBottom: '32px',
                }}>
                  <div style={{
                    padding: '16px 24px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '12px',
                    textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Confidence</div>
                    <div style={{ fontSize: '24px', fontWeight: 700 }}>{(result.score * 100).toFixed(0)}%</div>
                  </div>
                  <div style={{
                    padding: '16px 24px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '12px',
                    textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Returned</div>
                    <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--success)' }}>
                      {(stake * 0.95).toLocaleString()}
                    </div>
                  </div>
                  <div style={{
                    padding: '16px 24px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '12px',
                    textAlign: 'center',
                  }}>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Burned</div>
                    <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--danger)' }}>
                      🔥 {Math.floor(stake * 0.05).toLocaleString()}
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleNewSimulation}
                  style={{
                    width: '100%',
                    padding: '16px',
                    background: 'linear-gradient(90deg, #1d9bf0, #9333ea)',
                    border: 'none',
                    borderRadius: '9999px',
                    color: 'white',
                    fontSize: '18px',
                    fontWeight: 700,
                    cursor: 'pointer',
                  }}
                >
                  🔬 Run Another Simulation
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
