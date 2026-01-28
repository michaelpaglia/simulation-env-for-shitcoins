'use client'

import { useState } from 'react'

interface Tweet {
  id: string
  author: {
    name: string
    handle: string
    type: string
  }
  content: string
  hour: number
  likes: number
  retweets: number
  replies: number
  sentiment: number
}

interface SimulationResult {
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

const MOCK_TWEETS: Tweet[] = [
  {
    id: '1',
    author: { name: 'ansem', handle: 'blknoiz06', type: 'kol' },
    content: 'interesting ticker. watching.',
    hour: 1,
    likes: 2847,
    retweets: 412,
    replies: 89,
    sentiment: 0.4
  },
  {
    id: '2',
    author: { name: 'DegenSpartan', handle: 'degen_spartan_ii', type: 'degen' },
    content: 'ser I aped a smol bag into $EXAMPLE, the narrative is too good to pass. LFG wagmi 🚀',
    hour: 2,
    likes: 342,
    retweets: 67,
    replies: 23,
    sentiment: 0.8
  },
  {
    id: '3',
    author: { name: 'CryptoSkeptic', handle: 'NotYourLiquidity', type: 'skeptic' },
    content: '$EXAMPLE - anon team, unlocked LP, copied website. Classic rug setup. DYOR or become exit liquidity.',
    hour: 3,
    likes: 567,
    retweets: 234,
    replies: 156,
    sentiment: -0.7
  },
  {
    id: '4',
    author: { name: 'LilMoonLambo', handle: 'LilMoonLambo', type: 'kol' },
    content: 'YOOO $EXAMPLE is SENDING!! This narrative is hitting different. Dont fade this one CT 🔥🔥',
    hour: 4,
    likes: 1893,
    retweets: 445,
    replies: 234,
    sentiment: 0.9
  },
]

const MOCK_RESULT: SimulationResult = {
  viral_coefficient: 1.47,
  peak_sentiment: 0.72,
  sentiment_stability: 0.65,
  fud_resistance: 0.58,
  total_mentions: 847,
  total_engagement: 23456,
  influencer_pickups: 4,
  hours_to_peak: 8,
  hours_to_death: null,
  dominant_narrative: 'Hidden gem with strong community',
  top_fud_points: ['Anon team concerns', 'Low initial liquidity', 'Similar to recent rugs'],
  predicted_outcome: 'cult_classic',
  confidence: 0.62
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
  const [result, setResult] = useState<SimulationResult | null>(null)

  const runSimulation = async () => {
    setIsRunning(true)
    setTweets([])
    setResult(null)

    // Simulate tweets appearing over time
    for (let i = 0; i < MOCK_TWEETS.length; i++) {
      await new Promise(r => setTimeout(r, 800))
      setTweets(prev => [...prev, {
        ...MOCK_TWEETS[i],
        content: MOCK_TWEETS[i].content.replace(/\$EXAMPLE/g, `$${config.ticker.toUpperCase() || 'TOKEN'}`)
      }])
    }

    await new Promise(r => setTimeout(r, 500))
    setResult(MOCK_RESULT)
    setIsRunning(false)
  }

  const formatNumber = (n: number) => {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
    return n.toString()
  }

  const getAvatarInitial = (name: string) => name[0]?.toUpperCase() || '?'

  return (
    <div className="container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">ShitcoinSim</div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
          Test your token on simulated CT before launch
        </p>
      </aside>

      {/* Main Feed */}
      <main className="main-feed">
        <div className="feed-header">
          Simulation Feed
          {config.ticker && <span style={{ color: 'var(--accent)' }}> - ${config.ticker.toUpperCase()}</span>}
        </div>

        {tweets.length === 0 && !isRunning ? (
          <div className="empty-state">
            <h3>No simulation running</h3>
            <p>Configure your token and hit simulate to see how CT reacts</p>
          </div>
        ) : (
          <>
            {tweets.map(tweet => (
              <div key={tweet.id} className="tweet">
                <div className="avatar">{getAvatarInitial(tweet.author.name)}</div>
                <div className="tweet-content">
                  <div className="tweet-header">
                    <span className="tweet-name">{tweet.author.name}</span>
                    <span className="tweet-handle">@{tweet.author.handle}</span>
                    <span className="tweet-time">· {tweet.hour}h</span>
                  </div>
                  <div className="tweet-text">{tweet.content}</div>
                  <div className="sentiment-bar">
                    <div
                      className={`sentiment-fill ${tweet.sentiment >= 0 ? 'positive' : 'negative'}`}
                      style={{ width: `${Math.abs(tweet.sentiment) * 100}%` }}
                    />
                  </div>
                  <div className="tweet-actions">
                    <span className="tweet-action">💬 {tweet.replies}</span>
                    <span className="tweet-action">🔁 {tweet.retweets}</span>
                    <span className="tweet-action">❤️ {tweet.likes}</span>
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
          <label className="form-label">Ticker</label>
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
          <label className="form-label">Narrative</label>
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

        <button
          className="btn btn-primary"
          onClick={runSimulation}
          disabled={isRunning || !config.ticker}
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
              <div style={{ fontStyle: 'italic', marginTop: '4px' }}>"{result.dominant_narrative}"</div>
            </div>
          </div>
        )}
      </aside>
    </div>
  )
}
