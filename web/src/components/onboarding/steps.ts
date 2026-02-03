export interface OnboardingStep {
  id: string
  targetSelector: string
  mobileTargetSelector?: string
  arrowDirection: 'left' | 'right' | 'up' | 'down'
  tooltipPosition: 'left' | 'right' | 'top' | 'bottom'
  title: string
  body: string
  hint?: string
  icon: string
}

export interface PageOnboarding {
  steps: OnboardingStep[]
  storageKey: string
}

// Home page steps
const HOME_STEPS: OnboardingStep[] = [
  {
    id: 'welcome',
    targetSelector: '[data-onboarding="wallet"]',
    mobileTargetSelector: '[data-onboarding="mobile-wallet"]',
    arrowDirection: 'left',
    tooltipPosition: 'right',
    title: 'Welcome to Hopium Lab!',
    body: 'First, connect your wallet to get started. This gives you demo $HOPIUM tokens to run simulations.',
    icon: '👋',
  },
  {
    id: 'ticker',
    targetSelector: '[data-onboarding="ticker"]',
    mobileTargetSelector: '[data-onboarding="ticker"]',
    arrowDirection: 'left',
    tooltipPosition: 'right',
    title: 'Create Your Token',
    body: 'Give your meme coin a ticker symbol (like $PEPE or $DOGE) and describe its narrative. This is what CT will react to.',
    hint: 'Ticker and Narrative are required fields',
    icon: '🪙',
  },
  {
    id: 'style',
    targetSelector: '[data-onboarding="meme-style"]',
    mobileTargetSelector: '[data-onboarding="meme-style"]',
    arrowDirection: 'left',
    tooltipPosition: 'right',
    title: 'Fine-tune the Vibe',
    body: 'Choose a meme style and market condition. These affect how the simulated personas react to your token.',
    icon: '🎨',
  },
  {
    id: 'simulate',
    targetSelector: '[data-onboarding="simulate-btn"]',
    mobileTargetSelector: '[data-onboarding="simulate-btn"]',
    arrowDirection: 'up',
    tooltipPosition: 'top',
    title: 'Launch the Simulation',
    body: 'Click here to stake demo $HOPIUM and watch AI personas react to your token in real-time. Higher stakes = more simulation hours.',
    icon: '🚀',
  },
  {
    id: 'results',
    targetSelector: '.main-feed',
    mobileTargetSelector: '.main-feed',
    arrowDirection: 'right',
    tooltipPosition: 'left',
    title: 'Watch the Chaos Unfold',
    body: 'Simulated tweets appear here as CT personas react to your token. After completion, check the Results Card for metrics and predictions.',
    icon: '📊',
  },
]

// Lab page steps
const LAB_STEPS: OnboardingStep[] = [
  {
    id: 'lab-welcome',
    targetSelector: '[data-onboarding="lab-header"]',
    arrowDirection: 'down',
    tooltipPosition: 'bottom',
    title: 'Welcome to Harness Lab!',
    body: 'Run autonomous experiments that generate and test token ideas while you sleep. The AI learns what works best over time.',
    icon: '🧪',
  },
  {
    id: 'lab-mode',
    targetSelector: '[data-onboarding="lab-mode"]',
    arrowDirection: 'right',
    tooltipPosition: 'left',
    title: 'Choose Your Strategy',
    body: 'Balanced explores new ideas while exploiting winners. Explore maximizes learning. Exploit focuses on proven patterns. Targeted tests a specific theme.',
    icon: '🎯',
  },
  {
    id: 'lab-experiments',
    targetSelector: '[data-onboarding="lab-experiments"]',
    arrowDirection: 'right',
    tooltipPosition: 'left',
    title: 'Set Experiment Count',
    body: 'Each experiment costs 50 $HOPIUM. Run more experiments to discover more winning patterns, but it takes longer.',
    hint: 'Start with 3-5 experiments to learn the system',
    icon: '🔢',
  },
  {
    id: 'lab-launch',
    targetSelector: '[data-onboarding="lab-launch"]',
    arrowDirection: 'up',
    tooltipPosition: 'top',
    title: 'Launch the Harness',
    body: 'Stake your $HOPIUM and let the AI run experiments autonomously. Watch results stream in real-time or check back later.',
    icon: '🚀',
  },
  {
    id: 'lab-leaderboard',
    targetSelector: '[data-onboarding="lab-leaderboard"]',
    arrowDirection: 'right',
    tooltipPosition: 'left',
    title: 'Track Top Performers',
    body: 'The leaderboard shows which token concepts performed best. Use these insights to inform your own token designs.',
    icon: '🏆',
  },
  {
    id: 'lab-history',
    targetSelector: '[data-onboarding="lab-history"]',
    arrowDirection: 'down',
    tooltipPosition: 'bottom',
    title: 'Review Past Experiments',
    body: 'All experiments are saved here. Filter by outcome, strategy, or sort by score to find patterns in what works.',
    icon: '📚',
  },
]

// Whitepaper page steps
const WHITEPAPER_STEPS: OnboardingStep[] = [
  {
    id: 'wp-welcome',
    targetSelector: '[data-onboarding="wp-progress"]',
    arrowDirection: 'down',
    tooltipPosition: 'bottom',
    title: 'The $HOPIUM Whitepaper',
    body: 'Read about the tokenomics, simulation engine, and roadmap. Your reading progress is tracked at the top.',
    icon: '📄',
  },
  {
    id: 'wp-thread',
    targetSelector: '[data-onboarding="wp-thread"]',
    arrowDirection: 'right',
    tooltipPosition: 'left',
    title: 'Twitter-Style Thread',
    body: 'The whitepaper is presented as a Twitter thread for easy reading. Scroll through to learn about $HOPIUM.',
    icon: '🧵',
  },
  {
    id: 'wp-download',
    targetSelector: '[data-onboarding="wp-download"]',
    arrowDirection: 'up',
    tooltipPosition: 'top',
    title: 'Download the PDF',
    body: 'Want a traditional whitepaper? Download the full PDF version for offline reading or sharing.',
    icon: '📥',
  },
]

// Map routes to their onboarding configs
export const PAGE_ONBOARDING: Record<string, PageOnboarding> = {
  '/': {
    steps: HOME_STEPS,
    storageKey: 'hopium_onboarding_home',
  },
  '/lab': {
    steps: LAB_STEPS,
    storageKey: 'hopium_onboarding_lab',
  },
  '/whitepaper': {
    steps: WHITEPAPER_STEPS,
    storageKey: 'hopium_onboarding_whitepaper',
  },
}

export const CURRENT_VERSION = '1.0.0'

// Helper to get steps for a given path
export function getOnboardingForPath(pathname: string): PageOnboarding | null {
  return PAGE_ONBOARDING[pathname] || null
}
