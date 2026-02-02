'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { config } from '@/config'
import { useWallet } from '@/hooks/useWallet'
import { useAuth } from '@/hooks/useAuth'
import { WalletDisplay } from '@/components/WalletDisplay'
import { MobileNav } from '@/components/MobileNav'

const API_URL = config.apiUrl

interface HarnessConfig {
  mode: string
  max_experiments: number
  simulation_hours: number
  market_condition: string
  target_theme: string
}

interface Experiment {
  id: string
  ticker: string
  name: string
  strategy: string
  meme_style: string
  hook: string
  score: number | null
  status: string
  outcome: string | null
  progress?: { hour: number; total: number }
}

interface LeaderboardEntry {
  rank: number
  id: string
  ticker: string
  name: string
  score: number
  outcome: string
  strategy: string
  viral_coefficient: number
}

interface PastExperiment {
  id: string
  ticker: string
  name: string
  narrative: string
  hook: string
  strategy: string
  meme_style: string
  status: string
  score: number | null
  outcome: string | null
  viral_coefficient: number | null
  peak_sentiment: number | null
  fud_resistance: number | null
  total_engagement: number | null
  dominant_narrative: string | null
  created_at: string
  // Risk assessment
  risk_factors: string[] | null
  reasoning: string | null
  confidence: number | null
}

// Icons
const FlaskIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
    <path d="M9 3v8.5L5 18h14l-4-6.5V3H9zm-1-2h8a1 1 0 011 1v8.5l4 6.5a2 2 0 01-1.7 3H4.7A2 2 0 013 18l4-6.5V2a1 1 0 011-1z"/>
  </svg>
)

const HomeIcon = () => (
  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
    <path d="M21.591 7.146L12.52 1.157c-.316-.21-.724-.21-1.04 0l-9.071 5.99c-.26.173-.409.456-.409.757v13.183c0 .502.418.913.929.913h6.638c.511 0 .929-.41.929-.913v-7.075h3.008v7.075c0 .502.418.913.929.913h6.638c.511 0 .929-.41.929-.913V7.904c0-.301-.158-.584-.418-.758z" />
  </svg>
)

const TrophyIcon = () => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
    <path d="M12 2a3 3 0 00-3 3v1H5a2 2 0 00-2 2v2a4 4 0 004 4h.5A5.5 5.5 0 0012 17.5 5.5 5.5 0 0016.5 14h.5a4 4 0 004-4V8a2 2 0 00-2-2h-4V5a3 3 0 00-3-3zm-3 4h6v4a3 3 0 11-6 0V6zM5 8h2v2a5.002 5.002 0 01-.5 2H5a2 2 0 01-2-2V8zm14 0v2a2 2 0 01-2 2h-1.5a5.002 5.002 0 01-.5-2V8h4zM9 20h6v2H9v-2z"/>
  </svg>
)

// Calculate stake for harness run (base stake per experiment)
const HARNESS_STAKE_PER_EXPERIMENT = 50

