'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'

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
    subtitle: "Stake $HOPIUM → Lock period (1-7 days) → Get stake back minus 5% burn.\n\nNo speculation. Just pay-to-play with time commitment + deflationary pressure. Higher stake = shorter lock."
  },
  {
    id: 8,
    content: "Simulation staking tiers",
    subtitle: "Quick (12h): 100 $HOPIUM → 7 day lock\nStandard (24h): 500 $HOPIUM → 3 day lock\nFull (48h): 1,000 $HOPIUM → 1 day lock\n\nHigher stake = deeper sim + shorter lock. Rewards commitment."
  },
  {
    id: 9,
    content: "Harness Lab",
    subtitle: "Run multiple experiments autonomously. The AI generates token ideas, tests them, and learns what works. Stake 50 $HOPIUM per experiment. Batch-test 10 ideas while you sleep."
  },
  {
    id: 10,
    content: "The Gauntlet (Phase 2)",
    subtitle: "Coming soon: Battle-test ideas through increasing difficulty.\n\nStage 1: Crab market\nStage 2: Bear market\nStage 3: Bear + Skeptic swarm\n\nSurvive all three = 'Gauntlet Survivor' badge."
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
    subtitle: "Phase 1: Core platform + staking economy ✓\nPhase 2: Gauntlet mode + on-chain integration\nPhase 3: Leaderboards + social features\nPhase 4: Simulation-to-launch pipeline"
  },
  {
    id: 14,
    content: "Risks (we're honest)",
    subtitle: "• Simulation accuracy: CT is chaotic, predictions are probabilistic\n• Token value: Burns create deflation but adoption drives value\n• Utility dependency: Platform needs users to be useful\n\nThis is a memecoin with utility. Treat it accordingly."
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

// Engagement scales DOWN as thread progresses (earlier = more viral)
function getEngagement(tweetId: number) {
  const baseViews = 50000
  const decay = Math.pow(0.85, tweetId - 1)
  const views = Math.floor(baseViews * decay)
  return {
    replies: Math.floor(views * 0.004),
    reposts: Math.floor(views * 0.015),
    likes: Math.floor(views * 0.04),
    views: views >= 1000 ? `${(views / 1000).toFixed(1)}K` : views.toString()
  }
}

// Verified badge SVG
const VerifiedBadge = () => (
  <svg viewBox="0 0 22 22" style={{ width: '18px', height: '18px', marginLeft: '4px' }}>
    <path
      fill="#1d9bf0"
      d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"
    />
  </svg>
)

export default function WhitepaperPage() {
  const [scrollProgress, setScrollProgress] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
      setScrollProgress(progress)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="container">
      {/* Header with progress bar */}
      <div className="feed-header" style={{ padding: 0 }}>
        {/* Progress bar */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          height: '3px',
          width: `${scrollProgress}%`,
          background: 'var(--accent)',
          transition: 'width 0.1s ease-out',
          zIndex: 10
        }} />
        <div className="feed-title" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '12px 16px'
        }}>
          <Link href="/" style={{
            color: 'var(--text-secondary)',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '8px 12px',
            borderRadius: '9999px',
            transition: 'background 0.2s'
          }}>
            <svg viewBox="0 0 24 24" style={{ width: '20px', height: '20px', fill: 'var(--text-primary)' }}>
              <path d="M7.414 13l5.043 5.04-1.414 1.42L3.586 12l7.457-7.46 1.414 1.42L7.414 11H21v2H7.414z" />
            </svg>
          </Link>
          <div>
            <span style={{ fontWeight: 700 }}>$HOPIUM Whitepaper</span>
            <span style={{
              color: 'var(--text-secondary)',
              fontSize: '13px',
              marginLeft: '8px'
            }}>
              {Math.round(scrollProgress)}% read
            </span>
          </div>
        </div>
      </div>

      {/* Thread */}
      <div style={{ maxWidth: '600px', margin: '0 auto', paddingBottom: '100px' }}>
        {whitepaperThread.map((tweet, index) => {
          const engagement = getEngagement(tweet.id)
          const isFirst = index === 0

          return (
            <div
              key={tweet.id}
              className="tweet"
              style={isFirst ? {
                background: 'linear-gradient(180deg, rgba(29, 155, 240, 0.05) 0%, transparent 100%)',
                borderLeft: '3px solid var(--accent)',
                marginLeft: '-3px'
              } : undefined}
            >
              {/* Avatar with thread line */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  className="avatar"
                  style={isFirst ? {
                    width: '48px',
                    height: '48px',
                    fontSize: '20px',
                    boxShadow: '0 0 0 3px var(--accent)'
                  } : undefined}
                >
                  H
                </div>
                {/* Continuous thread line */}
                {index < whitepaperThread.length - 1 && (
                  <div style={{
                    width: '2px',
                    flex: 1,
                    background: 'var(--border)',
                    minHeight: '100%',
                    marginTop: '4px'
                  }} />
                )}
              </div>

              {/* Content */}
              <div className="tweet-content" style={{ flex: 1 }}>
                {/* Author info with verified badge */}
                <div className="tweet-header" style={{ display: 'flex', alignItems: 'center' }}>
                  <span className="tweet-name" style={isFirst ? { fontSize: '16px' } : undefined}>
                    Hopium Lab
                  </span>
                  <VerifiedBadge />
                  <span className="tweet-handle">@hopaboratory</span>
                  <span className="tweet-time">·</span>
                  <span className="tweet-time">{tweet.id}/16</span>
                </div>

                {/* Tweet content */}
                <div className="tweet-text">
                  <p style={{
                    fontSize: isFirst ? '20px' : '17px',
                    fontWeight: '600',
                    color: 'var(--accent)',
                    marginBottom: '8px'
                  }}>
                    {tweet.content}
                  </p>
                  {tweet.subtitle && (
                    <p style={{
                      whiteSpace: 'pre-line',
                      color: 'var(--text-primary)',
                      fontSize: isFirst ? '16px' : '15px',
                      lineHeight: '1.5'
                    }}>
                      {tweet.subtitle}
                    </p>
                  )}
                </div>

                {/* Engagement - higher for earlier tweets */}
                <div className="tweet-actions">
                  <div className="tweet-action reply">
                    <svg viewBox="0 0 24 24"><path d="M1.751 10c0-4.42 3.584-8 8.005-8h4.366c4.49 0 8.129 3.64 8.129 8.13 0 2.96-1.607 5.68-4.196 7.11l-8.054 4.46v-3.69h-.067c-4.49.1-8.183-3.51-8.183-8.01zm8.005-6c-3.317 0-6.005 2.69-6.005 6 0 3.37 2.77 6.08 6.138 6.01l.351-.01h1.761v2.3l5.087-2.81c1.951-1.08 3.163-3.13 3.163-5.36 0-3.39-2.744-6.13-6.129-6.13H9.756z"/></svg>
                    <span>{engagement.replies}</span>
                  </div>
                  <div className="tweet-action repost">
                    <svg viewBox="0 0 24 24"><path d="M4.5 3.88l4.432 4.14-1.364 1.46L5.5 7.55V16c0 1.1.896 2 2 2H13v2H7.5c-2.209 0-4-1.79-4-4V7.55L1.432 9.48.068 8.02 4.5 3.88zM16.5 6H11V4h5.5c2.209 0 4 1.79 4 4v8.45l2.068-1.93 1.364 1.46-4.432 4.14-4.432-4.14 1.364-1.46 2.068 1.93V8c0-1.1-.896-2-2-2z"/></svg>
                    <span>{engagement.reposts}</span>
                  </div>
                  <div className="tweet-action like">
                    <svg viewBox="0 0 24 24"><path d="M16.697 5.5c-1.222-.06-2.679.51-3.89 2.16l-.805 1.09-.806-1.09C9.984 6.01 8.526 5.44 7.304 5.5c-1.243.07-2.349.78-2.91 1.91-.552 1.12-.633 2.78.479 4.82 1.074 1.97 3.257 4.27 7.129 6.61 3.87-2.34 6.052-4.64 7.126-6.61 1.111-2.04 1.03-3.7.477-4.82-.561-1.13-1.666-1.84-2.908-1.91zm4.187 7.69c-1.351 2.48-4.001 5.12-8.379 7.67l-.503.3-.504-.3c-4.379-2.55-7.029-5.19-8.382-7.67-1.36-2.5-1.41-4.86-.514-6.67.887-1.79 2.647-2.91 4.601-3.01 1.651-.09 3.368.56 4.798 2.01 1.429-1.45 3.146-2.1 4.796-2.01 1.954.1 3.714 1.22 4.601 3.01.896 1.81.846 4.17-.514 6.67z"/></svg>
                    <span>{engagement.likes}</span>
                  </div>
                  <div className="tweet-action views">
                    <svg viewBox="0 0 24 24"><path d="M8.75 21V3h2v18h-2zM18 21V8.5h2V21h-2zM4 21l.004-10h2L6 21H4zm9.248 0v-7h2v7h-2z"/></svg>
                    <span>{engagement.views}</span>
                  </div>
                </div>
              </div>
            </div>
          )
        })}

        {/* Footer */}
        <div style={{ padding: '32px 16px', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <p style={{ marginBottom: '8px' }}>Hopium Lab 2026</p>
          <p style={{ fontSize: '13px' }}>This is a memecoin with utility. NFA. DYOR.</p>
        </div>
      </div>

      {/* Sticky CTA */}
      <div style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '16px',
        background: 'linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.95) 30%)',
        display: 'flex',
        justifyContent: 'center',
        zIndex: 50
      }}>
        <a
          href="/HOPIUM_Whitepaper.pdf"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '14px 32px',
            background: 'var(--accent)',
            color: 'white',
            borderRadius: '9999px',
            textDecoration: 'none',
            fontWeight: '700',
            fontSize: '15px',
            transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'var(--accent-hover)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'var(--accent)'
          }}
        >
          <svg viewBox="0 0 24 24" style={{ width: '20px', height: '20px', fill: 'white' }}>
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
          </svg>
          Download Full Whitepaper (PDF)
        </a>
      </div>
    </div>
  )
}
