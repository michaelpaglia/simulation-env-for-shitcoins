'use client'

import { useState, useEffect, useCallback } from 'react'
import { usePathname } from 'next/navigation'
import { useOnboarding } from './OnboardingProvider'
import { OnboardingArrow } from './OnboardingArrow'
import { OnboardingTooltip } from './OnboardingTooltip'
import { getOnboardingForPath } from './steps'
import styles from './Onboarding.module.css'

interface TargetRect {
  top: number
  left: number
  width: number
  height: number
}

export function OnboardingOverlay() {
  const pathname = usePathname()
  const { isActive, currentStep, totalSteps, next, back, skip } = useOnboarding()
  const [targetRect, setTargetRect] = useState<TargetRect | null>(null)
  const [isMobile, setIsMobile] = useState(false)

  const pageOnboarding = getOnboardingForPath(pathname)
  const step = pageOnboarding?.steps[currentStep]

  // Check if mobile
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 1000)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Find and track target element position
  const updateTargetRect = useCallback(() => {
    if (!step) return

    const selector = isMobile && step.mobileTargetSelector
      ? step.mobileTargetSelector
      : step.targetSelector

    const target = document.querySelector(selector)
    if (target) {
      const rect = target.getBoundingClientRect()
      const padding = 8
      setTargetRect({
        top: rect.top - padding,
        left: rect.left - padding,
        width: rect.width + padding * 2,
        height: rect.height + padding * 2,
      })

      // Scroll target into view if needed
      const isInViewport =
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= window.innerHeight &&
        rect.right <= window.innerWidth

      if (!isInViewport) {
        target.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    } else {
      setTargetRect(null)
    }
  }, [step, isMobile])

  // Update position on step change and resize
  useEffect(() => {
    if (!isActive) return

    updateTargetRect()

    // Use ResizeObserver for dynamic updates
    const resizeObserver = new ResizeObserver(updateTargetRect)
    const mutationObserver = new MutationObserver(updateTargetRect)

    resizeObserver.observe(document.body)
    mutationObserver.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
    })

    window.addEventListener('resize', updateTargetRect)
    window.addEventListener('scroll', updateTargetRect)

    return () => {
      resizeObserver.disconnect()
      mutationObserver.disconnect()
      window.removeEventListener('resize', updateTargetRect)
      window.removeEventListener('scroll', updateTargetRect)
    }
  }, [isActive, currentStep, updateTargetRect])

  if (!isActive || !step || !pageOnboarding) return null

  // Calculate arrow and tooltip positions
  const getArrowPosition = (): React.CSSProperties => {
    if (!targetRect) return { display: 'none' }

    const arrowSize = 32
    const gap = 8

    switch (step.arrowDirection) {
      case 'left':
        return {
          top: targetRect.top + targetRect.height / 2 - arrowSize / 2,
          left: targetRect.left - arrowSize - gap,
        }
      case 'right':
        return {
          top: targetRect.top + targetRect.height / 2 - arrowSize / 2,
          left: targetRect.left + targetRect.width + gap,
        }
      case 'up':
        return {
          top: targetRect.top - arrowSize - gap,
          left: targetRect.left + targetRect.width / 2 - arrowSize / 2,
        }
      case 'down':
        return {
          top: targetRect.top + targetRect.height + gap,
          left: targetRect.left + targetRect.width / 2 - arrowSize / 2,
        }
      default:
        return {}
    }
  }

  const getTooltipPosition = (): React.CSSProperties => {
    if (!targetRect || isMobile) return {}

    const tooltipWidth = 320
    const gap = 56 // Space for arrow + padding

    switch (step.tooltipPosition) {
      case 'left':
        return {
          top: Math.max(20, targetRect.top),
          left: Math.max(20, targetRect.left - tooltipWidth - gap),
        }
      case 'right':
        return {
          top: Math.max(20, targetRect.top),
          left: Math.min(
            window.innerWidth - tooltipWidth - 20,
            targetRect.left + targetRect.width + gap
          ),
        }
      case 'top':
        return {
          bottom: window.innerHeight - targetRect.top + gap,
          left: Math.max(
            20,
            Math.min(
              window.innerWidth - tooltipWidth - 20,
              targetRect.left + targetRect.width / 2 - tooltipWidth / 2
            )
          ),
        }
      case 'bottom':
        return {
          top: targetRect.top + targetRect.height + gap,
          left: Math.max(
            20,
            Math.min(
              window.innerWidth - tooltipWidth - 20,
              targetRect.left + targetRect.width / 2 - tooltipWidth / 2
            )
          ),
        }
      default:
        return {}
    }
  }

  return (
    <div className={styles.overlay} aria-hidden="false">
      {/* Backdrop - clicking it skips the tour */}
      <div className={styles.backdrop} onClick={skip} />

      {/* Spotlight around target element */}
      {targetRect && (
        <div
          className={`${styles.spotlight} ${styles.spotlightPulse}`}
          style={{
            top: targetRect.top,
            left: targetRect.left,
            width: targetRect.width,
            height: targetRect.height,
          }}
        />
      )}

      {/* Arrow pointing to target */}
      {!isMobile && targetRect && (
        <OnboardingArrow
          direction={step.arrowDirection}
          style={getArrowPosition()}
        />
      )}

      {/* Tooltip with content */}
      <OnboardingTooltip
        step={step}
        currentStep={currentStep}
        totalSteps={totalSteps}
        onNext={next}
        onBack={back}
        onSkip={skip}
        style={getTooltipPosition()}
      />
    </div>
  )
}
