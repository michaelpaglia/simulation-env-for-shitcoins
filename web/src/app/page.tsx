'use client'

import { useState } from 'react'
import Link from 'next/link'

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

// SVG Icons
const XLogo = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
)

const HomeIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M21.591 7.146L12.52 1.157c-.316-.21-.724-.21-1.04 0l-9.071 5.99c-.26.173-.409.456-.409.757v13.183c0 .502.418.913.929.913h6.638c.511 0 .929-.41.929-.913v-7.075h3.008v7.075c0 .502.418.913.929.913h6.638c.511 0 .929-.41.929-.913V7.904c0-.301-.158-.584-.418-.758z" />
  </svg>
)

const SearchIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M10.25 3.75c-3.59 0-6.5 2.91-6.5 6.5s2.91 6.5 6.5 6.5c1.795 0 3.419-.726 4.596-1.904 1.178-1.177 1.904-2.801 1.904-4.596 0-3.59-2.91-6.5-6.5-6.5zm-8.5 6.5c0-4.694 3.806-8.5 8.5-8.5s8.5 3.806 8.5 8.5c0 1.986-.682 3.815-1.824 5.262l4.781 4.781-1.414 1.414-4.781-4.781c-1.447 1.142-3.276 1.824-5.262 1.824-4.694 0-8.5-3.806-8.5-8.5z" />
  </svg>
)

const BellIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M19.993 9.042C19.48 5.017 16.054 2 11.996 2s-7.49 3.021-7.999 7.051L2.866 18H7.1c.463 2.282 2.481 4 4.9 4s4.437-1.718 4.9-4h4.236l-1.143-8.958zM12 20c-1.306 0-2.417-.835-2.829-2h5.658c-.412 1.165-1.523 2-2.829 2zm-6.866-4l.847-6.698C6.364 6.272 8.941 4 11.996 4s5.627 2.268 6.013 5.295L18.864 16H5.134z" />
  </svg>
)

const MessageIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M1.998 5.5c0-1.381 1.119-2.5 2.5-2.5h15c1.381 0 2.5 1.119 2.5 2.5v13c0 1.381-1.119 2.5-2.5 2.5h-15c-1.381 0-2.5-1.119-2.5-2.5v-13zm2.5-.5c-.276 0-.5.224-.5.5v2.764l8 3.638 8-3.636V5.5c0-.276-.224-.5-.5-.5h-15zm15.5 5.463l-8 3.636-8-3.638V18.5c0 .276.224.5.5.5h15c.276 0 .5-.224.5-.5v-8.037z" />
  </svg>
)

const VerifiedBadge = ({ gold = false }: { gold?: boolean }) => (
  <svg viewBox="0 0 22 22" className={`verified-badge ${gold ? 'gold' : ''}`}>
    <path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z" />
  </svg>
)

const ReplyIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M1.751 10c0-4.42 3.584-8 8.005-8h4.366c4.49 0 8.129 3.64 8.129 8.13 0 2.96-1.607 5.68-4.196 7.11l-8.054 4.46v-3.69h-.067c-4.49.1-8.183-3.51-8.183-8.01zm8.005-6c-3.317 0-6.005 2.69-6.005 6 0 3.37 2.77 6.08 6.138 6.01l.351-.01h1.761v2.3l5.087-2.81c1.951-1.08 3.163-3.13 3.163-5.36 0-3.39-2.744-6.13-6.129-6.13H9.756z" />
  </svg>
)

const RepostIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M4.5 3.88l4.432 4.14-1.364 1.46L5.5 7.55V16c0 1.1.896 2 2 2H13v2H7.5c-2.209 0-4-1.79-4-4V7.55L1.432 9.48.068 8.02 4.5 3.88zM16.5 6H11V4h5.5c2.209 0 4 1.79 4 4v8.45l2.068-1.93 1.364 1.46-4.432 4.14-4.432-4.14 1.364-1.46 2.068 1.93V8c0-1.1-.896-2-2-2z" />
  </svg>
)

const LikeIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M16.697 5.5c-1.222-.06-2.679.51-3.89 2.16l-.805 1.09-.806-1.09C9.984 6.01 8.526 5.44 7.304 5.5c-1.243.07-2.349.78-2.91 1.91-.552 1.12-.633 2.78.479 4.82 1.074 1.97 3.257 4.27 7.129 6.61 3.87-2.34 6.052-4.64 7.126-6.61 1.111-2.04 1.03-3.7.477-4.82-.561-1.13-1.666-1.84-2.908-1.91zm4.187 7.69c-1.351 2.48-4.001 5.12-8.379 7.67l-.503.3-.504-.3c-4.379-2.55-7.029-5.19-8.382-7.67-1.36-2.5-1.41-4.86-.514-6.67.887-1.79 2.647-2.91 4.601-3.01 1.651-.09 3.368.56 4.798 2.01 1.429-1.45 3.146-2.1 4.796-2.01 1.954.1 3.714 1.22 4.601 3.01.896 1.81.846 4.17-.514 6.67z" />
  </svg>
)

const ViewsIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M8.75 21V3h2v18h-2zM18 21V8.5h2V21h-2zM4 21l.004-10h2L6 21H4zm9.248 0v-7h2v7h-2z" />
  </svg>
)

const BookmarkIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M4 4.5C4 3.12 5.119 2 6.5 2h11C18.881 2 20 3.12 20 4.5v18.44l-8-5.71-8 5.71V4.5zM6.5 4c-.276 0-.5.22-.5.5v14.56l6-4.29 6 4.29V4.5c0-.28-.224-.5-.5-.5h-11z" />
  </svg>
)

const ShareIcon = () => (
  <svg viewBox="0 0 24 24">
    <path d="M12 2.59l5.7 5.7-1.41 1.42L13 6.41V16h-2V6.41l-3.3 3.3-1.41-1.42L12 2.59zM21 15l-.02 3.51c0 1.38-1.12 2.49-2.5 2.49H5.5C4.11 21 3 19.88 3 18.5V15h2v3.5c0 .28.22.5.5.5h12.98c.28 0 .5-.22.5-.5L19 15h2z" />
  </svg>
)

