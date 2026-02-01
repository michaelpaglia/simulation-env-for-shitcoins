import styles from './ConfigPanel.module.css'

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

interface ResultsCardProps {
  result: SimulationResult
}

function formatNumber(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

export function ResultsCard({ result }: ResultsCardProps) {
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
    </div>
  )
}
