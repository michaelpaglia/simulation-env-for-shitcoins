import { useMemo } from 'react'
import { TweetData } from './Tweet'

interface SentimentChartProps {
  tweets: TweetData[]
}

export function SentimentChart({ tweets }: SentimentChartProps) {
  const chartData = useMemo(() => {
    if (tweets.length === 0) return []

    // Group tweets by hour and calculate average sentiment
    const byHour: Record<number, { total: number; count: number }> = {}
    tweets.forEach(tweet => {
      if (!byHour[tweet.hour]) {
        byHour[tweet.hour] = { total: 0, count: 0 }
      }
      byHour[tweet.hour].total += tweet.sentiment
      byHour[tweet.hour].count += 1
    })

    // Convert to array and calculate averages
    const maxHour = Math.max(...Object.keys(byHour).map(Number))
    const data: { hour: number; sentiment: number }[] = []

    for (let h = 0; h <= maxHour; h++) {
      const entry = byHour[h]
      data.push({
        hour: h,
        sentiment: entry ? entry.total / entry.count : 0,
      })
    }

    return data
  }, [tweets])

  if (chartData.length < 2) return null

  // Chart dimensions
  const width = 280
  const height = 100
  const padding = { top: 10, right: 10, bottom: 20, left: 30 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Scale functions
  const xScale = (hour: number) =>
    padding.left + (hour / (chartData.length - 1)) * chartWidth
  const yScale = (sentiment: number) =>
    padding.top + ((1 - sentiment) / 2) * chartHeight // -1 to 1 range

  // Generate path
  const pathD = chartData
    .map((d, i) => `${i === 0 ? 'M' : 'L'} ${xScale(d.hour)} ${yScale(d.sentiment)}`)
    .join(' ')

  // Generate area path (filled below the line)
  const areaD =
    pathD +
    ` L ${xScale(chartData.length - 1)} ${yScale(0)} L ${xScale(0)} ${yScale(0)} Z`

  // Find peak and trough
  const maxSentiment = Math.max(...chartData.map(d => d.sentiment))
  const minSentiment = Math.min(...chartData.map(d => d.sentiment))

  return (
    <div style={{ marginTop: '12px' }}>
      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
        Sentiment Over Time
      </div>
      <svg width={width} height={height} style={{ display: 'block' }}>
        {/* Grid lines */}
        <line
          x1={padding.left}
          y1={yScale(0)}
          x2={width - padding.right}
          y2={yScale(0)}
          stroke="var(--border)"
          strokeDasharray="4,4"
        />
        <line
          x1={padding.left}
          y1={yScale(0.5)}
          x2={width - padding.right}
          y2={yScale(0.5)}
          stroke="var(--border)"
          strokeDasharray="2,4"
          opacity={0.5}
        />
        <line
          x1={padding.left}
          y1={yScale(-0.5)}
          x2={width - padding.right}
          y2={yScale(-0.5)}
          stroke="var(--border)"
          strokeDasharray="2,4"
          opacity={0.5}
        />

        {/* Area fill */}
        <path
          d={areaD}
          fill="url(#sentimentGradient)"
          opacity={0.3}
        />

        {/* Gradient definition */}
        <defs>
          <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--success)" />
            <stop offset="50%" stopColor="var(--text-secondary)" />
            <stop offset="100%" stopColor="var(--danger)" />
          </linearGradient>
        </defs>

        {/* Line */}
        <path
          d={pathD}
          fill="none"
          stroke="var(--accent)"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Y-axis labels */}
        <text x={padding.left - 5} y={yScale(1)} fontSize={10} fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">
          +1
        </text>
        <text x={padding.left - 5} y={yScale(0)} fontSize={10} fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">
          0
        </text>
        <text x={padding.left - 5} y={yScale(-1)} fontSize={10} fill="var(--text-secondary)" textAnchor="end" dominantBaseline="middle">
          -1
        </text>

        {/* X-axis labels */}
        <text x={xScale(0)} y={height - 5} fontSize={10} fill="var(--text-secondary)" textAnchor="middle">
          0h
        </text>
        <text x={xScale(chartData.length - 1)} y={height - 5} fontSize={10} fill="var(--text-secondary)" textAnchor="middle">
          {chartData.length - 1}h
        </text>

        {/* Peak/trough markers */}
        {chartData.map((d, i) => {
          if (d.sentiment === maxSentiment && maxSentiment > 0.3) {
            return (
              <circle
                key={`peak-${i}`}
                cx={xScale(d.hour)}
                cy={yScale(d.sentiment)}
                r={4}
                fill="var(--success)"
              />
            )
          }
          if (d.sentiment === minSentiment && minSentiment < -0.3) {
            return (
              <circle
                key={`trough-${i}`}
                cx={xScale(d.hour)}
                cy={yScale(d.sentiment)}
                r={4}
                fill="var(--danger)"
              />
            )
          }
          return null
        })}
      </svg>
    </div>
  )
}
