'use client'

import styles from './Onboarding.module.css'

interface OnboardingArrowProps {
  direction: 'left' | 'right' | 'up' | 'down'
  style?: React.CSSProperties
}

export function OnboardingArrow({ direction, style }: OnboardingArrowProps) {
  const directionClass = {
    left: styles.arrowLeft,
    right: styles.arrowRight,
    up: styles.arrowUp,
    down: styles.arrowDown,
  }[direction]

  // SVG arrow pointing right (rotated by CSS for other directions)
  const getArrowPath = () => {
    switch (direction) {
      case 'right':
        return 'M8 16L24 16M24 16L16 8M24 16L16 24'
      case 'left':
        return 'M24 16L8 16M8 16L16 8M8 16L16 24'
      case 'up':
        return 'M16 24L16 8M16 8L8 16M16 8L24 16'
      case 'down':
        return 'M16 8L16 24M16 24L8 16M16 24L24 16'
      default:
        return 'M8 16L24 16M24 16L16 8M24 16L16 24'
    }
  }

  return (
    <div className={`${styles.arrow} ${directionClass}`} style={style}>
      <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d={getArrowPath()}
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
  )
}
