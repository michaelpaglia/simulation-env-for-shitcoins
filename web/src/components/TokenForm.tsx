'use client'

import { useState, useCallback } from 'react'
import styles from './ConfigPanel.module.css'

export interface TokenConfig {
  name: string
  ticker: string
  narrative: string
  tagline: string
  meme_style: string
  market_condition: string
}

interface TokenFormProps {
  config: TokenConfig
  onChange: (config: TokenConfig) => void
  onSubmit: () => void
  isRunning: boolean
  isConnected: boolean
  useTwitterPriors: boolean
  onTwitterPriorsChange: (value: boolean) => void
}

const TICKER_MAX = 10
const NARRATIVE_MAX = 200

export function TokenForm({
  config,
  onChange,
  onSubmit,
  isRunning,
  isConnected,
  useTwitterPriors,
  onTwitterPriorsChange,
}: TokenFormProps) {
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const handleChange = useCallback((field: keyof TokenConfig, value: string) => {
    onChange({ ...config, [field]: value })
  }, [config, onChange])

  const handleBlur = useCallback((field: string) => {
    setTouched(prev => ({ ...prev, [field]: true }))
  }, [])

  const tickerError = touched.ticker && !config.ticker ? 'Ticker is required' : null
  const narrativeError = touched.narrative && !config.narrative ? 'Narrative is required' : null

  const canSubmit = config.ticker && config.narrative && !isRunning

  const getButtonText = () => {
    if (isRunning) return 'Summoning CT Chaos...'
    if (!isConnected) return 'Connect Wallet to Simulate'
    return 'Stake & Simulate'
  }

  const getButtonTooltip = () => {
    if (isRunning) return 'Simulation in progress'
    if (!isConnected) return 'Connect your wallet first'
    if (!config.ticker) return 'Enter a ticker symbol'
    if (!config.narrative) return 'Enter a narrative'
    return ''
  }

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>&#129514; Synthesize Token</div>
      <div className={styles.cardBody}>
        <div className={styles.formGroup}>
          <label className={styles.formLabel} htmlFor="token-name">
            Token Name
          </label>
          <input
            id="token-name"
            type="text"
            className={styles.formInput}
            placeholder="DogeKiller9000"
            value={config.name}
            onChange={e => handleChange('name', e.target.value)}
          />
        </div>

        <div className={styles.formGroup}>
          <label className={styles.formLabel} htmlFor="token-ticker">
            Ticker <span style={{ color: 'var(--danger)' }}>*</span>
          </label>
          <div className={styles.formInputWrapper}>
            <input
              id="token-ticker"
              type="text"
              className={`${styles.formInput} ${tickerError ? styles.error : ''}`}
              placeholder="DK9000"
              value={config.ticker}
              onChange={e => handleChange('ticker', e.target.value.toUpperCase())}
              onBlur={() => handleBlur('ticker')}
              maxLength={TICKER_MAX}
              aria-invalid={!!tickerError}
              aria-describedby={tickerError ? 'ticker-error' : undefined}
              data-onboarding="ticker"
            />
            <span
              className={`${styles.charCounter} ${
                config.ticker.length >= TICKER_MAX ? styles.error :
                config.ticker.length >= TICKER_MAX - 2 ? styles.warning : ''
              }`}
            >
              {config.ticker.length}/{TICKER_MAX}
            </span>
          </div>
          {tickerError && (
            <div id="ticker-error" className={styles.formError} role="alert">
              {tickerError}
            </div>
          )}
        </div>

        <div className={styles.formGroup}>
          <label className={styles.formLabel} htmlFor="token-narrative">
            Narrative <span style={{ color: 'var(--danger)' }}>*</span>
          </label>
          <div className={styles.formInputWrapper}>
            <input
              id="token-narrative"
              type="text"
              className={`${styles.formInput} ${narrativeError ? styles.error : ''}`}
              placeholder="AI meme that roasts other memes"
              value={config.narrative}
              onChange={e => handleChange('narrative', e.target.value)}
              onBlur={() => handleBlur('narrative')}
              maxLength={NARRATIVE_MAX}
              aria-invalid={!!narrativeError}
              aria-describedby={narrativeError ? 'narrative-error' : undefined}
            />
            <span
              className={`${styles.charCounter} ${
                config.narrative.length >= NARRATIVE_MAX ? styles.error :
                config.narrative.length >= NARRATIVE_MAX - 20 ? styles.warning : ''
              }`}
            >
              {config.narrative.length}/{NARRATIVE_MAX}
            </span>
          </div>
          {narrativeError && (
            <div id="narrative-error" className={styles.formError} role="alert">
              {narrativeError}
            </div>
          )}
        </div>

        <div className={styles.formGroup}>
          <label className={styles.formLabel} htmlFor="meme-style">
            Meme Style
          </label>
          <select
            id="meme-style"
            className={styles.formSelect}
            value={config.meme_style}
            onChange={e => handleChange('meme_style', e.target.value)}
            data-onboarding="meme-style"
          >
            <option value="cute">Cute (doge, cats)</option>
            <option value="edgy">Edgy (dark humor)</option>
            <option value="absurd">Absurd (surreal)</option>
            <option value="topical">Topical (trending)</option>
            <option value="nostalgic">Nostalgic (retro)</option>
          </select>
        </div>

        <div className={styles.formGroup}>
          <label className={styles.formLabel} htmlFor="market-condition">
            Market Condition
          </label>
          <select
            id="market-condition"
            className={styles.formSelect}
            value={config.market_condition}
            onChange={e => handleChange('market_condition', e.target.value)}
          >
            <option value="bear">Bear Market</option>
            <option value="crab">Crab Market</option>
            <option value="bull">Bull Market</option>
            <option value="euphoria">Euphoria</option>
          </select>
        </div>

        <div className={styles.checkboxGroup}>
          <input
            type="checkbox"
            id="twitter-priors"
            checked={useTwitterPriors}
            onChange={e => onTwitterPriorsChange(e.target.checked)}
          />
          <label htmlFor="twitter-priors">
            <div className={styles.checkboxLabel}>Use real X data</div>
            <div className={styles.checkboxHint}>
              Calibrate with live CT sentiment (costs API credits)
            </div>
          </label>
        </div>

        <button
          className={`${styles.btn} ${styles.btnPrimary} ${!canSubmit ? styles.tooltip : ''}`}
          onClick={onSubmit}
          disabled={!canSubmit}
          data-tooltip={getButtonTooltip()}
          aria-busy={isRunning}
          data-onboarding="simulate-btn"
        >
          {getButtonText()}
        </button>
        {isConnected && !isRunning && (
          <div className={styles.stakeHint}>
            100-1,000 $HOPIUM · 5% burned per sim
          </div>
        )}
      </div>
    </div>
  )
}
