'use client'

import Link from 'next/link'

interface WhitepaperTweet {
  id: number
  content: string
  subtitle?: string
}

const whitepaperThread: WhitepaperTweet[] = [
  {
    id: 1,
    content: "Introducing $HOPIUM by @HopiumLab",
    subtitle: "The only token that passed its own simulation. A thread on what we're building..."
  },
  {
    id: 2,
    content: "The Problem",
    subtitle: "Every day, thousands of tokens launch. Most fail within hours. The problem isn't lack of creativity—it's lack of testing. Founders launch based on gut feeling and what worked last cycle."
  },
  {
    id: 3,
    content: "CT is predictable (sort of)",
    subtitle: "Despite appearing chaotic, CT follows patterns. Certain narratives resonate in certain markets. Skeptics pile on weak concepts. Influencers follow momentum. FUD attacks target predictable vulnerabilities."
  },
  {
    id: 4,
    content: "We built a simulation engine",
    subtitle: "AI personas (degens, skeptics, whales, influencers) react to your token concept. We model sentiment dynamics, viral spread, and FUD resistance across market conditions."
  },
  {
    id: 5,
    content: "What we measure",
    subtitle: "Viral Coefficient • Peak Sentiment • FUD Resistance • Sentiment Stability • Hours to Peak • Hours to Death. Run your idea through the gauntlet before risking real capital."
  },
  {
    id: 6,
    content: "$HOPIUM tokenomics",
    subtitle: "1B supply • Solana (Pump.fun launch) • 80% fair launch • 10% team (vested) • 10% treasury. No VC. No presale."
  },
  {
    id: 7,
    content: "The economy is simple",
    subtitle: "1. Stake $HOPIUM to run simulations\n2. Predict outcomes, winners take pool\n3. 5% of everything burned\n\nUse it or lose it to deflation."
  },
  {
    id: 8,
    content: "Simulation staking tiers",
    subtitle: "Quick sim (12h): 100 $HOPIUM\nStandard (24h): 500 $HOPIUM\nFull (48h): 1,000 $HOPIUM\nGauntlet (all markets): 2,500 $HOPIUM"
  },
  {
    id: 9,
    content: "Prediction markets",
    subtitle: "Bet on outcomes: Moon, Cult Classic, Pump & Dump, Slow Bleed, Rug. Winners split the pool minus 5% burn. Put your money where your alpha is."
  },
  {
    id: 10,
    content: "The Gauntlet",
    subtitle: "Battle-test ideas through increasing difficulty:\n\nStage 1: Crab → 1.5x\nStage 2: Bear → 2x\nStage 3: Bear + Skeptics → 3x\n\nFail = 50% burned. Pass all = 'Gauntlet Survivor' badge."
  },
  {
    id: 11,
    content: "The meta play",
    subtitle: "This is recursive: a token for a platform that simulates tokens. We ran $HOPIUM through our own simulator before launch. Result: Cult Classic (67% confidence). We publish this openly."
  },
  {
    id: 12,
    content: "Self-simulation results",
    subtitle: "Viral Coefficient: 7.2x\nPeak Sentiment: +0.73\nFUD Resistance: 0.81\n\nStrength: Meta-narrative resonates\nRisk: May seem too niche"
  },
  {
    id: 13,
    content: "Roadmap",
    subtitle: "Phase 1: Fair launch + core platform\nPhase 2: Gauntlet mode + leaderboards\nPhase 3: Curator rewards + social\nPhase 4: Simulation-to-launch pipeline"
  },
  {
    id: 14,
    content: "Risks (we're honest)",
    subtitle: "• Simulation accuracy: CT can be unpredictable\n• Regulatory: Prediction markets are gray area\n• Adoption: Utility needs users\n\nThis is a memecoin with utility. Treat it accordingly."
  },
  {
    id: 15,
    content: "TL;DR",
    subtitle: "$HOPIUM is an experiment in recursive tokenomics. A token that simulated itself before launch. If we're right, we build something useful. If we're wrong, at least we were honest about it."
  },
  {
    id: 16,
    content: "The only token that passed its own simulation.",
    subtitle: "Website: hopiumlab.xyz\nTwitter: @hopaboratory\n\nFair launch soon. NFA. DYOR."
  },
]

