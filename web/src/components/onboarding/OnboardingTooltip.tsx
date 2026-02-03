'use client'

import { useEffect, useRef } from 'react'
import { OnboardingStep } from './steps'
import styles from './Onboarding.module.css'

interface OnboardingTooltipProps {
  step: OnboardingStep
  currentStep: number
  totalSteps: number
  onNext: () => void
  onBack: () => void
  onSkip: () => void
  style?: React.CSSProperties
}

export function OnboardingTooltip({
  step,
  currentStep,
  totalSteps,
  onNext,
  onBack,
  onSkip,
  style,
}: OnboardingTooltipProps) {
  const tooltipRef = useRef<HTMLDivElement>(null)
  const isLastStep = currentStep === totalSteps - 1
  const isFirstStep = currentStep === 0

  // Focus tooltip for accessibility
  useEffect(() => {
    if (tooltipRef.current) {
      tooltipRef.current.focus()
    }
  }, [currentStep])

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onSkip()
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onNext()
      } else if (e.key === 'ArrowLeft' && !isFirstStep) {
        onBack()
      } else if (e.key === 'ArrowRight' && !isLastStep) {
        onNext()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [onNext, onBack, onSkip, isFirstStep, isLastStep])

  return (
    <div
      ref={tooltipRef}
      className={styles.tooltip}
      style={style}
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
      aria-describedby="onboarding-body"
      tabIndex={-1}
    >
      <div className={styles.tooltipTitle} id="onboarding-title">
        <span className={styles.tooltipIcon}>{step.icon}</span>
        {step.title}
      </div>
      <div className={styles.tooltipBody} id="onboarding-body">
        {step.body}
      </div>
      {step.hint && (
        <div className={styles.tooltipHint}>
          {step.hint}
        </div>
      )}

      <div className={styles.controls}>
        <div className={styles.progressDots}>
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`${styles.dot} ${
                i === currentStep ? styles.active : i < currentStep ? styles.completed : ''
              }`}
            />
          ))}
        </div>

        <div className={styles.btnGroup}>
          {!isFirstStep && (
            <button className={styles.btnBack} onClick={onBack}>
              Back
            </button>
          )}
          <button className={styles.btnSkip} onClick={onSkip}>
            Skip
          </button>
          <button className={styles.btnNext} onClick={onNext}>
            {isLastStep ? 'Got it!' : 'Next'}
          </button>
        </div>
      </div>
    </div>
  )
}
