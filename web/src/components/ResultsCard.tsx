import { useState } from 'react'
import styles from './ConfigPanel.module.css'
import { SentimentChart } from './SentimentChart'
import { PersonaImpact } from './PersonaImpact'
import { TweetData } from './Tweet'

export interface SimulationResult {
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

export interface TokenVariation {
  name: string
  ticker: string
  narrative: string
  hook: string
  meme_style: string
  changes: string
}

interface ResultsCardProps {
  result: SimulationResult
  tweets?: TweetData[]
  onImprove?: () => Promise<TokenVariation[]>
  onSelectVariation?: (variation: TokenVariation) => void
  isImproving?: boolean
}

function formatNumber(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

export function ResultsCard({
  result,
  tweets = [],
  onImprove,
  onSelectVariation,
  isImproving = false
}: ResultsCardProps) {
  const [variations, setVariations] = useState<TokenVariation[]>([])
  const [showVariations, setShowVariations] = useState(false)

  const handleImprove = async () => {
    if (!onImprove) return
    try {
      const newVariations = await onImprove()
      setVariations(newVariations)
      setShowVariations(true)
    } catch (err) {
      console.error('Failed to get improvements:', err)
    }
  }

  const handleSelectVariation = (variation: TokenVariation) => {
    if (onSelectVariation) {
      onSelectVariation(variation)
      setShowVariations(false)
    }
  }

  return (
    <div className={styles.resultsCard}>
      <div className={styles.resultsHeader}>&#128302; The Oracle Speaks</div>

      <div className={styles.resultRow}>
        <span className={styles.resultLabel}>Viral Score</span>
        <span className={`${styles.resultValue} ${result.viral_coefficient > 1 ? styles.positive : styles.negative}`}>
          {result.viral_coefficient.toFixed(2)}x
        </span>
      </div>

      <div className={styles.resultRow}>
        <span className={styles.resultLabel}>Peak Sentiment</span>
        <span className={`${styles.resultValue} ${result.peak_sentiment > 0 ? styles.positive : styles.negative}`}>
          {result.peak_sentiment > 0 ? '+' : ''}{result.peak_sentiment.toFixed(2)}
        </span>
      </div>

      <div className={styles.resultRow}>
        <span className={styles.resultLabel}>FUD Resistance</span>
        <span className={`${styles.resultValue} ${result.fud_resistance > 0.5 ? styles.positive : styles.neutral}`}>
          {(result.fud_resistance * 100).toFixed(0)}%
        </span>
      </div>

      <div className={styles.resultRow}>
        <span className={styles.resultLabel}>Total Engagement</span>
        <span className={styles.resultValue}>{formatNumber(result.total_engagement)}</span>
      </div>

      <div className={styles.resultRow}>
        <span className={styles.resultLabel}>KOL Pickups</span>
        <span className={styles.resultValue}>{result.influencer_pickups}</span>
      </div>

      <div className={styles.resultRow}>
        <span className={styles.resultLabel}>Peak Hour</span>
        <span className={styles.resultValue}>Hour {result.hours_to_peak}</span>
      </div>

      <div className={styles.predictionSection}>
        <span className={`${styles.predictionBadge} ${styles[result.predicted_outcome] || ''}`}>
          {result.predicted_outcome.replace('_', ' ')}
        </span>
        <div className={styles.confidenceText}>
          {(result.confidence * 100).toFixed(0)}% confidence
        </div>
      </div>

      <div className={styles.narrativeSection}>
        <div className={styles.narrativeLabel}>&#129514; Lab Conclusion</div>
        <div className={styles.narrativeText}>&quot;{result.dominant_narrative}&quot;</div>
      </div>

      {onImprove && (
        <div className={styles.improveSection}>
          <button
            className={`${styles.btn} ${styles.btnImprove}`}
            onClick={handleImprove}
            disabled={isImproving}
          >
            {isImproving ? 'Analyzing...' : '&#128161; Improve This Token'}
          </button>
        </div>
      )}

      {showVariations && variations.length > 0 && (
        <div className={styles.variationsSection}>
          <div className={styles.variationsHeader}>&#9889; Suggested Improvements</div>
          {variations.map((variation, idx) => (
            <div
              key={idx}
              className={styles.variationCard}
              onClick={() => handleSelectVariation(variation)}
            >
              <div className={styles.variationHeader}>
                <span className={styles.variationName}>{variation.name}</span>
                <span className={styles.variationTicker}>${variation.ticker}</span>
              </div>
              <div className={styles.variationNarrative}>{variation.narrative}</div>
              {variation.hook && (
                <div className={styles.variationHook}>&#127919; {variation.hook}</div>
              )}
              <div className={styles.variationChanges}>{variation.changes}</div>
            </div>
          ))}
        </div>
      )}

      {tweets.length > 0 && (
        <>
          <SentimentChart tweets={tweets} />
          <PersonaImpact tweets={tweets} />
        </>
      )}
    </div>
  )
}
