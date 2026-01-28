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
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 px-4 py-3 sticky top-0 bg-black/80 backdrop-blur z-10">
        <div className="max-w-2xl mx-auto flex items-center gap-4">
          <Link href="/" className="text-gray-400 hover:text-white">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
          </Link>
          <div>
            <h1 className="font-bold text-xl">$HOPIUM Whitepaper</h1>
            <p className="text-gray-500 text-sm">Thread format</p>
          </div>
        </div>
      </header>

      {/* Thread */}
      <main className="max-w-2xl mx-auto">
        {whitepaperThread.map((tweet, index) => (
          <article key={tweet.id} className="border-b border-gray-800 px-4 py-4 hover:bg-gray-900/50 transition-colors">
            <div className="flex gap-3">
              {/* Avatar */}
              <div className="flex-shrink-0">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-orange-500 flex items-center justify-center text-white font-bold text-lg">
                  H
                </div>
                {/* Thread line */}
                {index < whitepaperThread.length - 1 && (
                  <div className="w-0.5 h-full bg-gray-800 mx-auto mt-2" style={{ minHeight: '20px' }} />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Author info */}
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold hover:underline cursor-pointer">Hopium Lab</span>
                  <span className="text-gray-500">@hopaboratory</span>
                  <span className="text-gray-500">·</span>
                  <span className="text-gray-500 text-sm">{tweet.id}/16</span>
                </div>

                {/* Tweet content */}
                <div className="space-y-2">
                  <p className="text-lg font-semibold text-purple-400">{tweet.content}</p>
                  {tweet.subtitle && (
                    <p className="text-gray-300 whitespace-pre-line">{tweet.subtitle}</p>
                  )}
                </div>

                {/* Engagement (fake) */}
                <div className="flex items-center gap-6 mt-3 text-gray-500">
                  <button className="flex items-center gap-2 hover:text-blue-400 transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <span className="text-sm">{Math.floor(Math.random() * 50) + 10}</span>
                  </button>
                  <button className="flex items-center gap-2 hover:text-green-400 transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span className="text-sm">{Math.floor(Math.random() * 200) + 50}</span>
                  </button>
                  <button className="flex items-center gap-2 hover:text-pink-400 transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <span className="text-sm">{Math.floor(Math.random() * 500) + 100}</span>
                  </button>
                  <button className="flex items-center gap-2 hover:text-blue-400 transition-colors">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </article>
        ))}

        {/* Download section */}
        <div className="px-4 py-8 border-b border-gray-800">
          <div className="bg-gray-900 rounded-xl p-6 text-center">
            <h3 className="text-xl font-bold mb-2">Full Whitepaper</h3>
            <p className="text-gray-400 mb-4">Download the complete technical document</p>
            <a
              href="/whitepaper.pdf"
              className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold px-6 py-3 rounded-full transition-colors"
            >
              Download PDF
            </a>
          </div>
        </div>

        {/* Footer */}
        <div className="px-4 py-8 text-center text-gray-500">
          <p className="mb-2">Hopium Lab © 2026</p>
          <p className="text-sm">This is a memecoin with utility. NFA. DYOR.</p>
        </div>
      </main>
    </div>
  )
}
