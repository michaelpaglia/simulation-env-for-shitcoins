'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { config } from '@/config'

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

// Whitepaper-aligned tiers: stake → hours
const STAKE_TIERS = {
  100: { hours: 12, label: 'Quick (12h)' },
  500: { hours: 24, label: 'Standard (24h)' },
  1000: { hours: 48, label: 'Full (48h)' },
  2500: { hours: 48, label: 'Gauntlet' },
} as const
const STAKE_OPTIONS = [100, 500, 1000, 2500] as const

interface BetHistory {
  id: string
  tokenName: string
  ticker: string
  stake: number
  prediction: Outcome
  actual: Outcome
  won: boolean
  payout: number
  timestamp: number
}

interface PlayerStats {
  balance: number
  totalBets: number
  wins: number
  losses: number
  totalWagered: number
  totalWon: number
  streak: number
  bestStreak: number
}

const DEFAULT_STATS: PlayerStats = {
  balance: 1000,
  totalBets: 0,
  wins: 0,
  losses: 0,
  totalWagered: 0,
  totalWon: 0,
  streak: 0,
  bestStreak: 0,
}

export default function Arena() {
  // Player state
  const [stats, setStats] = useState<PlayerStats>(DEFAULT_STATS)
  const [history, setHistory] = useState<BetHistory[]>([])

  // Bet state
  const [tokenName, setTokenName] = useState('')
  const [ticker, setTicker] = useState('')
  const [market, setMarket] = useState('crab')
  const [stake, setStake] = useState(100)
  const [prediction, setPrediction] = useState<Outcome | null>(null)

  // Simulation state
  const [phase, setPhase] = useState<'setup' | 'predict' | 'simulating' | 'result'>('setup')
  const [simProgress, setSimProgress] = useState(0)
  const [result, setResult] = useState<{ outcome: Outcome; score: number } | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Load from localStorage
  useEffect(() => {
    const savedStats = localStorage.getItem('hopium_stats')
    const savedHistory = localStorage.getItem('hopium_history')
    if (savedStats) setStats(JSON.parse(savedStats))
    if (savedHistory) setHistory(JSON.parse(savedHistory))
  }, [])

  // Save to localStorage
  useEffect(() => {
    localStorage.setItem('hopium_stats', JSON.stringify(stats))
  }, [stats])

  useEffect(() => {
    localStorage.setItem('hopium_history', JSON.stringify(history))
  }, [history])

  const canBet = tokenName.trim() && ticker.trim() && stake <= stats.balance && prediction

  const handlePlaceBet = async () => {
    if (!canBet || !prediction) return

    setPhase('simulating')
    setSimProgress(0)
    setError(null)

    // Deduct stake
    setStats(prev => ({ ...prev, balance: prev.balance - stake }))

    try {
      // Get hours based on stake tier (whitepaper-aligned)
      const tier = STAKE_TIERS[stake as keyof typeof STAKE_TIERS]
      const simHours = tier?.hours || 12

      // Run actual simulation via API
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

      // Calculate payout with 5% burn (whitepaper-aligned)
      const won = prediction === actualOutcome
      const burnAmount = Math.floor(stake * 0.05) // 5% burn
      const payout = won ? (stake * 2) - burnAmount : 0 // 2x return minus burn

      // Update stats
      setStats(prev => ({
        ...prev,
        balance: prev.balance + payout,
        totalBets: prev.totalBets + 1,
        wins: prev.wins + (won ? 1 : 0),
        losses: prev.losses + (won ? 0 : 1),
        totalWagered: prev.totalWagered + stake,
        totalWon: prev.totalWon + payout,
        streak: won ? prev.streak + 1 : 0,
        bestStreak: won ? Math.max(prev.bestStreak, prev.streak + 1) : prev.bestStreak,
      }))

      // Add to history
      setHistory(prev => [{
        id: `bet_${Date.now()}`,
        tokenName,
        ticker: ticker.toUpperCase(),
        stake,
        prediction,
        actual: actualOutcome,
        won,
        payout,
        timestamp: Date.now(),
      }, ...prev.slice(0, 49)]) // Keep last 50

      setPhase('result')
    } catch (err) {
      console.error('Simulation error:', err)
      setError('Simulation failed. Refunding stake.')
      setStats(prev => ({ ...prev, balance: prev.balance + stake }))
      setPhase('setup')
    }
  }

  const handleNewBet = () => {
    setPhase('setup')
    setTokenName('')
    setTicker('')
    setPrediction(null)
    setResult(null)
    setSimProgress(0)
  }

  const winRate = stats.totalBets > 0 ? ((stats.wins / stats.totalBets) * 100).toFixed(0) : '0'
  const profitLoss = stats.totalWon - stats.totalWagered

  return (
    <div className="lab-container">
      {/* Header */}
      <header className="lab-header">
        <div className="lab-header-left">
          <span className="lab-logo">🎰</span>
          <h1>Simulation Arena</h1>
          <span className="lab-badge" style={{ background: 'linear-gradient(90deg, #9333ea, #f91880)', color: 'white' }}>
            MVP
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'var(--bg-secondary)',
            borderRadius: '9999px',
          }}>
            <span style={{ fontSize: '20px' }}>💰</span>
            <span style={{ fontWeight: 700, fontSize: '18px' }}>{stats.balance.toLocaleString()}</span>
            <span style={{ color: 'var(--text-secondary)' }}>$HOPIUM</span>
          </div>
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

      <div className="lab-content">
        {/* Left Panel - Stats & History */}
        <aside className="lab-controls">
          {/* Player Stats */}
          <div className="control-card">
            <div className="control-card-header">
              <span>📊</span>
              <span>Your Stats</span>
            </div>
            <div style={{ padding: '16px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700 }}>{stats.totalBets}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Total Bets</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--success)' }}>{winRate}%</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Win Rate</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: profitLoss >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                    {profitLoss >= 0 ? '+' : ''}{profitLoss.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>P/L</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: 'var(--bg-tertiary)', borderRadius: '8px' }}>
                  <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--warning)' }}>🔥 {stats.streak}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Streak</div>
                </div>
              </div>
              {stats.balance <= 0 && (
                <button
                  onClick={() => setStats(prev => ({ ...prev, balance: 1000 }))}
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

          {/* Recent Bets */}
          <div className="control-card">
            <div className="control-card-header">
              <span>📜</span>
              <span>Recent Bets</span>
            </div>
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {history.length === 0 ? (
                <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                  No bets yet
                </div>
              ) : (
                history.slice(0, 10).map(bet => (
                  <div key={bet.id} style={{
                    padding: '12px 16px',
                    borderBottom: '1px solid var(--border)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}>
                    <div>
                      <div style={{ fontWeight: 600 }}>${bet.ticker}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        Bet: {OUTCOME_DISPLAY[bet.prediction].emoji} → Actual: {OUTCOME_DISPLAY[bet.actual].emoji}
                      </div>
                    </div>
                    <div style={{
                      fontWeight: 700,
                      color: bet.won ? 'var(--success)' : 'var(--danger)',
                    }}>
                      {bet.won ? `+${bet.payout}` : `-${bet.stake}`}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        {/* Main Area - Betting Interface */}
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
                <span>🎯</span>
                <span>Place Your Bet</span>
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

                {/* Stake Selection - Whitepaper Tiers */}
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Simulation Tier</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                    {STAKE_OPTIONS.map(amount => {
                      const tier = STAKE_TIERS[amount]
                      return (
                        <button
                          key={amount}
                          onClick={() => setStake(amount)}
                          disabled={amount > stats.balance}
                          style={{
                            padding: '12px',
                            background: stake === amount ? 'var(--accent)' : 'var(--bg-tertiary)',
                            border: stake === amount ? '2px solid var(--accent)' : '2px solid transparent',
                            borderRadius: '8px',
                            color: stake === amount ? 'white' : amount > stats.balance ? 'var(--text-secondary)' : 'var(--text-primary)',
                            fontWeight: 600,
                            cursor: amount > stats.balance ? 'not-allowed' : 'pointer',
                            opacity: amount > stats.balance ? 0.5 : 1,
                            textAlign: 'left',
                          }}
                        >
                          <div style={{ fontSize: '16px' }}>{amount} $HOPIUM</div>
                          <div style={{ fontSize: '11px', opacity: 0.8 }}>{tier.label}</div>
                        </button>
                      )
                    })}
                  </div>
                </div>

                {/* Outcome Prediction */}
                <div style={{ marginBottom: '24px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Your Prediction</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px' }}>
                    {OUTCOMES.map(outcome => (
                      <button
                        key={outcome}
                        onClick={() => setPrediction(outcome)}
                        style={{
                          padding: '12px 8px',
                          background: prediction === outcome ? OUTCOME_DISPLAY[outcome].color : 'var(--bg-tertiary)',
                          border: prediction === outcome ? `2px solid ${OUTCOME_DISPLAY[outcome].color}` : '2px solid transparent',
                          borderRadius: '8px',
                          color: prediction === outcome ? 'white' : 'var(--text-primary)',
                          cursor: 'pointer',
                          textAlign: 'center',
                        }}
                      >
                        <div style={{ fontSize: '24px' }}>{OUTCOME_DISPLAY[outcome].emoji}</div>
                        <div style={{ fontSize: '10px', marginTop: '4px' }}>{OUTCOME_DISPLAY[outcome].label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Place Bet Button */}
                <button
                  onClick={handlePlaceBet}
                  disabled={!canBet}
                  style={{
                    width: '100%',
                    padding: '16px',
                    background: canBet ? 'linear-gradient(90deg, #1d9bf0, #9333ea)' : 'var(--bg-tertiary)',
                    border: 'none',
                    borderRadius: '9999px',
                    color: canBet ? 'white' : 'var(--text-secondary)',
                    fontSize: '18px',
                    fontWeight: 700,
                    cursor: canBet ? 'pointer' : 'not-allowed',
                  }}
                >
                  {!tokenName || !ticker ? 'Enter Token Details' :
                   !prediction ? 'Select Prediction' :
                   stake > stats.balance ? 'Insufficient Balance' :
                   `🎲 Bet ${stake} $HOPIUM`}
                </button>

                <div style={{ textAlign: 'center', marginTop: '12px', fontSize: '14px', color: 'var(--text-secondary)' }}>
                  Win = 2x return (minus 5% burn) • Lose = stake burned
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

                <p style={{ fontWeight: 600 }}>
                  Your prediction: {prediction && OUTCOME_DISPLAY[prediction].emoji} {prediction && OUTCOME_DISPLAY[prediction].label}
                </p>
              </div>
            </div>
          )}

          {/* Result Phase */}
          {phase === 'result' && result && prediction && (
            <div className="control-card" style={{ maxWidth: '500px', margin: '0 auto', textAlign: 'center' }}>
              <div style={{ padding: '48px 24px' }}>
                {result.outcome === prediction ? (
                  <>
                    <div style={{ fontSize: '80px', marginBottom: '16px' }}>🎉</div>
                    <h2 style={{ color: 'var(--success)', fontSize: '28px', marginBottom: '8px' }}>YOU WON!</h2>
                    <p style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>
                      +{stake * 2} $HOPIUM
                    </p>
                  </>
                ) : (
                  <>
                    <div style={{ fontSize: '80px', marginBottom: '16px' }}>😤</div>
                    <h2 style={{ color: 'var(--danger)', fontSize: '28px', marginBottom: '8px' }}>REKT</h2>
                    <p style={{ fontSize: '24px', fontWeight: 700, marginBottom: '24px' }}>
                      -{stake} $HOPIUM burned
                    </p>
                  </>
                )}

                <div style={{
                  display: 'flex',
                  justifyContent: 'center',
                  gap: '32px',
                  marginBottom: '32px',
                }}>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Your Bet</div>
                    <div style={{ fontSize: '32px' }}>{OUTCOME_DISPLAY[prediction].emoji}</div>
                    <div style={{ fontWeight: 600 }}>{OUTCOME_DISPLAY[prediction].label}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', fontSize: '24px' }}>→</div>
                  <div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Actual Result</div>
                    <div style={{ fontSize: '32px' }}>{OUTCOME_DISPLAY[result.outcome].emoji}</div>
                    <div style={{ fontWeight: 600, color: OUTCOME_DISPLAY[result.outcome].color }}>
                      {OUTCOME_DISPLAY[result.outcome].label}
                    </div>
                  </div>
                </div>

                <div style={{
                  background: 'var(--bg-tertiary)',
                  padding: '16px',
                  borderRadius: '12px',
                  marginBottom: '24px',
                }}>
                  <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
                    ${ticker} simulation confidence: {(result.score * 100).toFixed(0)}%
                  </div>
                </div>

                <button
                  onClick={handleNewBet}
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
                  🎲 Bet Again
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
