'use client'

import { useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Tweet {
  id: string
  author_name: string
  author_handle: string
  author_type: string
  content: string
  hour: number
  likes: number
  retweets: number
  replies: number
  sentiment: number
}

interface SimulationResult {
  tweets: Tweet[]
  viral_coefficient: number
  peak_sentiment: number
  sentiment_stability: number
  fud_resistance: number
  total_mentions: number
  total_engagement: number
  influencer_pickups: number
  hours_to_peak: number
  hours_to_death: number | null
  dominant_narrative: string
  top_fud_points: string[]
  predicted_outcome: string
  confidence: number
}

interface TokenConfig {
  name: string
  ticker: string
  narrative: string
  tagline: string
  meme_style: string
  market_condition: string
}

export default function Home() {
  const [config, setConfig] = useState<TokenConfig>({
    name: '',
    ticker: '',
    narrative: '',
    tagline: '',
    meme_style: 'absurd',
    market_condition: 'crab'
  })
  const [isRunning, setIsRunning] = useState(false)
  const [tweets, setTweets] = useState<Tweet[]>([])
  const [result, setResult] = useState<Omit<SimulationResult, 'tweets'> | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [useTwitterPriors, setUseTwitterPriors] = useState(false)

  const runSimulation = async () => {
    setIsRunning(true)
    setTweets([])
    setResult(null)
    setError(null)

    try {
      const response = await fetch(`${API_URL}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          token: {
            name: config.name || config.ticker,
            ticker: config.ticker,
            narrative: config.narrative || 'A new memecoin',
            tagline: config.tagline || null,
            meme_style: config.meme_style,
            market_condition: config.market_condition,
          },
          hours: 48,
          use_twitter_priors: useTwitterPriors,
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Simulation failed')
      }

      const data: SimulationResult = await response.json()

      // Animate tweets appearing
      for (let i = 0; i < data.tweets.length; i++) {
        await new Promise(r => setTimeout(r, 150))
        setTweets(prev => [...prev, data.tweets[i]])
      }

      // Show results
      const { tweets: _, ...resultWithoutTweets } = data
      setResult(resultWithoutTweets)

    } catch (err) {
      console.error('Simulation error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsRunning(false)
    }
  }

  const formatNumber = (n: number) => {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
    return n.toString()
  }

  const getAvatarInitial = (name: string) => name[0]?.toUpperCase() || '?'

  const getAvatarColor = (type: string) => {
    const colors: Record<string, string> = {
      kol: 'linear-gradient(135deg, #9333ea, #ec4899)',
      degen: 'linear-gradient(135deg, #f97316, #eab308)',
      skeptic: 'linear-gradient(135deg, #ef4444, #dc2626)',
      whale: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
      influencer: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
      normie: 'linear-gradient(135deg, #6b7280, #4b5563)',
      bot: 'linear-gradient(135deg, #10b981, #059669)',
    }
    return colors[type] || 'linear-gradient(135deg, var(--accent), #9333ea)'
  }

  return (
    <div className="container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">ShitcoinSim</div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Test your token on simulated CT before launch
        </p>
        <div style={{ marginTop: '20px', padding: '12px', background: 'var(--bg-secondary)', borderRadius: '12px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>API Status</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }} />
            <span style={{ fontSize: '14px' }}>Connected</span>
          </div>
        </div>
      </aside>

      {/* Main Feed */}
      <main className="main-feed">
        <div className="feed-header">
          Simulation Feed
          {config.ticker && <span style={{ color: 'var(--accent)' }}> - ${config.ticker.toUpperCase()}</span>}
        </div>

        {error && (
          <div style={{ padding: '16px', background: 'rgba(244, 33, 46, 0.1)', borderBottom: '1px solid var(--danger)' }}>
            <strong style={{ color: 'var(--danger)' }}>Error:</strong> {error}
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Make sure the API server is running: <code>python run_api.py</code>
            </div>
          </div>
        )}

        {tweets.length === 0 && !isRunning && !error ? (
          <div className="empty-state">
            <h3>No simulation running</h3>
            <p>Configure your token and hit simulate to see how CT reacts</p>
          </div>
        ) : (
          <>
            {tweets.map(tweet => (
              <div key={tweet.id} className="tweet">
                <div className="avatar" style={{ background: getAvatarColor(tweet.author_type) }}>
                  {getAvatarInitial(tweet.author_name)}
                </div>
                <div className="tweet-content">
                  <div className="tweet-header">
                    <span className="tweet-name">{tweet.author_name}</span>
                    <span className="tweet-handle">@{tweet.author_handle}</span>
                    <span className="tweet-time">· {tweet.hour}h</span>
                    <span style={{
                      marginLeft: '8px',
                      fontSize: '11px',
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: 'var(--bg-tertiary)',
                      color: 'var(--text-secondary)'
                    }}>
                      {tweet.author_type}
                    </span>
                  </div>
                  <div className="tweet-text">{tweet.content}</div>
                  <div className="sentiment-bar">
                    <div
                      className={`sentiment-fill ${tweet.sentiment >= 0 ? 'positive' : 'negative'}`}
                      style={{ width: `${Math.abs(tweet.sentiment) * 100}%` }}
                    />
                  </div>
                  <div className="tweet-actions">
                    <span className="tweet-action">replies {tweet.replies}</span>
                    <span className="tweet-action">retweets {tweet.retweets}</span>
                    <span className="tweet-action">likes {tweet.likes}</span>
                  </div>
                </div>
              </div>
            ))}
            {isRunning && (
              <div className="loading">
                <div className="spinner" />
                Simulating CT reactions...
              </div>
            )}
          </>
        )}
      </main>

      {/* Config Panel */}
      <aside className="config-panel">
        <div className="config-title">Token Config</div>

        <div className="form-group">
          <label className="form-label">Token Name</label>
          <input
            type="text"
            className="form-input"
            placeholder="DogeKiller9000"
            value={config.name}
            onChange={e => setConfig({ ...config, name: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Ticker *</label>
          <input
            type="text"
            className="form-input"
            placeholder="DK9000"
            value={config.ticker}
            onChange={e => setConfig({ ...config, ticker: e.target.value.toUpperCase() })}
            maxLength={10}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Narrative *</label>
          <input
            type="text"
            className="form-input"
            placeholder="AI meme that roasts other memes"
            value={config.narrative}
            onChange={e => setConfig({ ...config, narrative: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Tagline</label>
          <input
            type="text"
            className="form-input"
            placeholder="To the moon and beyond"
            value={config.tagline}
            onChange={e => setConfig({ ...config, tagline: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label className="form-label">Meme Style</label>
          <select
            className="form-select"
            value={config.meme_style}
            onChange={e => setConfig({ ...config, meme_style: e.target.value })}
          >
            <option value="cute">Cute (doge, cats)</option>
            <option value="edgy">Edgy (dark humor)</option>
            <option value="absurd">Absurd (surreal)</option>
            <option value="topical">Topical (trending)</option>
            <option value="nostalgic">Nostalgic (retro)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Market Condition</label>
          <select
            className="form-select"
            value={config.market_condition}
            onChange={e => setConfig({ ...config, market_condition: e.target.value })}
          >
            <option value="bear">Bear Market</option>
            <option value="crab">Crab Market</option>
            <option value="bull">Bull Market</option>
            <option value="euphoria">Euphoria</option>
          </select>
        </div>

        <div className="form-group">
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={useTwitterPriors}
              onChange={e => setUseTwitterPriors(e.target.checked)}
              style={{ width: '16px', height: '16px' }}
            />
            <span className="form-label" style={{ margin: 0 }}>Use real Twitter data</span>
          </label>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Calibrate with live CT sentiment (requires API key)
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={runSimulation}
          disabled={isRunning || !config.ticker || !config.narrative}
        >
          {isRunning ? 'Simulating...' : 'Run Simulation'}
        </button>

        {/* Results */}
        {result && (
          <div className="results-card">
            <div className="results-title">Results</div>

            <div className="result-row">
              <span className="result-label">Viral Score</span>
              <span className={`result-value ${result.viral_coefficient > 1 ? 'positive' : 'negative'}`}>
                {result.viral_coefficient.toFixed(2)}x
              </span>
            </div>

            <div className="result-row">
              <span className="result-label">Peak Sentiment</span>
              <span className={`result-value ${result.peak_sentiment > 0 ? 'positive' : 'negative'}`}>
                {result.peak_sentiment > 0 ? '+' : ''}{result.peak_sentiment.toFixed(2)}
              </span>
            </div>

            <div className="result-row">
              <span className="result-label">FUD Resistance</span>
              <span className={`result-value ${result.fud_resistance > 0.5 ? 'positive' : 'neutral'}`}>
                {(result.fud_resistance * 100).toFixed(0)}%
              </span>
            </div>

            <div className="result-row">
              <span className="result-label">Total Engagement</span>
              <span className="result-value">{formatNumber(result.total_engagement)}</span>
            </div>

            <div className="result-row">
              <span className="result-label">KOL Pickups</span>
              <span className="result-value">{result.influencer_pickups}</span>
            </div>

            <div className="result-row">
              <span className="result-label">Peak Hour</span>
              <span className="result-value">Hour {result.hours_to_peak}</span>
            </div>

            <div style={{ marginTop: '16px', textAlign: 'center' }}>
              <span className={`prediction-badge ${result.predicted_outcome}`}>
                {result.predicted_outcome.replace('_', ' ')}
              </span>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {(result.confidence * 100).toFixed(0)}% confidence
              </div>
            </div>

            <div style={{ marginTop: '16px' }}>
              <div className="result-label">CT Verdict</div>
              <div style={{ fontStyle: 'italic', marginTop: '4px' }}>&quot;{result.dominant_narrative}&quot;</div>
            </div>

            {result.top_fud_points.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <div className="result-label">Top FUD Points</div>
                <ul style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px', paddingLeft: '16px' }}>
                  {result.top_fud_points.slice(0, 3).map((fud, i) => (
                    <li key={i} style={{ marginBottom: '4px' }}>{fud}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </aside>
    </div>
  )
}
