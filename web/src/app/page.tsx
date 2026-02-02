'use client'

import { useState, useEffect, useCallback } from 'react'
import { config } from '@/config'
import { useWallet } from '@/hooks/useWallet'
import { useAuth } from '@/hooks/useAuth'

// Components
import { Sidebar } from '@/components/Sidebar'
import { MobileNav } from '@/components/MobileNav'
import { TweetThread, groupTweetsIntoThreads } from '@/components/TweetThread'
import { TokenForm, TokenConfig } from '@/components/TokenForm'
import { ResultsCard, SimulationResult } from '@/components/ResultsCard'
import { PastExperiments, PastExperiment } from '@/components/PastExperiments'
import { StakingGate } from '@/components/StakingGate'
import { SearchIcon } from '@/components/icons'
import { TweetData } from '@/components/Tweet'
import styles from '@/components/ConfigPanel.module.css'

const API_URL = config.apiUrl

interface Progress {
  hour: number
  total: number
  momentum: number
}

export default function Home() {
  // Form state
  const [tokenConfig, setTokenConfig] = useState<TokenConfig>({
    name: '',
    ticker: '',
    narrative: '',
    tagline: '',
    meme_style: 'absurd',
    market_condition: 'crab'
  })
  const [useTwitterPriors, setUseTwitterPriors] = useState(false)

  // Simulation state
  const [isRunning, setIsRunning] = useState(false)
  const [tweets, setTweets] = useState<TweetData[]>([])
  const [result, setResult] = useState<SimulationResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<Progress | null>(null)

  // UI state
  const [activeTab, setActiveTab] = useState<'foryou' | 'following'>('foryou')
  const [showStakingGate, setShowStakingGate] = useState(false)
  const [stakingHours, setStakingHours] = useState(48)

  // Past experiments
  const [pastExperiments, setPastExperiments] = useState<PastExperiment[]>([])
  const [loadingExperiments, setLoadingExperiments] = useState(true)

  // Hooks
  const wallet = useWallet()
  const auth = useAuth()

  // Fetch past experiments on mount
  useEffect(() => {
    const fetchExperiments = async () => {
      try {
        const response = await fetch(`${API_URL}/harness/experiments`)
        if (response.ok) {
          const data = await response.json()
          setPastExperiments(data.experiments.slice(0, 5))
        }
      } catch {
        // Silently fail - experiments are optional
      } finally {
        setLoadingExperiments(false)
      }
    }
    fetchExperiments()
  }, [])

  // Show staking gate before running simulation
  const handleRunClick = useCallback(() => {
    if (!auth.isConnected) return
    if (!tokenConfig.ticker || !tokenConfig.narrative) return
    setShowStakingGate(true)
  }, [auth.isConnected, tokenConfig.ticker, tokenConfig.narrative])

  // Handle stake confirmation
  const handleStake = useCallback((amount: number, hours: number) => {
    if (!wallet.stake(amount)) {
      setError('Insufficient balance')
      setShowStakingGate(false)
      return
    }
    setStakingHours(hours)
    setShowStakingGate(false)
    runSimulation(hours)
  }, [wallet])

  const runSimulation = async (hours: number) => {
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
            name: tokenConfig.name || tokenConfig.ticker,
            ticker: tokenConfig.ticker,
            narrative: tokenConfig.narrative || 'A new memecoin',
            tagline: tokenConfig.tagline || null,
            meme_style: tokenConfig.meme_style,
            market_condition: tokenConfig.market_condition,
          },
          hours,
          use_twitter_priors: useTwitterPriors,
        }),
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Simulation failed')
      }

      const reader = response.body?.getReader()
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
                wallet.completeSimulation()
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
      wallet.refundStake()
    } finally {
      setIsRunning(false)
      setProgress(null)
    }
  }

  const handleSelectExperiment = useCallback((exp: PastExperiment) => {
    setTokenConfig(prev => ({
      ...prev,
      name: exp.name,
      ticker: exp.ticker,
    }))
  }, [])

  const threadedTweets = groupTweetsIntoThreads(tweets)

  // Config panel content (shared between desktop sidebar and mobile sheet)
  const configPanelContent = (
    <>
      <TokenForm
        config={tokenConfig}
        onChange={setTokenConfig}
        onSubmit={handleRunClick}
        isRunning={isRunning}
        isConnected={auth.isConnected}
        useTwitterPriors={useTwitterPriors}
        onTwitterPriorsChange={setUseTwitterPriors}
      />

      {!result && (
        <PastExperiments
          experiments={pastExperiments}
          loading={loadingExperiments}
          onSelect={handleSelectExperiment}
        />
      )}

      {result && <ResultsCard result={result} tweets={tweets} />}

      <div className={styles.footer}>
        <span>&#129514; Hopium Lab - For research purposes only</span>
      </div>
      <div className={styles.footer}>
        <a href="#">Terms of Tomfoolery</a>
        <a href="#">Privacy? LOL</a>
        <a href="#">Not Financial Advice</a>
        <a href="#">DYOR</a>
      </div>
    </>
  )

  return (
    <div className="container">
      {/* Skip link for accessibility */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Staking Gate Modal */}
      {showStakingGate && (
        <StakingGate
          mode="demo"
          balance={wallet.balance}
          onStake={handleStake}
          onCancel={() => setShowStakingGate(false)}
        />
      )}

      {/* Left Sidebar (Desktop) */}
      <Sidebar
        isConnected={auth.isConnected}
        balance={wallet.balance}
        pendingStake={wallet.pendingStake ?? 0}
        onClaimFaucet={wallet.claimFaucet}
      />

      {/* Main Feed */}
      <main id="main-content" className="main-feed">
        <div className="feed-header">
          <div className="feed-title">&#129489;&#8205;&#128300; The Lab</div>
          <div className="feed-tabs" role="tablist">
            <button
              role="tab"
              className={`feed-tab ${activeTab === 'foryou' ? 'active' : ''}`}
              onClick={() => setActiveTab('foryou')}
              aria-selected={activeTab === 'foryou'}
            >
              For You (Allegedly)
            </button>
            <button
              role="tab"
              className={`feed-tab ${activeTab === 'following' ? 'active' : ''}`}
              onClick={() => setActiveTab('following')}
              aria-selected={activeTab === 'following'}
            >
              Following (lol)
            </button>
          </div>
        </div>

        {error && (
          <div className="error-banner" role="alert">
            <strong>Error:</strong> {error}
            <div className="error-hint">
              Make sure the API server is running: <code>python run_api.py</code>
            </div>
          </div>
        )}

        {tweets.length === 0 && !isRunning && !error ? (
          <div className="empty-state">
            <span className="jester-icon" aria-hidden="true">&#129514;</span>
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
            {threadedTweets.map(({ parent, replies, quotes }) => (
              <TweetThread
                key={parent.id}
                parent={parent}
                replies={replies}
                quotes={quotes}
              />
            ))}
            {isRunning && (
              <div className="loading" aria-live="polite">
                <div className="spinner" aria-hidden="true" />
                <div className="progress-inline">
                  <div>&#129514; Running experiment...</div>
                  <div className="progress-status">
                    {progress ? (
                      <>
                        Hour {progress.hour}/{progress.total} | Momentum: {progress.momentum > 0 ? '+' : ''}{progress.momentum.toFixed(2)} | {tweets.length} tweets
                      </>
                    ) : (
                      <>Starting simulation...</>
                    )}
                  </div>
                  {progress && (
                    <div className="progress-bar-inline">
                      <div
                        className={`progress-fill-inline ${
                          progress.momentum > 0 ? 'positive' :
                          progress.momentum < -0.3 ? 'negative' : 'neutral'
                        }`}
                        style={{ width: `${(progress.hour / progress.total) * 100}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* Right Sidebar - Config Panel (Desktop) */}
      <aside className={styles.panel} aria-label="Token configuration">
        <div
          className={`${styles.searchBox} ${styles.disabled} ${styles.tooltip}`}
          data-tooltip="Coming soon"
        >
          <SearchIcon />
          <input
            type="text"
            placeholder="Search"
            disabled
            aria-label="Search (coming soon)"
          />
        </div>
        {configPanelContent}
      </aside>

      {/* Mobile Navigation */}
      <MobileNav
        isConnected={auth.isConnected}
        balance={wallet.balance}
        configPanel={configPanelContent}
      />
    </div>
  )
}
