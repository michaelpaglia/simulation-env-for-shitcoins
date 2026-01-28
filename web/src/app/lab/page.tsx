'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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

export default function Lab() {
  const [config, setConfig] = useState<HarnessConfig>({
    mode: 'balanced',
    max_experiments: 5,
    simulation_hours: 24,
    market_condition: 'crab',
    target_theme: '',
  })

  const [isRunning, setIsRunning] = useState(false)
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [currentExperiment, setCurrentExperiment] = useState<Experiment | null>(null)
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])
  const [runProgress, setRunProgress] = useState<{ completed: number; total: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [insights, setInsights] = useState<string[]>([])

  const eventSourceRef = useRef<AbortController | null>(null)

  // Load initial leaderboard
  useEffect(() => {
    fetchLeaderboard()
    fetchLearnings()
  }, [])

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

  const startHarness = async () => {
    setIsRunning(true)
    setExperiments([])
    setCurrentExperiment(null)
    setError(null)
    setRunProgress(null)

    try {
      // Start the harness run
      const startRes = await fetch(`${API_URL}/harness/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      })

      if (!startRes.ok) {
        const err = await startRes.json()
        throw new Error(err.detail || 'Failed to start harness')
      }

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
              handleHarnessEvent(event)

              if (event.type === 'done' || event.type === 'run_completed') {
                setIsRunning(false)
                fetchLeaderboard()
                fetchLearnings()
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
        setError(err instanceof Error ? err.message : 'Unknown error')
      }
    } finally {
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
        const completedExp: Experiment = {
          id: event.experiment_id as string,
          ticker: currentExperiment?.ticker || 'UNK',
          name: currentExperiment?.name || 'Unknown',
          strategy: currentExperiment?.strategy || '',
          meme_style: currentExperiment?.meme_style || '',
          hook: currentExperiment?.hook || '',
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
      {/* Header */}
      <header className="lab-header">
        <div className="lab-header-left">
          <span className="lab-logo">&#129514;</span>
          <h1>Harness Lab</h1>
          <span className="lab-badge">Autonomous Testing</span>
        </div>
        <Link href="/" className="nav-link">
          <HomeIcon />
          <span>Single Sim</span>
        </Link>
      </header>

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
                value={config.mode}
                onChange={e => setConfig({ ...config, mode: e.target.value })}
                disabled={isRunning}
              >
                <option value="balanced">Balanced (Explore + Exploit)</option>
                <option value="explore">Explore (Maximize Learning)</option>
                <option value="exploit">Exploit (Focus on Winners)</option>
                <option value="targeted">Targeted (Specific Theme)</option>
              </select>
            </div>

            {config.mode === 'targeted' && (
              <div className="control-group">
                <label>Target Theme</label>
                <input
                  type="text"
                  placeholder="e.g., AI cats, nostalgic memes"
                  value={config.target_theme}
                  onChange={e => setConfig({ ...config, target_theme: e.target.value })}
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
                value={config.max_experiments}
                onChange={e => setConfig({ ...config, max_experiments: parseInt(e.target.value) || 5 })}
                disabled={isRunning}
              />
            </div>

            <div className="control-group">
              <label>Hours per Simulation</label>
              <select
                value={config.simulation_hours}
                onChange={e => setConfig({ ...config, simulation_hours: parseInt(e.target.value) })}
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
                value={config.market_condition}
                onChange={e => setConfig({ ...config, market_condition: e.target.value })}
                disabled={isRunning}
              >
                <option value="bear">Bear Market</option>
                <option value="crab">Crab Market</option>
                <option value="bull">Bull Market</option>
                <option value="euphoria">Euphoria</option>
              </select>
            </div>

            {!isRunning ? (
              <button className="launch-btn" onClick={startHarness}>
                &#128640; Launch Harness
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
          {error && (
            <div className="error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Current Experiment */}
          {currentExperiment && (
            <div className="experiment-card current">
              <div className="experiment-header">
                <span className="experiment-status running">&#9679; Running</span>
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
              <div className="experiment-loading">
                <div className="spinner" />
                <span>Simulating CT reactions...</span>
              </div>
            </div>
          )}

          {/* Completed Experiments */}
          {experiments.slice().reverse().map(exp => (
            <div key={exp.id} className="experiment-card completed">
              <div className="experiment-header">
                <span
                  className="experiment-status"
                  style={{ color: getOutcomeColor(exp.outcome) }}
                >
                  {exp.outcome === 'moon' ? '&#127773;' :
                   exp.outcome === 'rug' ? '&#128163;' :
                   exp.outcome === 'cult_classic' ? '&#11088;' :
                   exp.outcome === 'pump_and_dump' ? '&#128200;' : '&#128201;'}
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

          {/* Empty State */}
          {!isRunning && experiments.length === 0 && !currentExperiment && (
            <div className="empty-feed">
              <span className="empty-icon">&#129514;</span>
              <h3>Harness Lab</h3>
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
        </main>
      </div>

      <style jsx>{`
        .lab-container {
          min-height: 100vh;
          background: var(--bg-primary);
          color: var(--text-primary);
        }

        .lab-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          border-bottom: 1px solid var(--border);
          background: rgba(0, 0, 0, 0.8);
          backdrop-filter: blur(12px);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .lab-header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .lab-logo {
          font-size: 28px;
        }

        .lab-header h1 {
          font-size: 20px;
          font-weight: 700;
          margin: 0;
        }

        .lab-badge {
          font-size: 11px;
          padding: 4px 8px;
          background: var(--bg-tertiary);
          border-radius: 4px;
          color: var(--text-secondary);
        }

        .nav-link {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          background: var(--bg-secondary);
          border-radius: 9999px;
          color: var(--text-primary);
          text-decoration: none;
          font-size: 14px;
          transition: background 0.2s;
        }

        .nav-link:hover {
          background: var(--bg-tertiary);
        }

        .lab-content {
          display: grid;
          grid-template-columns: 320px 1fr;
          max-width: 1200px;
          margin: 0 auto;
          gap: 24px;
          padding: 24px;
        }

        .lab-controls {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .control-card {
          background: var(--bg-secondary);
          border-radius: 16px;
          overflow: hidden;
        }

        .control-card-header {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 16px;
          font-weight: 700;
          border-bottom: 1px solid var(--border);
        }

        .control-group {
          padding: 12px 16px;
        }

        .control-group label {
          display: block;
          font-size: 13px;
          color: var(--text-secondary);
          margin-bottom: 6px;
        }

        .control-group select,
        .control-group input {
          width: 100%;
          padding: 10px 12px;
          background: var(--bg-primary);
          border: 1px solid var(--border);
          border-radius: 8px;
          color: var(--text-primary);
          font-size: 14px;
        }

        .control-group select:disabled,
        .control-group input:disabled {
          opacity: 0.5;
        }

        .launch-btn, .stop-btn {
          width: calc(100% - 32px);
          margin: 16px;
          padding: 14px;
          border: none;
          border-radius: 9999px;
          font-size: 15px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.2s;
        }

        .launch-btn {
          background: var(--accent);
          color: white;
        }

        .launch-btn:hover {
          background: var(--accent-hover);
        }

        .stop-btn {
          background: var(--danger);
          color: white;
        }

        .run-progress {
          padding: 0 16px 16px;
        }

        .progress-text {
          font-size: 13px;
          color: var(--text-secondary);
          margin-bottom: 8px;
        }

        .progress-bar {
          height: 6px;
          background: var(--bg-tertiary);
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: var(--accent);
          border-radius: 3px;
          transition: width 0.3s;
        }

        .leaderboard {
          padding: 8px;
        }

        .empty-leaderboard {
          padding: 24px;
          text-align: center;
          color: var(--text-secondary);
          font-size: 14px;
        }

        .leaderboard-entry {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .leaderboard-entry:hover {
          background: var(--bg-tertiary);
        }

        .rank {
          font-weight: 700;
          color: var(--text-secondary);
          width: 28px;
        }

        .entry-info {
          flex: 1;
          display: flex;
          justify-content: space-between;
        }

        .ticker {
          font-weight: 700;
        }

        .score {
          color: var(--success);
          font-weight: 600;
        }

        .outcome-badge {
          font-size: 11px;
          padding: 3px 8px;
          border-radius: 4px;
          color: white;
          text-transform: uppercase;
        }

        .insights-list {
          padding: 12px 16px;
        }

        .insight-item {
          font-size: 13px;
          color: var(--text-secondary);
          padding: 8px 0;
          border-bottom: 1px solid var(--border);
        }

        .insight-item:last-child {
          border-bottom: none;
        }

        .lab-feed {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .error-banner {
          padding: 16px;
          background: rgba(244, 33, 46, 0.1);
          border: 1px solid var(--danger);
          border-radius: 12px;
          color: var(--danger);
        }

        .experiment-card {
          background: var(--bg-secondary);
          border-radius: 16px;
          padding: 20px;
          border: 1px solid var(--border);
        }

        .experiment-card.current {
          border-color: var(--accent);
          box-shadow: 0 0 20px rgba(29, 155, 240, 0.2);
        }

        .experiment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .experiment-status {
          font-size: 13px;
          font-weight: 600;
        }

        .experiment-status.running {
          color: var(--accent);
        }

        .experiment-id {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .experiment-score {
          font-size: 20px;
          font-weight: 700;
          color: var(--success);
        }

        .experiment-main h3 {
          font-size: 24px;
          font-weight: 700;
          margin: 0 0 4px;
        }

        .experiment-name {
          font-size: 16px;
          color: var(--text-secondary);
          margin: 0 0 8px;
        }

        .experiment-hook {
          font-style: italic;
          color: var(--text-secondary);
          margin: 0;
          font-size: 14px;
        }

        .experiment-meta {
          display: flex;
          gap: 8px;
          margin-top: 16px;
        }

        .meta-tag {
          font-size: 12px;
          padding: 4px 10px;
          border-radius: 4px;
          background: var(--bg-tertiary);
          color: var(--text-secondary);
        }

        .meta-tag.strategy {
          background: rgba(29, 155, 240, 0.15);
          color: var(--accent);
        }

        .experiment-loading {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid var(--border);
          color: var(--text-secondary);
          font-size: 14px;
        }

        .spinner {
          width: 18px;
          height: 18px;
          border: 2px solid var(--border);
          border-top-color: var(--accent);
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .empty-feed {
          text-align: center;
          padding: 60px 40px;
          background: var(--bg-secondary);
          border-radius: 16px;
        }

        .empty-icon {
          font-size: 48px;
          display: block;
          margin-bottom: 16px;
        }

        .empty-feed h3 {
          font-size: 24px;
          margin: 0 0 12px;
        }

        .empty-feed p {
          color: var(--text-secondary);
          margin: 0 0 8px;
          max-width: 400px;
          margin-left: auto;
          margin-right: auto;
        }

        .empty-hint {
          font-size: 13px;
        }

        @media (max-width: 900px) {
          .lab-content {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  )
}