export default function Lab() {
  const wallet = useWallet()
  const auth = useAuth()

  const [harnessConfig, setHarnessConfig] = useState<HarnessConfig>({
    mode: 'balanced',
    max_experiments: 5,
    simulation_hours: 24,
    market_condition: 'crab',
    target_theme: '',
  })

  const [isRunning, setIsRunning] = useState(false)
  const [showStakingConfirm, setShowStakingConfirm] = useState(false)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [currentExperiment, setCurrentExperiment] = useState<Experiment | null>(null)
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [runProgress, setRunProgress] = useState<{ completed: number; total: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [insights, setInsights] = useState<string[]>([])
  const [pastExperiments, setPastExperiments] = useState<PastExperiment[]>([])
  const [viewMode, setViewMode] = useState<'current' | 'history'>('history')
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'error'>('loading')

  // Filtering state
  const [outcomeFilter, setOutcomeFilter] = useState<string>('all')
  const [strategyFilter, setStrategyFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'score' | 'date' | 'viral'>('date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [expandedExperiment, setExpandedExperiment] = useState<string | null>(null)

  const eventSourceRef = useRef<AbortController | null>(null)

  // Get unique strategies and outcomes for filter options
  const uniqueStrategies = [...new Set(pastExperiments.map(e => e.strategy).filter(Boolean))]
  const uniqueOutcomes = [...new Set(pastExperiments.map(e => e.outcome).filter(Boolean))]

  // Filter and sort experiments
  const filteredExperiments = pastExperiments
    .filter(exp => {
      if (outcomeFilter !== 'all' && exp.outcome !== outcomeFilter) return false
      if (strategyFilter !== 'all' && exp.strategy !== strategyFilter) return false
      return true
    })
    .sort((a, b) => {
      let comparison = 0
      switch (sortBy) {
        case 'score':
          comparison = (a.score ?? 0) - (b.score ?? 0)
          break
        case 'viral':
          comparison = (a.viral_coefficient ?? 0) - (b.viral_coefficient ?? 0)
          break
        case 'date':
        default:
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
      }
      return sortOrder === 'desc' ? -comparison : comparison
    })

  // Load initial data
  useEffect(() => {
    const loadData = async () => {
      try {
        // First check if API is reachable
        const healthCheck = await fetch(`${API_URL}/health`)
        if (healthCheck.ok) {
          setApiStatus('connected')
          // Fire off fetches without blocking
          fetchLeaderboard()
          fetchLearnings()
          fetchPastExperiments()
        } else {
          setApiStatus('error')
        }
      } catch (e) {
        console.error('API not reachable:', e)
        setApiStatus('error')
      }
    }
    loadData()
  }, [])

  const fetchPastExperiments = async () => {
    try {
      const res = await fetch(`${API_URL}/harness/experiments`)
      if (res.ok) {
        const data = await res.json()
        console.log('Fetched experiments:', data)
        setPastExperiments(data.experiments || [])
      } else {
        console.error('Failed to fetch experiments:', res.status, res.statusText)
      }
    } catch (e) {
      console.error('Failed to fetch past experiments:', e)
      // API might not be running - that's OK
    }
  }

  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${API_URL}/harness/leaderboard`)
      if (res.ok) {
        const data = await res.json()
        setLeaderboard(data.leaderboard || [])
      }
    } catch (e) {
      console.error('Failed to fetch leaderboard:', e)
    }
  }

  const fetchLearnings = async () => {
    try {
      const res = await fetch(`${API_URL}/harness/learnings`)
      if (res.ok) {
        const data = await res.json()
        setInsights(data.insights || [])
      }
    } catch (e) {
      console.error('Failed to fetch learnings:', e)
    }
  }

  const requiredStake = harnessConfig.max_experiments * HARNESS_STAKE_PER_EXPERIMENT

  const handleLaunchClick = () => {
    if (!wallet.canAfford(requiredStake)) {
      setError(`Insufficient balance. Need ${requiredStake} $HOPIUM for ${harnessConfig.max_experiments} experiments.`)
      return
    }
    setShowStakingConfirm(true)
  }

  const confirmAndStartHarness = () => {
    if (!wallet.stake(requiredStake)) {
      setError('Failed to stake tokens')
      setShowStakingConfirm(false)
      return
    }
    setShowStakingConfirm(false)
    startHarness()
  }

  const startHarness = async () => {
    setIsRunning(true)
    setExperiments([])
    setCurrentExperiment(null)
    setError(null)
    setRunProgress(null)
    setViewMode('current')  // Switch to current run view

    try {
      console.log('Starting harness with config:', harnessConfig)

      // Start the harness run
      const startRes = await fetch(`${API_URL}/harness/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(harnessConfig),
      })

      console.log('Harness run response status:', startRes.status)

      if (!startRes.ok) {
        const err = await startRes.json()
        console.error('Harness run failed:', err)
        throw new Error(err.detail || 'Failed to start harness')
      }

      const runData = await startRes.json()
      console.log('Harness started:', runData)

      // Subscribe to SSE stream
      const controller = new AbortController()
      eventSourceRef.current = controller

      const streamRes = await fetch(`${API_URL}/harness/stream`, {
        signal: controller.signal,
      })

      if (!streamRes.ok) throw new Error('Failed to connect to stream')

      const reader = streamRes.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              console.log('SSE event:', event)
              handleHarnessEvent(event)

              if (event.type === 'done' || event.type === 'run_completed') {
                setIsRunning(false)
                wallet.completeSimulation() // Return stake minus burn
                fetchLeaderboard()
                fetchLearnings()
                fetchPastExperiments()
                return
              }
            } catch {
              // Ignore parse errors
            }
          }
        }
      }
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        console.error('Harness error:', err)
        const errorMsg = err instanceof Error ? err.message : 'Unknown error'
        setError(errorMsg)
        wallet.refundStake() // Refund on error
      }
    } finally {
      console.log('Harness finished/stopped')
      setIsRunning(false)
    }
  }

  const handleHarnessEvent = (event: Record<string, unknown>) => {
    switch (event.type) {
      case 'experiment_started':
        const newExp: Experiment = {
          id: event.experiment_id as string,
          ticker: (event.idea as Record<string, unknown>)?.ticker as string || 'UNK',
          name: (event.idea as Record<string, unknown>)?.name as string || 'Unknown',
          strategy: (event.idea as Record<string, unknown>)?.strategy as string || '',
          meme_style: (event.idea as Record<string, unknown>)?.meme_style as string || '',
          hook: (event.idea as Record<string, unknown>)?.hook as string || '',
          score: null,
          status: 'running',
          outcome: null,
        }
        setCurrentExperiment(newExp)
        setRunProgress({
          completed: (event.experiment_index as number) - 1,
          total: event.total_experiments as number,
        })
        break

      case 'experiment_completed':
        const idea = event.idea as Record<string, unknown> | undefined
        const completedExp: Experiment = {
          id: event.experiment_id as string,
          ticker: (idea?.ticker as string) || currentExperiment?.ticker || 'UNK',
          name: (idea?.name as string) || currentExperiment?.name || 'Unknown',
          strategy: (idea?.strategy as string) || currentExperiment?.strategy || '',
          meme_style: (idea?.meme_style as string) || currentExperiment?.meme_style || '',
          hook: (idea?.hook as string) || currentExperiment?.hook || '',
          score: event.score as number | null,
          status: 'completed',
          outcome: (event.result as Record<string, unknown>)?.predicted_outcome as string || null,
        }
        setExperiments(prev => [...prev, completedExp])
        setCurrentExperiment(null)
        setRunProgress({
          completed: event.experiment_index as number,
          total: event.total_experiments as number,
        })
        // Refresh past experiments list
        fetchPastExperiments()
        fetchLeaderboard()
        break

      case 'simulation_progress':
        if (currentExperiment) {
          setCurrentExperiment({
            ...currentExperiment,
            progress: {
              hour: event.hour as number,
              total: event.total_hours as number,
            }
          })
        }
        break

      case 'run_completed':
        setIsRunning(false)
        break

      case 'error':
        setError(event.message as string)
        break
    }
  }

  const stopHarness = async () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.abort()
    }
    try {
      await fetch(`${API_URL}/harness/stop`, { method: 'POST' })
    } catch (e) {
      console.error('Failed to stop harness:', e)
    }
    setIsRunning(false)
  }

  const getOutcomeColor = (outcome: string | null) => {
    switch (outcome) {
      case 'moon': return 'var(--success)'
      case 'cult_classic': return 'var(--accent)'
      case 'pump_and_dump': return 'var(--warning)'
      case 'slow_bleed': return 'var(--text-secondary)'
      case 'rug': return 'var(--danger)'
      default: return 'var(--text-secondary)'
    }
  }

  return (
    <div className="lab-container">
      {/* Staking Confirmation Modal */}
      {showStakingConfirm && (
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <h2 style={{ margin: 0, fontSize: '20px' }}>🔒 Stake to Run Harness</h2>
              <span style={{
                padding: '2px 8px',
                background: 'var(--warning)',
                color: '#000',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: 700,
              }}>
                DEMO
              </span>
            </div>

            <div style={{
              background: 'var(--bg-tertiary)',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '16px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>Experiments:</span>
                <span style={{ fontWeight: 600 }}>{harnessConfig.max_experiments}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span>Stake per experiment:</span>
                <span style={{ fontWeight: 600 }}>{HARNESS_STAKE_PER_EXPERIMENT} $HOPIUM</span>
              </div>
              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '8px', marginTop: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontWeight: 600 }}>Total Stake:</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent)' }}>
                    {requiredStake} $HOPIUM
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                  <span>5% burn:</span>
                  <span style={{ color: 'var(--danger)' }}>-{Math.floor(requiredStake * 0.05)}</span>
                </div>
              </div>
            </div>

            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '0 0 16px 0' }}>
              Your stake will be returned after the harness completes, minus a 5% burn.
            </p>

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setShowStakingConfirm(false)}
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
                onClick={confirmAndStartHarness}
                style={{
                  flex: 2,
                  padding: '12px',
                  background: 'var(--accent)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontWeight: 700,
                  cursor: 'pointer',
                }}
              >
                🔒 Stake & Launch
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="lab-header">
        <div className="lab-header-left">
          <span className="lab-logo">&#129514;</span>
          <h1>Harness Lab</h1>
          <span className="lab-badge">Autonomous Testing</span>
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
          {apiStatus !== 'connected' && (
            <span className="api-status" style={{
              marginLeft: '12px',
              padding: '4px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              background: apiStatus === 'error' ? 'var(--danger)' : 'var(--warning)',
              color: '#000'
            }}>
              {apiStatus === 'error' ? 'API Offline' : 'Connecting...'}
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <WalletDisplay balance={wallet.balance} pendingStake={wallet.pendingStake} />
          <Link href="/" className="nav-link">
            <HomeIcon />
            <span>Single Sim</span>
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
        <div style={{ flex: 1, fontSize: '13px' }}>
          <strong>Demo Mode:</strong> Staking uses synthetic $HOPIUM tokens stored in your browser.
          Each experiment costs {HARNESS_STAKE_PER_EXPERIMENT} $HOPIUM (5% burned).
        </div>
        {wallet.balance <= 0 && (
          <button
            onClick={wallet.claimFaucet}
            style={{
              padding: '8px 16px',
              background: 'var(--accent)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              fontWeight: 600,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
            }}
          >
            🎁 Claim 1,000
          </button>
        )}
      </div>

      <div className="lab-content">
        {/* Left Panel - Controls */}
        <aside className="lab-controls">
          <div className="control-card">
            <div className="control-card-header">
              <FlaskIcon />
              <span>Experiment Config</span>
            </div>

            <div className="control-group">
              <label>Mode</label>
              <select
                value={harnessConfig.mode}
                onChange={e => setHarnessConfig({ ...harnessConfig, mode: e.target.value })}
                disabled={isRunning}
              >
                <option value="balanced">Balanced (Explore + Exploit)</option>
                <option value="explore">Explore (Maximize Learning)</option>
                <option value="exploit">Exploit (Focus on Winners)</option>
                <option value="targeted">Targeted (Specific Theme)</option>
              </select>
            </div>

            {harnessConfig.mode === 'targeted' && (
              <div className="control-group">
                <label>Target Theme</label>
                <input
                  type="text"
                  placeholder="e.g., AI cats, nostalgic memes"
                  value={harnessConfig.target_theme}
                  onChange={e => setHarnessConfig({ ...harnessConfig, target_theme: e.target.value })}
                  disabled={isRunning}
                />
              </div>
            )}

            <div className="control-group">
              <label>Experiments</label>
              <input
                type="number"
                min={1}
                max={20}
                value={harnessConfig.max_experiments}
                onChange={e => setHarnessConfig({ ...harnessConfig, max_experiments: parseInt(e.target.value) || 5 })}
                disabled={isRunning}
              />
            </div>

            <div className="control-group">
              <label>Hours per Simulation</label>
              <select
                value={harnessConfig.simulation_hours}
                onChange={e => setHarnessConfig({ ...harnessConfig, simulation_hours: parseInt(e.target.value) })}
                disabled={isRunning}
              >
                <option value={12}>12 hours (Quick)</option>
                <option value={24}>24 hours (Standard)</option>
                <option value={48}>48 hours (Full)</option>
              </select>
            </div>

            <div className="control-group">
              <label>Market Condition</label>
              <select
                value={harnessConfig.market_condition}
                onChange={e => setHarnessConfig({ ...harnessConfig, market_condition: e.target.value })}
                disabled={isRunning}
              >
                <option value="bear">Bear Market</option>
                <option value="crab">Crab Market</option>
                <option value="bull">Bull Market</option>
                <option value="euphoria">Euphoria</option>
              </select>
            </div>

            {!isRunning ? (
              <button
                className="launch-btn"
                onClick={handleLaunchClick}
                disabled={!wallet.canAfford(requiredStake)}
                style={{
                  opacity: wallet.canAfford(requiredStake) ? 1 : 0.5,
                  cursor: wallet.canAfford(requiredStake) ? 'pointer' : 'not-allowed',
                }}
              >
                🔒 Stake {requiredStake} & Launch
              </button>
            ) : (
              <button className="stop-btn" onClick={stopHarness}>
                &#9632; Stop Harness
              </button>
            )}

            {runProgress && (
              <div className="run-progress">
                <div className="progress-text">
                  Progress: {runProgress.completed}/{runProgress.total} experiments
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${(runProgress.completed / runProgress.total) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Leaderboard */}
          <div className="control-card">
            <div className="control-card-header">
              <TrophyIcon />
              <span>Leaderboard</span>
            </div>
            <div className="leaderboard">
              {leaderboard.length === 0 ? (
                <div className="empty-leaderboard">No experiments yet</div>
              ) : (
                leaderboard.slice(0, 5).map((entry, i) => (
                  <div key={entry.id} className="leaderboard-entry">
                    <span className="rank">#{entry.rank}</span>
                    <div className="entry-info">
                      <span className="ticker">${entry.ticker}</span>
                      <span className="score">{(entry.score * 100).toFixed(0)}%</span>
                    </div>
                    <span
                      className="outcome-badge"
                      style={{ background: getOutcomeColor(entry.outcome) }}
                    >
                      {entry.outcome?.replace('_', ' ')}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Insights */}
          {insights.length > 0 && (
            <div className="control-card">
              <div className="control-card-header">
                <span>&#128161;</span>
                <span>Insights</span>
              </div>
              <div className="insights-list">
                {insights.map((insight, i) => (
                  <div key={i} className="insight-item">{insight}</div>
                ))}
              </div>
            </div>
          )}
        </aside>

        {/* Main Area - Experiments Feed */}
        <main className="lab-feed">
          {/* View Toggle */}
          <div className="view-toggle">
            <button
              className={`toggle-btn ${viewMode === 'current' ? 'active' : ''}`}
              onClick={() => setViewMode('current')}
            >
              Current Run
            </button>
            <button
              className={`toggle-btn ${viewMode === 'history' ? 'active' : ''}`}
              onClick={() => setViewMode('history')}
            >
              Past Experiments ({pastExperiments.length})
            </button>
          </div>

          {error && (
            <div className="error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}

          {viewMode === 'current' ? (
            <>
              {/* Current Experiment */}
              {currentExperiment && (
                <div className="experiment-card current">
                  <div className="experiment-header">
                    <span className="experiment-status running">● Running</span>
                    <span className="experiment-id">{currentExperiment.id}</span>
                  </div>
                  <div className="experiment-main">
                    <h3>${currentExperiment.ticker}</h3>
                    <p className="experiment-name">{currentExperiment.name}</p>
                    <p className="experiment-hook">&quot;{currentExperiment.hook}&quot;</p>
                  </div>
                  <div className="experiment-meta">
                    <span className="meta-tag strategy">{currentExperiment.strategy}</span>
                    <span className="meta-tag style">{currentExperiment.meme_style}</span>
                  </div>
                  <div className="simulation-progress">
                    {currentExperiment.progress ? (
                      <>
                        <div className="progress-header">
                          <span>Simulating hour {currentExperiment.progress.hour}/{currentExperiment.progress.total}</span>
                          <span>{Math.round((currentExperiment.progress.hour / currentExperiment.progress.total) * 100)}%</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${(currentExperiment.progress.hour / currentExperiment.progress.total) * 100}%` }}
                          />
                        </div>
                      </>
                    ) : (
                      <div className="progress-header">
                        <span>Generating idea...</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Completed Experiments from Current Run */}
              {experiments.slice().reverse().map(exp => (
                <div key={exp.id} className="experiment-card completed">
                  <div className="experiment-header">
                    <span
                      className="experiment-status"
                      style={{ color: getOutcomeColor(exp.outcome) }}
                    >
                      {exp.outcome === 'moon' ? '🌕' :
                       exp.outcome === 'rug' ? '💣' :
                       exp.outcome === 'cult_classic' ? '⭐' :
                       exp.outcome === 'pump_and_dump' ? '📈' : '📉'}
                      {' '}{exp.outcome?.replace('_', ' ')}
                    </span>
                    <span className="experiment-score">
                      {exp.score !== null ? `${(exp.score * 100).toFixed(0)}%` : '--'}
                    </span>
                  </div>
                  <div className="experiment-main">
                    <h3>${exp.ticker}</h3>
                    <p className="experiment-name">{exp.name}</p>
                    <p className="experiment-hook">&quot;{exp.hook}&quot;</p>
                  </div>
                  <div className="experiment-meta">
                    <span className="meta-tag strategy">{exp.strategy}</span>
                    <span className="meta-tag style">{exp.meme_style}</span>
                  </div>
                </div>
              ))}

              {/* Running but no experiment yet */}
              {isRunning && !currentExperiment && experiments.length === 0 && (
                <div className="empty-feed">
                  <span className="empty-icon">⏳</span>
                  <h3>Starting Harness...</h3>
                  <p>
                    Connecting to server and initializing experiments.
                    This may take a moment.
                  </p>
                </div>
              )}

              {/* Empty State for Current Run */}
              {!isRunning && experiments.length === 0 && !currentExperiment && (
                <div className="empty-feed">
                  <span className="empty-icon">&#129514;</span>
                  <h3>No Active Run</h3>
                  <p>
                    Configure your experiment parameters and launch the harness
                    to automatically generate and test shitcoin concepts.
                  </p>
                  <p className="empty-hint">
                    The AI will brainstorm ideas, simulate CT reactions, and learn
                    what strategies work best.
                  </p>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Past Experiments History */}
              {pastExperiments.length === 0 ? (
                <div className="empty-feed">
                  <span className="empty-icon">{apiStatus === 'error' ? '⚠️' : apiStatus === 'loading' ? '⏳' : '📚'}</span>
                  <h3>{apiStatus === 'error' ? 'API Not Connected' : apiStatus === 'loading' ? 'Connecting...' : 'No Past Experiments'}</h3>
                  {apiStatus === 'error' ? (
                    <>
                      <p>Cannot reach the API server at:</p>
                      <code style={{ display: 'block', background: 'var(--bg-tertiary)', padding: '12px', borderRadius: '8px', marginTop: '12px' }}>
                        {API_URL}
                      </code>
                      <p style={{ marginTop: '16px' }}>Start the API server:</p>
                      <code style={{ display: 'block', background: 'var(--bg-tertiary)', padding: '12px', borderRadius: '8px', marginTop: '8px' }}>
                        python run_api.py
                      </code>
                    </>
                  ) : apiStatus === 'connected' ? (
                    <p>No experiments have been run yet. Launch the harness to start experimenting.</p>
                  ) : (
                    <p>Checking API connection...</p>
                  )}
                </div>
              ) : (
                <div className="experiments-table">
                  {/* Filter Controls */}
                  <div className="filter-controls" style={{
                    display: 'flex',
                    gap: '12px',
                    padding: '12px 16px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    flexWrap: 'wrap',
                    alignItems: 'center',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <label style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Outcome:</label>
                      <select
                        value={outcomeFilter}
                        onChange={e => setOutcomeFilter(e.target.value)}
                        style={{
                          padding: '6px 10px',
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          color: 'var(--text-primary)',
                          fontSize: '13px',
                        }}
                      >
                        <option value="all">All</option>
                        {uniqueOutcomes.map(o => (
                          <option key={o} value={o!}>{o?.replace('_', ' ')}</option>
                        ))}
                      </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <label style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Strategy:</label>
                      <select
                        value={strategyFilter}
                        onChange={e => setStrategyFilter(e.target.value)}
                        style={{
                          padding: '6px 10px',
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          color: 'var(--text-primary)',
                          fontSize: '13px',
                        }}
                      >
                        <option value="all">All</option>
                        {uniqueStrategies.map(s => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <label style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Sort:</label>
                      <select
                        value={sortBy}
                        onChange={e => setSortBy(e.target.value as 'score' | 'date' | 'viral')}
                        style={{
                          padding: '6px 10px',
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          color: 'var(--text-primary)',
                          fontSize: '13px',
                        }}
                      >
                        <option value="date">Date</option>
                        <option value="score">Score</option>
                        <option value="viral">Viral Coefficient</option>
                      </select>
                      <button
                        onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')}
                        style={{
                          padding: '6px 10px',
                          background: 'var(--bg-secondary)',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          color: 'var(--text-primary)',
                          fontSize: '13px',
                          cursor: 'pointer',
                        }}
                        title={sortOrder === 'desc' ? 'Descending' : 'Ascending'}
                      >
                        {sortOrder === 'desc' ? '↓' : '↑'}
                      </button>
                    </div>

                    <div style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {filteredExperiments.length} of {pastExperiments.length} experiments
                    </div>
                  </div>

                  <div className="table-header">
                    <span className="col-token">Token</span>
                    <span className="col-score">Score</span>
                    <span className="col-outcome">Outcome</span>
                    <span className="col-viral">Viral</span>
                    <span className="col-sentiment">Sentiment</span>
                    <span className="col-fud">FUD Res.</span>
                    <span className="col-strategy">Strategy</span>
                  </div>
                  {filteredExperiments.map(exp => (
                    <div key={exp.id}>
                      <div
                        className="experiment-row"
                        onClick={() => setExpandedExperiment(expandedExperiment === exp.id ? null : exp.id)}
                        style={{ cursor: 'pointer' }}
                      >
                        <div className="col-token">
                          <span className="token-ticker">${exp.ticker}</span>
                          <span className="token-name">{exp.name}</span>
                          <span className="token-id">{exp.id}</span>
                        </div>
                        <div className="col-score">
                          <span className="score-value" style={{ color: exp.score && exp.score >= 0.8 ? 'var(--success)' : exp.score && exp.score >= 0.5 ? 'var(--warning)' : 'var(--text-secondary)' }}>
                            {exp.score !== null ? `${(exp.score * 100).toFixed(0)}%` : '--'}
                          </span>
                        </div>
                        <div className="col-outcome">
                          <span className="outcome-badge" style={{ background: getOutcomeColor(exp.outcome) }}>
                            {exp.outcome === 'moon' ? '🌕 moon' :
                             exp.outcome === 'rug' ? '💣 rug' :
                             exp.outcome === 'cult_classic' ? '⭐ cult' :
                             exp.outcome === 'pump_and_dump' ? '📈 pump' :
                             exp.outcome === 'slow_bleed' ? '📉 bleed' : exp.status}
                          </span>
                        </div>
                        <div className="col-viral">
                          {exp.viral_coefficient !== null ? `${exp.viral_coefficient.toFixed(1)}x` : '--'}
                        </div>
                        <div className="col-sentiment">
                          {exp.peak_sentiment !== null ? (
                            <span style={{ color: exp.peak_sentiment > 0.5 ? 'var(--success)' : exp.peak_sentiment > 0 ? 'var(--warning)' : 'var(--danger)' }}>
                              {exp.peak_sentiment > 0 ? '+' : ''}{(exp.peak_sentiment * 100).toFixed(0)}%
                            </span>
                          ) : '--'}
                        </div>
                        <div className="col-fud">
                          {exp.fud_resistance !== null ? `${(exp.fud_resistance * 100).toFixed(0)}%` : '--'}
                        </div>
                        <div className="col-strategy">
                          <span className="strategy-tag">{exp.strategy}</span>
                          <span className="style-tag">{exp.meme_style}</span>
                        </div>
                      </div>

                      {/* Expanded Details Panel */}
                      {expandedExperiment === exp.id && (
                        <div style={{
                          padding: '16px',
                          background: 'var(--bg-tertiary)',
                          borderBottom: '1px solid var(--border)',
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr',
                          gap: '16px',
                        }}>
                          {/* Left: Hook & Reasoning */}
                          <div>
                            <div style={{ marginBottom: '12px' }}>
                              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Hook</div>
                              <div style={{ fontSize: '14px', fontStyle: 'italic' }}>&quot;{exp.hook}&quot;</div>
                            </div>
                            {exp.reasoning && (
                              <div style={{ marginBottom: '12px' }}>
                                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Strategy Reasoning</div>
                                <div style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{exp.reasoning}</div>
                              </div>
                            )}
                            {exp.confidence !== null && (
                              <div>
                                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '4px' }}>Idea Confidence</div>
                                <div style={{ fontSize: '14px', fontWeight: 600, color: exp.confidence > 0.7 ? 'var(--success)' : exp.confidence > 0.4 ? 'var(--warning)' : 'var(--text-secondary)' }}>
                                  {(exp.confidence * 100).toFixed(0)}%
                                </div>
                              </div>
                            )}
                          </div>

                          {/* Right: Risk Factors */}
                          <div>
                            {exp.risk_factors && exp.risk_factors.length > 0 && (
                              <div>
                                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>Risk Factors</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                  {exp.risk_factors.map((risk, i) => (
                                    <span
                                      key={i}
                                      style={{
                                        padding: '4px 10px',
                                        background: 'rgba(244, 33, 46, 0.15)',
                                        color: 'var(--danger)',
                                        borderRadius: '12px',
                                        fontSize: '12px',
                                        fontWeight: 500,
                                      }}
                                    >
                                      {risk}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {(!exp.risk_factors || exp.risk_factors.length === 0) && (
                              <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                                No risk factors identified
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </main>
      </div>

      {/* Mobile Navigation */}
      <MobileNav
        isConnected={auth.isConnected}
        balance={wallet.balance}
        configPanel={null}
      />
    </div>
  )
}
