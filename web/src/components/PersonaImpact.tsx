import { useMemo } from 'react'
import { TweetData } from './Tweet'

interface PersonaImpactProps {
  tweets: TweetData[]
}

interface PersonaStats {
  type: string
  tweetCount: number
  avgSentiment: number
  totalEngagement: number
  engagementPct: number
}

const PERSONA_COLORS: Record<string, string> = {
  kol: '#1d9bf0',
  degen: '#f91880',
  skeptic: '#f4212e',
  whale: '#ffd400',
  influencer: '#7856ff',
  normie: '#71767b',
  bot: '#00ba7c',
}

const PERSONA_LABELS: Record<string, string> = {
  kol: 'KOL',
  degen: 'Degen',
  skeptic: 'Skeptic',
  whale: 'Whale',
  influencer: 'Influencer',
  normie: 'Normie',
  bot: 'Bot',
}

export function PersonaImpact({ tweets }: PersonaImpactProps) {
  const stats = useMemo(() => {
    if (tweets.length === 0) return []

    // Group by persona type
    const byType: Record<string, { tweets: TweetData[]; engagement: number }> = {}
    let totalEngagement = 0

    tweets.forEach(tweet => {
      const type = tweet.author_type
      if (!byType[type]) {
        byType[type] = { tweets: [], engagement: 0 }
      }
      const engagement = tweet.likes + tweet.retweets + tweet.replies
      byType[type].tweets.push(tweet)
      byType[type].engagement += engagement
      totalEngagement += engagement
    })

    // Calculate stats
    const result: PersonaStats[] = Object.entries(byType)
      .map(([type, data]) => ({
        type,
        tweetCount: data.tweets.length,
        avgSentiment:
          data.tweets.reduce((sum, t) => sum + t.sentiment, 0) / data.tweets.length,
        totalEngagement: data.engagement,
        engagementPct: totalEngagement > 0 ? (data.engagement / totalEngagement) * 100 : 0,
      }))
      .sort((a, b) => b.engagementPct - a.engagementPct)

    return result
  }, [tweets])

  if (stats.length === 0) return null

  const hypeSources = stats.filter(s => s.avgSentiment > 0.2)
  const fudSources = stats.filter(s => s.avgSentiment < -0.2)

  return (
    <div style={{ marginTop: '16px', padding: '12px 16px', borderTop: '1px solid var(--border)' }}>
      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
        Persona Impact
      </div>

      {/* Bar chart */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {stats.slice(0, 5).map(persona => (
          <div key={persona.type} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ width: '70px', fontSize: '12px', color: PERSONA_COLORS[persona.type] || 'var(--text-secondary)' }}>
              {PERSONA_LABELS[persona.type] || persona.type}
            </div>
            <div style={{ flex: 1, height: '16px', background: 'var(--bg-tertiary)', borderRadius: '4px', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${persona.engagementPct}%`,
                  height: '100%',
                  background: PERSONA_COLORS[persona.type] || 'var(--text-secondary)',
                  opacity: 0.7,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            <div style={{ width: '40px', fontSize: '11px', color: 'var(--text-secondary)', textAlign: 'right' }}>
              {persona.engagementPct.toFixed(0)}%
            </div>
          </div>
        ))}
      </div>

      {/* Hype/FUD breakdown */}
      <div style={{ display: 'flex', gap: '16px', marginTop: '12px', fontSize: '12px' }}>
        {hypeSources.length > 0 && (
          <div style={{ flex: 1 }}>
            <div style={{ color: 'var(--success)', marginBottom: '4px' }}>Hype drivers</div>
            <div style={{ color: 'var(--text-secondary)' }}>
              {hypeSources.map(s => PERSONA_LABELS[s.type] || s.type).join(', ')}
            </div>
          </div>
        )}
        {fudSources.length > 0 && (
          <div style={{ flex: 1 }}>
            <div style={{ color: 'var(--danger)', marginBottom: '4px' }}>FUD sources</div>
            <div style={{ color: 'var(--text-secondary)' }}>
              {fudSources.map(s => PERSONA_LABELS[s.type] || s.type).join(', ')}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
