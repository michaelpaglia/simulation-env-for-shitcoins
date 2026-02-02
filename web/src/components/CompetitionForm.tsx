'use client'

import { useState } from 'react'
import styles from './ConfigPanel.module.css'

export interface CompetitorToken {
  name: string
  ticker: string
  narrative: string
  meme_style: string
}

export interface CompetitionResult {
  token: CompetitorToken
  viral_coefficient: number
  peak_sentiment: number
  total_engagement: number
  influencer_pickups: number
  predicted_outcome: string
  confidence: number
  rank: number
  market_share: number
}

export interface CompetitionResponse {
  results: CompetitionResult[]
  winner: string
  analysis: string
}

interface CompetitionFormProps {
  onRun: (tokens: CompetitorToken[], hours: number) => Promise<void>
  isRunning: boolean
  result: CompetitionResponse | null
}

const MEME_STYLES = [
  { value: 'absurd', label: 'Absurd' },
  { value: 'cute', label: 'Cute' },
  { value: 'edgy', label: 'Edgy' },
  { value: 'topical', label: 'Topical' },
  { value: 'nostalgic', label: 'Nostalgic' },
]

const emptyToken = (): CompetitorToken => ({
  name: '',
  ticker: '',
  narrative: '',
  meme_style: 'absurd',
})

export function CompetitionForm({ onRun, isRunning, result }: CompetitionFormProps) {
  const [tokens, setTokens] = useState<CompetitorToken[]>([emptyToken(), emptyToken()])
  const [hours, setHours] = useState(48)

  const updateToken = (index: number, field: keyof CompetitorToken, value: string) => {
    setTokens(prev => {
      const updated = [...prev]
      updated[index] = { ...updated[index], [field]: value }
      return updated
    })
  }

  const addToken = () => {
    if (tokens.length < 4) {
      setTokens(prev => [...prev, emptyToken()])
    }
  }

  const removeToken = (index: number) => {
    if (tokens.length > 2) {
      setTokens(prev => prev.filter((_, i) => i !== index))
    }
  }

  const handleSubmit = () => {
    const validTokens = tokens.filter(t => t.ticker && t.narrative)
    if (validTokens.length >= 2) {
      onRun(validTokens, hours)
    }
  }

  const canSubmit = tokens.filter(t => t.ticker && t.narrative).length >= 2

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>&#9876; Token Competition</div>
      <div className={styles.cardBody}>
        <p className={styles.competitionHint}>
          Pit 2-4 tokens against each other to see which concept wins on CT.
        </p>

        {tokens.map((token, idx) => (
          <div key={idx} className={styles.competitorCard}>
            <div className={styles.competitorHeader}>
              <span>Token #{idx + 1}</span>
              {tokens.length > 2 && (
                <button
                  type="button"
                  className={styles.removeBtn}
                  onClick={() => removeToken(idx)}
                >
                  &#10005;
                </button>
              )}
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel}>Ticker</label>
              <input
                type="text"
                className={styles.formInput}
                placeholder="TICKER"
                value={token.ticker}
                onChange={e => updateToken(idx, 'ticker', e.target.value.toUpperCase())}
                maxLength={10}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel}>Name</label>
              <input
                type="text"
                className={styles.formInput}
                placeholder="Token Name"
                value={token.name}
                onChange={e => updateToken(idx, 'name', e.target.value)}
                maxLength={50}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel}>Narrative</label>
              <textarea
                className={styles.formInput}
                placeholder="What's the story?"
                value={token.narrative}
                onChange={e => updateToken(idx, 'narrative', e.target.value)}
                rows={2}
                maxLength={200}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.formLabel}>Meme Style</label>
              <select
                className={styles.formSelect}
                value={token.meme_style}
                onChange={e => updateToken(idx, 'meme_style', e.target.value)}
              >
                {MEME_STYLES.map(style => (
                  <option key={style.value} value={style.value}>
                    {style.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        ))}

        {tokens.length < 4 && (
          <button
            type="button"
            className={styles.addTokenBtn}
            onClick={addToken}
          >
            + Add Another Token
          </button>
        )}

        <div className={styles.formGroup}>
          <label className={styles.formLabel}>Simulation Hours</label>
          <select
            className={styles.formSelect}
            value={hours}
            onChange={e => setHours(Number(e.target.value))}
          >
            <option value={24}>24 hours</option>
            <option value={48}>48 hours</option>
            <option value={72}>72 hours</option>
          </select>
        </div>

        <button
          type="button"
          className={`${styles.btn} ${styles.btnPrimary}`}
          onClick={handleSubmit}
          disabled={!canSubmit || isRunning}
        >
          {isRunning ? 'Running Competition...' : 'Run Competition'}
        </button>
      </div>

      {result && (
        <div className={styles.competitionResults}>
          <div className={styles.competitionResultsHeader}>&#127942; Results</div>

          {result.results.map((r, idx) => (
            <div
              key={idx}
              className={`${styles.competitorResult} ${r.rank === 1 ? styles.winner : ''}`}
            >
              <div className={styles.competitorResultHeader}>
                <span className={styles.competitorRank}>#{r.rank}</span>
                <span className={styles.competitorTicker}>${r.token.ticker}</span>
                {r.rank === 1 && <span className={styles.winnerBadge}>&#127942; WINNER</span>}
              </div>
              <div className={styles.competitorStats}>
                <div className={styles.competitorStat}>
                  <span className={styles.statLabel}>Viral</span>
                  <span className={styles.statValue}>{r.viral_coefficient.toFixed(2)}x</span>
                </div>
                <div className={styles.competitorStat}>
                  <span className={styles.statLabel}>Share</span>
                  <span className={styles.statValue}>{(r.market_share * 100).toFixed(0)}%</span>
                </div>
                <div className={styles.competitorStat}>
                  <span className={styles.statLabel}>KOLs</span>
                  <span className={styles.statValue}>{r.influencer_pickups}</span>
                </div>
              </div>
              <div className={styles.competitorOutcome}>
                <span className={`${styles.outcomeBadge} ${styles[r.predicted_outcome] || ''}`}>
                  {r.predicted_outcome.replace('_', ' ')}
                </span>
              </div>
            </div>
          ))}

          <div className={styles.competitionAnalysis}>
            <div className={styles.analysisLabel}>&#129302; AI Analysis</div>
            <div className={styles.analysisText}>{result.analysis}</div>
          </div>
        </div>
      )}
    </div>
  )
}