export default function WhitepaperPage() {
  return (
    <div className="container">
      {/* Header */}
      <div className="feed-header">
        <div className="feed-title" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Link href="/" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
            ← Back
          </Link>
          <span>$HOPIUM Whitepaper</span>
        </div>
      </div>

      {/* Thread */}
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        {whitepaperThread.map((tweet, index) => (
          <div key={tweet.id} className="tweet">
            {/* Avatar */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div className="avatar">H</div>
              {/* Thread line */}
              {index < whitepaperThread.length - 1 && (
                <div style={{
                  width: '2px',
                  flex: 1,
                  background: 'var(--border)',
                  marginTop: '8px',
                  minHeight: '20px'
                }} />
              )}
            </div>

            {/* Content */}
            <div className="tweet-content">
              {/* Author info */}
              <div className="tweet-header">
                <span className="tweet-name">Hopium Lab</span>
                <span className="tweet-handle">@hopaboratory</span>
                <span className="tweet-time">·</span>
                <span className="tweet-time">{tweet.id}/16</span>
              </div>

              {/* Tweet content */}
              <div className="tweet-text">
                <p style={{
                  fontSize: '17px',
                  fontWeight: '600',
                  color: 'var(--accent)',
                  marginBottom: '8px'
                }}>
                  {tweet.content}
                </p>
                {tweet.subtitle && (
                  <p style={{ whiteSpace: 'pre-line', color: 'var(--text-primary)' }}>
                    {tweet.subtitle}
                  </p>
                )}
              </div>

              {/* Engagement */}
              <div className="tweet-actions">
                <div className="tweet-action reply">
                  <svg viewBox="0 0 24 24"><path d="M1.751 10c0-4.42 3.584-8 8.005-8h4.366c4.49 0 8.129 3.64 8.129 8.13 0 2.96-1.607 5.68-4.196 7.11l-8.054 4.46v-3.69h-.067c-4.49.1-8.183-3.51-8.183-8.01zm8.005-6c-3.317 0-6.005 2.69-6.005 6 0 3.37 2.77 6.08 6.138 6.01l.351-.01h1.761v2.3l5.087-2.81c1.951-1.08 3.163-3.13 3.163-5.36 0-3.39-2.744-6.13-6.129-6.13H9.756z"/></svg>
                  <span>{12 + tweet.id * 3}</span>
                </div>
                <div className="tweet-action repost">
                  <svg viewBox="0 0 24 24"><path d="M4.5 3.88l4.432 4.14-1.364 1.46L5.5 7.55V16c0 1.1.896 2 2 2H13v2H7.5c-2.209 0-4-1.79-4-4V7.55L1.432 9.48.068 8.02 4.5 3.88zM16.5 6H11V4h5.5c2.209 0 4 1.79 4 4v8.45l2.068-1.93 1.364 1.46-4.432 4.14-4.432-4.14 1.364-1.46 2.068 1.93V8c0-1.1-.896-2-2-2z"/></svg>
                  <span>{50 + tweet.id * 15}</span>
                </div>
                <div className="tweet-action like">
                  <svg viewBox="0 0 24 24"><path d="M16.697 5.5c-1.222-.06-2.679.51-3.89 2.16l-.805 1.09-.806-1.09C9.984 6.01 8.526 5.44 7.304 5.5c-1.243.07-2.349.78-2.91 1.91-.552 1.12-.633 2.78.479 4.82 1.074 1.97 3.257 4.27 7.129 6.61 3.87-2.34 6.052-4.64 7.126-6.61 1.111-2.04 1.03-3.7.477-4.82-.561-1.13-1.666-1.84-2.908-1.91zm4.187 7.69c-1.351 2.48-4.001 5.12-8.379 7.67l-.503.3-.504-.3c-4.379-2.55-7.029-5.19-8.382-7.67-1.36-2.5-1.41-4.86-.514-6.67.887-1.79 2.647-2.91 4.601-3.01 1.651-.09 3.368.56 4.798 2.01 1.429-1.45 3.146-2.1 4.796-2.01 1.954.1 3.714 1.22 4.601 3.01.896 1.81.846 4.17-.514 6.67z"/></svg>
                  <span>{100 + tweet.id * 30}</span>
                </div>
                <div className="tweet-action views">
                  <svg viewBox="0 0 24 24"><path d="M8.75 21V3h2v18h-2zM18 21V8.5h2V21h-2zM4 21l.004-10h2L6 21H4zm9.248 0v-7h2v7h-2z"/></svg>
                  <span>{(tweet.id * 1.2).toFixed(0)}K</span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Download section */}
        <div style={{ padding: '32px 16px', borderBottom: '1px solid var(--border)' }}>
          <div className="config-card">
            <div className="config-card-header" style={{ textAlign: 'center' }}>
              Full Whitepaper (PDF)
            </div>
            <div className="config-card-body" style={{ textAlign: 'center', paddingTop: '16px' }}>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
                Download the complete IEEE-format technical document
              </p>
              <a
                href="/HOPIUM_Whitepaper.pdf"
                className="btn btn-primary"
                style={{ display: 'inline-block', width: 'auto', padding: '12px 32px' }}
              >
                Download PDF
              </a>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p style={{ marginBottom: '8px' }}>Hopium Lab 2026</p>
          <p style={{ fontSize: '13px' }}>This is a memecoin with utility. NFA. DYOR.</p>
        </div>
      </div>
    </div>
  )
}
