import styles from './ConfigPanel.module.css'

export interface PastExperiment {
  id: string
  ticker: string
  name: string
  narrative: string
  strategy: string
  status: string
  score: number | null
  outcome: string | null
}

interface PastExperimentsProps {
  experiments: PastExperiment[]
  loading: boolean
  onSelect: (experiment: PastExperiment) => void
}

export function PastExperiments({ experiments, loading, onSelect }: PastExperimentsProps) {
  if (loading) {
    return (
      <div className={styles.card}>
        <div className={styles.cardHeader}>&#128200; Past Experiments</div>
        <div className={styles.pastExperiments}>
          <div style={{ padding: '16px', color: 'var(--text-secondary)', fontSize: '13px', textAlign: 'center' }}>
            Loading experiments...
          </div>
        </div>
      </div>
    )
  }

  if (experiments.length === 0) {
    return null
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>&#128200; Past Experiments</div>
      <div className={styles.pastExperiments}>
        {experiments.map((exp) => (
          <button
            key={exp.id}
            className={styles.experimentItem}
            onClick={() => onSelect(exp)}
            title="Click to load this token config"
            type="button"
          >
            <div className={styles.experimentInfo}>
              <div className={styles.experimentTicker}>${exp.ticker}</div>
              <div className={styles.experimentName}>{exp.name}</div>
            </div>
            <span className={`${styles.outcomeBadge} ${styles[exp.outcome || exp.status] || ''}`}>
              {exp.outcome ? exp.outcome.replace('_', ' ') : exp.status}
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
