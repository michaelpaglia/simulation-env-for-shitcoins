'use client'

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react'
import { usePathname } from 'next/navigation'
import { getOnboardingForPath, CURRENT_VERSION } from './steps'

interface OnboardingState {
  isActive: boolean
  currentStep: number
  totalSteps: number
  hasCompleted: boolean
  currentPage: string
}

interface OnboardingActions {
  start: () => void
  next: () => void
  back: () => void
  skip: () => void
  complete: () => void
  goToStep: (step: number) => void
}

type OnboardingContextType = OnboardingState & OnboardingActions

const OnboardingContext = createContext<OnboardingContextType | null>(null)

export function useOnboarding() {
  const context = useContext(OnboardingContext)
  if (!context) {
    throw new Error('useOnboarding must be used within an OnboardingProvider')
  }
  return context
}

interface OnboardingProviderProps {
  children: ReactNode
}

export function OnboardingProvider({ children }: OnboardingProviderProps) {
  const pathname = usePathname()
  const [isActive, setIsActive] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const [hasCompleted, setHasCompleted] = useState(true)
  const [mounted, setMounted] = useState(false)

  const pageOnboarding = getOnboardingForPath(pathname)
  const totalSteps = pageOnboarding?.steps.length ?? 0
  const storageKey = pageOnboarding?.storageKey ?? ''
  const versionKey = `${storageKey}_version`
  const stepKey = `${storageKey}_step`

  // Check localStorage on mount and route change
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted || !pageOnboarding) return

    const completed = localStorage.getItem(storageKey)
    const version = localStorage.getItem(versionKey)
    const savedStep = localStorage.getItem(stepKey)

    // Reset if version changed or never completed for this page
    if (!completed || version !== CURRENT_VERSION) {
      setHasCompleted(false)
      setCurrentStep(0)
      // Auto-start for new users after a short delay
      const timer = setTimeout(() => {
        setIsActive(true)
      }, 1000)
      return () => clearTimeout(timer)
    } else {
      setHasCompleted(true)
      setIsActive(false)
    }

    // Resume from saved step if available
    if (savedStep) {
      const step = parseInt(savedStep, 10)
      if (!isNaN(step) && step >= 0 && step < totalSteps) {
        setCurrentStep(step)
      }
    }
  }, [mounted, pathname, pageOnboarding, storageKey, versionKey, stepKey, totalSteps])

  // Save current step to localStorage
  useEffect(() => {
    if (mounted && isActive && stepKey) {
      localStorage.setItem(stepKey, currentStep.toString())
    }
  }, [currentStep, isActive, mounted, stepKey])

  const start = useCallback(() => {
    if (!pageOnboarding) return
    setCurrentStep(0)
    setIsActive(true)
    setHasCompleted(false)
  }, [pageOnboarding])

  const next = useCallback(() => {
    if (!pageOnboarding) return

    if (currentStep < totalSteps - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      // Complete on last step
      setIsActive(false)
      setHasCompleted(true)
      localStorage.setItem(storageKey, 'true')
      localStorage.setItem(versionKey, CURRENT_VERSION)
      localStorage.removeItem(stepKey)
    }
  }, [currentStep, totalSteps, pageOnboarding, storageKey, versionKey, stepKey])

  const back = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }, [currentStep])

  const skip = useCallback(() => {
    if (!storageKey) return
    setIsActive(false)
    setHasCompleted(true)
    localStorage.setItem(storageKey, 'true')
    localStorage.setItem(versionKey, CURRENT_VERSION)
    localStorage.removeItem(stepKey)
  }, [storageKey, versionKey, stepKey])

  const complete = useCallback(() => {
    skip()
  }, [skip])

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < totalSteps) {
      setCurrentStep(step)
    }
  }, [totalSteps])

  const value: OnboardingContextType = {
    isActive,
    currentStep,
    totalSteps,
    hasCompleted,
    currentPage: pathname,
    start,
    next,
    back,
    skip,
    complete,
    goToStep,
  }

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  )
}