const FeatherIcon = () => (
  <svg viewBox="0 0 24 24" width="24" height="24">
    <path d="M23 3c-6.62-.1-10.38 2.421-13.05 6.03C7.29 12.61 6 17.331 6 22h2c0-1.007.07-2.012.19-3H12c4.1 0 7.48-3.082 7.94-7.054C22.79 10.147 23.17 6.359 23 3zm-7 8h-1.5v2H16c.63-.016 1.2-.08 1.72-.188C16.95 15.24 14.68 17 12 17H8.55c.57-2.512 1.57-4.851 3-6.78 2.16-2.912 5.29-4.911 9.45-5.187C20.95 8.079 19.9 11 16 11zM4 9V6H1V4h3V1h2v3h3v2H6v3H4z" fill="currentColor" />
  </svg>
)

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
  const [activeTab, setActiveTab] = useState<'foryou' | 'following'>('foryou')
  const [progress, setProgress] = useState<{ hour: number; total: number; momentum: number } | null>(null)

  const runSimulation = async () => {
    setIsRunning(true)
    setTweets([])
    setResult(null)
    setError(null)
    setProgress(null)

    try {
      const response = await fetch(`${API_URL}/simulate/stream`, {
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

      // Read the SSE stream
      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response body')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'tweet') {
                setTweets(prev => [...prev, data.tweet])
              } else if (data.type === 'progress') {
                setProgress({
                  hour: data.hour,
                  total: data.total_hours,
                  momentum: data.momentum,
                })
              } else if (data.type === 'result') {
                setResult(data.result)
              } else if (data.type === 'error') {
                throw new Error(data.message)
              }
            } catch {
              // Ignore parse errors for incomplete JSON
            }
          }
        }
      }

    } catch (err) {
      console.error('Simulation error:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setIsRunning(false)
      setProgress(null)
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
      kol: 'linear-gradient(135deg, #1d9bf0, #1a8cd8)',
      degen: 'linear-gradient(135deg, #f91880, #e2177a)',
      skeptic: 'linear-gradient(135deg, #f4212e, #dc1d28)',
      whale: 'linear-gradient(135deg, #ffd400, #e5be00)',
      influencer: 'linear-gradient(135deg, #7856ff, #6644ee)',
      normie: 'linear-gradient(135deg, #71767b, #555b5f)',
      bot: 'linear-gradient(135deg, #00ba7c, #00a76f)',
    }
    return colors[type] || 'linear-gradient(135deg, #1d9bf0, #9333ea)'
  }

  const isVerified = (type: string) => ['kol', 'influencer', 'whale'].includes(type)
  const isGoldVerified = (type: string) => type === 'whale'

  return (
    <div className="container">
      {/* Left Sidebar */}
      <aside className="sidebar">
        <div className="logo" title="Hopium Lab">
          <span style={{ fontSize: '28px' }}>&#129514;</span>
        </div>
        <nav className="nav-items">
          <div className="nav-item active">
            <HomeIcon />
            <span>Home</span>
          </div>
          <div className="nav-item">
            <SearchIcon />
            <span>Explore</span>
          </div>
          <div className="nav-item">
            <BellIcon />
            <span>Notifications</span>
          </div>
          <div className="nav-item">
            <MessageIcon />
            <span>Messages</span>
          </div>
          <Link href="/lab" className="nav-item" style={{ textDecoration: 'none', color: 'inherit' }}>
            <svg viewBox="0 0 24 24" width="26" height="26" fill="currentColor">
              <path d="M9 3v8.5L5 18h14l-4-6.5V3H9zm-1-2h8a1 1 0 011 1v8.5l4 6.5a2 2 0 01-1.7 3H4.7A2 2 0 013 18l4-6.5V2a1 1 0 011-1z"/>
            </svg>
            <span>Harness Lab</span>
          </Link>
        </nav>
        <button className="post-btn" title="You can't actually post, this is fake">
          <span>Shill</span>
          <FeatherIcon />
        </button>
      </aside>

      {/* Main Feed */}
      <main className="main-feed">
        <div className="feed-header">
          <div className="feed-title">&#129489;&#8205;&#128300; The Lab</div>
          <div className="feed-tabs">
            <div
              className={`feed-tab ${activeTab === 'foryou' ? 'active' : ''}`}
              onClick={() => setActiveTab('foryou')}
            >
              For You (Allegedly)
            </div>
            <div
              className={`feed-tab ${activeTab === 'following' ? 'active' : ''}`}
              onClick={() => setActiveTab('following')}
            >
              Following (lol)
            </div>
          </div>
        </div>

        {error && (
          <div style={{ padding: '16px', background: 'rgba(244, 33, 46, 0.1)', borderBottom: '1px solid var(--danger)' }}>
            <strong style={{ color: 'var(--danger)' }}>Error:</strong> {error}
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Make sure the API server is running: <code style={{ background: 'var(--bg-tertiary)', padding: '2px 6px', borderRadius: '4px' }}>python run_api.py</code>
            </div>
          </div>
        )}

        {tweets.length === 0 && !isRunning && !error ? (
          <div className="empty-state">
            <span className="jester-icon">&#129514;</span>
            <span className="parody-badge">100% Satire</span>
            <h3>Welcome to Hopium Lab</h3>
            <p>
              Synthesize a fictional shitcoin and observe how our AI test subjects react in a simulated CT environment.
              <br /><br />
              No real tokens harmed in this experiment. Side effects may include questioning your life choices.
            </p>
            <div className="disclaimer">
              For research purposes only. Not financial advice. NFA. DYOR. WAGMI? Results inconclusive.
            </div>
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
                    {isVerified(tweet.author_type) && <VerifiedBadge gold={isGoldVerified(tweet.author_type)} />}
                    <span className="tweet-handle">@{tweet.author_handle}</span>
                    <span className="tweet-time">· {tweet.hour}h</span>
                    <span className={`tweet-type-badge ${tweet.author_type}`}>
                      {tweet.author_type}
                    </span>
                  </div>
                  <div className="tweet-text">{tweet.content}</div>
                  <div className="tweet-actions">
                    <span className="tweet-action reply">
                      <ReplyIcon />
                      {tweet.replies > 0 && formatNumber(tweet.replies)}
                    </span>
                    <span className="tweet-action repost">
                      <RepostIcon />
                      {tweet.retweets > 0 && formatNumber(tweet.retweets)}
                    </span>
                    <span className="tweet-action like">
                      <LikeIcon />
                      {tweet.likes > 0 && formatNumber(tweet.likes)}
                    </span>
                    <span className="tweet-action views">
                      <ViewsIcon />
                      {formatNumber(Math.floor((tweet.likes + tweet.retweets) * 12.5))}
                    </span>
                    <span className="tweet-action">
                      <BookmarkIcon />
                    </span>
                    <span className="tweet-action">
                      <ShareIcon />
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {isRunning && (
              <div className="loading">
                <div className="spinner" />
                <div>
                  <div>&#129514; Running experiment...</div>
                  <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                    {progress ? (
                      <>
                        Hour {progress.hour}/{progress.total} | Momentum: {progress.momentum > 0 ? '+' : ''}{progress.momentum.toFixed(2)} | {tweets.length} tweets
                      </>
                    ) : (
                      <>Starting simulation...</>
                    )}
                  </div>
                  {progress && (
                    <div style={{ marginTop: '8px', background: 'var(--bg-tertiary)', borderRadius: '4px', height: '4px', width: '200px' }}>
                      <div style={{
                        width: `${(progress.hour / progress.total) * 100}%`,
                        height: '100%',
                        background: progress.momentum > 0 ? 'var(--success)' : progress.momentum < -0.3 ? 'var(--danger)' : 'var(--accent)',
                        borderRadius: '4px',
                        transition: 'width 0.3s, background 0.3s',
                      }} />
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Right Sidebar - Config Panel */}
      <aside className="config-panel">
        <div className="search-box">
          <SearchIcon />
          <input type="text" placeholder="Search" disabled />
        </div>

        <div className="config-card">
          <div className="config-card-header">&#129514; Synthesize Token</div>
          <div className="config-card-body">
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

            <div className="checkbox-group">
              <input
                type="checkbox"
                id="twitter-priors"
                checked={useTwitterPriors}
                onChange={e => setUseTwitterPriors(e.target.checked)}
              />
              <label htmlFor="twitter-priors">
                <div className="checkbox-label">Use real X data</div>
                <div className="checkbox-hint">Calibrate with live CT sentiment (costs API credits)</div>
              </label>
            </div>

            <button
              className="btn btn-primary"
              onClick={runSimulation}
              disabled={isRunning || !config.ticker || !config.narrative}
            >
              {isRunning ? 'Summoning CT Chaos...' : 'Unleash the Degens'}
            </button>
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="results-card">
            <div className="results-header">&#128302; The Oracle Speaks</div>

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

            <div className="prediction-section">
              <span className={`prediction-badge ${result.predicted_outcome}`}>
                {result.predicted_outcome.replace('_', ' ')}
              </span>
              <div className="confidence-text">
                {(result.confidence * 100).toFixed(0)}% confidence
              </div>
            </div>

            <div className="narrative-section">
              <div className="narrative-label">&#129514; Lab Conclusion</div>
              <div className="narrative-text">&quot;{result.dominant_narrative}&quot;</div>
            </div>
          </div>
        )}

        <div className="footer-links">
          <span style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>
            &#129514; Hopium Lab - For research purposes only
          </span>
        </div>
        <div className="footer-links">
          <a href="#">Terms of Tomfoolery</a>
          <a href="#">Privacy? LOL</a>
          <a href="#">Not Financial Advice</a>
          <a href="#">DYOR</a>
        </div>
      </aside>
    </div>
  )
}
