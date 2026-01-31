# 🧪 Hopium Lab

> *"The only token that passed its own simulation."*

Simulate how your token will perform on Crypto Twitter **before** you launch. Test narratives, memes, and timing in a sandbox with AI-powered personas.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Token Concept  │───▶│  CT Simulation   │───▶│  LLM Feedback   │
│  name/ticker/   │    │  personas react  │    │  iterate/refine │
│  narrative      │    │  viral spread    │    │  before launch  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                              │
         │         ┌──────────────────┐                 │
         └────────▶│ 🔬 Auto Harness  │◀────────────────┘
                   │  AI generates    │
                   │  ideas & tests   │
                   └──────────────────┘
```

---

## 📋 Table of Contents

- [Vision](#-vision)
- [Concept](#-concept)
- [Quick Start](#-quick-start)
- [CLI Commands](#-cli-commands)
- [Autonomous Harness](#-autonomous-harness)
- [Token Presets](#-token-presets)
- [LLM Feedback Loop](#-llm-feedback-loop)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Agent Personas](#-agent-personas)
- [Metrics](#-metrics)
- [Roadmap](#-roadmap)

---

## 🔮 Vision

Every day, thousands of tokens launch. Most fail within hours. The problem isn't lack of creativity—it's lack of testing.

**Hopium Lab** is a simulation engine that predicts how Crypto Twitter will react to a token *before* it launches. We model personas, sentiment dynamics, viral spread, and FUD resistance.

### The Meta-Narrative

This is inherently recursive: *a token for a platform that simulates tokens.*

The irony is the feature. **$HOPIUM** was the first token to run itself through its own simulation—and publish the results. If we can't pass our own test, why should anyone trust the platform?

### Self-Simulation Results

Before launch, we ran $HOPIUM through our own simulator:

| Metric | Result |
|--------|--------|
| Viral Coefficient | 7.2x |
| Peak Sentiment | +0.73 |
| FUD Resistance | 81% |
| Predicted Outcome | **Cult Classic** |
| Confidence | 67% |

**Key findings:**
- ✅ Meta-narrative resonates with CT irony
- ✅ Clear utility creates holder base
- ⚠️ "Simulation token" may seem niche
- ⚠️ Requires sustained platform usage

We publish this openly. If we're wrong, you'll know.

### The $HOPIUM Economy

| Action | Cost | Outcome |
|--------|------|---------|
| Run simulation | Stake $HOPIUM | Returned after sim (5% burned) |
| Predict outcomes | Bet $HOPIUM | Winners take pool (5% burned) |
| The Gauntlet | 2,500 $HOPIUM | Survive bear + skeptic swarm = 3x multiplier |

Deflationary by design. Every simulation burns tokens.

---

## 💡 Concept

Instead of launching blind and hoping for virality, run your token through a simulated CT environment:

| Feature | Description |
|---------|-------------|
| 🤖 **AI Agents** | Degens, skeptics, whales, influencers, KOLs react to your token |
| 📈 **Viral Modeling** | See how your meme spreads (or doesn't) |
| 💬 **Sentiment Tracking** | Measure hype, FUD, and engagement over time |
| 🔬 **Autonomous Harness** | AI generates and tests ideas automatically |
| 🔄 **LLM Feedback Loop** | AI evaluates your concept and suggests improvements |
| 💾 **Save & Export** | Persist simulations as JSON/CSV for analysis |
| ⚡ **Iterate Fast** | Test 10 variations in an hour instead of burning money |

---

## 🚀 Quick Start

### Option 1: Web UI

```bash
pip install -r requirements.txt
python run_api.py

# In another terminal
cd web && npm install && npm run dev
```
→ Open http://localhost:3000 (Twitter/X-style interface)

### Example Feed

The simulator generates a realistic Twitter/X-style feed with threaded conversations:

```
┌────────────────────────────────────────────────────────────────┐
│  🐋 0xWhale_                               @0xWhale_ · 2h      │
│  ──────────────────────────────────────────────────────────────│
│  $TEST                                                         │
│                                                                │
│  💬 12    🔁 45    ❤️ 892                                       │
├────────────────────────────────────────────────────────────────┤
│  │                                                             │
│  │  🎲 degen_spartan_ii              @degen_spartan · 2h       │
│  │  ────────────────────────────────────────────────────────── │
│  │  Replying to @0xWhale_                                      │
│  │  ser this is the way 🚀                                     │
│  │                                                             │
│  │  💬 3     🔁 8     ❤️ 156                                    │
├────────────────────────────────────────────────────────────────┤
│  🔍 NotYourLiquidity                   @NotYourLiq · 1h        │
│  ──────────────────────────────────────────────────────────────│
│  And this is why you DYOR on $TEST. Red flags everywhere.     │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ @degen_spartan · ser this is the way 🚀                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                │
│  💬 8     🔁 12    ❤️ 89                                        │
└────────────────────────────────────────────────────────────────┘
```

Personas interact with each other through **replies** (threaded) and **quote tweets** (embedded), creating realistic CT dynamics where skeptics challenge degens, normies ask questions, and whales spark engagement cascades.

### Option 2: CLI

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here  # optional, for AI responses

# Quick simulation with preset
python -m src.cli quick --preset doge

# Full simulation
python -m src.cli simulate \
  --name "PEPE2" \
  --ticker "PEPE2" \
  --narrative "The sequel nobody asked for"

# Compare tickers
python -m src.cli compare DOGE SHIB PEPE --narrative "classic meme"

# Run autonomous harness (AI generates & tests ideas)
python -m src.cli harness run --experiments 10 --mode balanced
```

---

## 🖥️ CLI Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `simulate` | Full simulation with all options | `--name X --ticker X --narrative "..."` |
| `quick` | Fast sim with minimal config | `quick WOJAK "sad frog"` |
| `quick --preset` | Use a preset template | `quick --preset ai` |
| `compare` | Compare multiple tickers | `compare DOGE SHIB PEPE` |
| `presets` | List available presets | `presets` |

### Harness Commands

| Command | Description | Example |
|---------|-------------|---------|
| `harness run` | Run autonomous experiments | `harness run -n 10 --mode explore` |
| `harness brainstorm` | Generate ideas around a theme | `harness brainstorm "AI dogs"` |
| `harness generate` | Generate ideas (no simulation) | `harness generate -n 5 -s contrarian` |
| `harness status` | Show experiment tracker status | `harness status` |
| `harness report` | Generate full experiment report | `harness report -o report.txt` |
| `harness learnings` | Show extracted insights | `harness learnings` |

---

## 🔬 Autonomous Harness

Let the AI generate and test token ideas automatically. The harness:

1. **Generates ideas** using LLM creativity (or fallback templates)
2. **Runs simulations** for each idea
3. **Tracks results** and calculates composite scores
4. **Learns** from successes/failures to improve future generation

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Generate   │────▶│  Simulate   │────▶│   Score     │────▶│   Learn     │
│   Ideas     │     │   Token     │     │  Results    │     │  Patterns   │
│             │     │             │     │             │     │             │
│ 6 strategies│     │ CT personas │     │ composite   │     │ adapt       │
│ LLM-powered │     │ react/tweet │     │ 0-100%      │     │ weights     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Run Modes

| Mode | Description |
|------|-------------|
| `explore` | Try diverse strategies, maximize learning |
| `exploit` | Focus on what's working |
| `balanced` | Mix of explore and exploit (default) |
| `targeted` | Focus on specific strategy or theme |

### Generation Strategies

| Strategy | Description |
|----------|-------------|
| `trend_chase` | Follow current CT meta (AI, dogs, etc.) |
| `contrarian` | Go against the current narrative |
| `remix` | Combine successful elements from past tokens |
| `avant_garde` | Experimental, boundary-pushing concepts |
| `nostalgia` | Throwback to early internet/meme culture |
| `topical` | Current events and news-driven |

### Examples

```bash
# Run 10 experiments in balanced mode
python -m src.cli harness run --experiments 10 --mode balanced

# Explore mode with bear market conditions
python -m src.cli harness run -n 20 --mode explore --market bear

# Targeted mode: only contrarian strategy
python -m src.cli harness run -n 5 --mode targeted --strategy contrarian

# Brainstorm around a theme and test all ideas
python -m src.cli harness brainstorm "cats vs dogs" --ideas 5 --test

# Generate ideas without running simulations
python -m src.cli harness generate -n 3 --strategy remix

# Check experiment history and top performers
python -m src.cli harness status

# Extract learnings from all experiments
python -m src.cli harness learnings
```

### Experiment Scoring

Ideas are scored (0-100%) based on:

| Factor | Weight |
|--------|--------|
| Viral Coefficient | 25% |
| Peak Sentiment | 20% |
| Sentiment Stability | 15% |
| FUD Resistance | 15% |
| Total Engagement | 15% |
| Predicted Outcome | 10% |

---

## 🎨 Token Presets

Pre-configured templates for common archetypes:

| Preset | Ticker | Style | Description |
|--------|--------|-------|-------------|
| `doge` | $DOGE | 🐕 Cute | Classic dog coin, wholesome community vibes |
| `ai` | $AGENT | 🤖 Topical | AI agent narrative, riding the hype wave |
| `pepe` | $PEPE | 🐸 Nostalgic | Iconic frog, classic meme culture |
| `cat` | $CAT | 🐱 Cute | Cat supremacy, anti-dog narrative |
| `edgy` | $EDGE | 🔪 Edgy | Dark humor for degen audiences |
| `meta` | $META | 🪞 Absurd | Self-aware ironic commentary |

```bash
# Use preset with custom ticker
python -m src.cli quick --preset pepe KEKE
```

---

## 🔁 LLM Feedback Loop

The feedback system evaluates concepts using synthetic simulation + LLM analysis:

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐     ┌──────────────┐
│   Concept    │────▶│   Simulate    │────▶│  LLM Eval    │────▶│   Iterate    │
│              │     │               │     │              │     │              │
│ name/ticker  │     │ CT personas   │     │ "weak hook"  │     │ refine until │
│ narrative    │     │ react & post  │     │ "FUD risk"   │     │ viable       │
│ hook         │     │ over N hours  │     │ "try X"      │     │              │
└──────────────┘     └───────────────┘     └──────────────┘     └──────────────┘
```

### Components

| Module | Purpose |
|--------|---------|
| `SimulationObserver` | Extracts state/metrics from running simulation |
| `LLMAnalyzer` | Sends context to Claude, parses structured feedback |
| `AdjustmentEngine` | Applies parameter changes with constraints |
| `FeedbackLoop` | Orchestrates observe → analyze → adjust cycle |
| `TokenEvaluator` | Quick concept evaluation without full sim |
| `CTConceptEvaluator` | Full CT simulation + LLM checkpoints |

### Examples

```bash
# Quick concept evaluation (no full sim)
python -m llm_feedback.examples.evaluate_concept

# Full CT simulation with LLM feedback
python -m llm_feedback.examples.run_ct_evaluation

# Synthetic market demo (works without API key with --mock)
python -m llm_feedback.examples.synthetic_market --mock
```

---

## 📁 Project Structure

```
├── src/
│   ├── agents/           # 🤖 AI persona definitions
│   │   └── personas.py   #    Degen, Skeptic, Whale, Influencer, etc.
│   ├── analysis/         # 📊 Post-simulation analysis
│   │   └── impact.py     #    Persona impact metrics
│   ├── api/              # 🌐 FastAPI backend
│   │   └── main.py       #    REST + SSE streaming endpoints
│   ├── harness/          # 🔬 Autonomous testing harness
│   │   ├── idea_generator.py   # LLM-powered idea generation
│   │   ├── runner.py           # AutonomousRunner orchestration
│   │   └── experiment.py       # ExperimentTracker & scoring
│   ├── models/           # 📦 Data models
│   │   └── token.py      #    Token, SimulationResult (Pydantic)
│   ├── presets/          # 🎨 Token templates
│   │   └── templates.py  #    doge, ai, pepe, cat, edgy, meta
│   ├── simulation/       # ⚙️ Core engine
│   │   └── engine.py     #    SimulationEngine, Tweet generation
│   ├── utils/            # 🔧 Utilities
│   │   ├── persistence.py#    Save/load simulations (JSON/CSV)
│   │   └── twitter.py    #    Twitter API integration
│   └── cli.py            # 💻 Command-line interface
│
├── llm_feedback/         # 🔁 LLM feedback loop system
│   ├── observer.py       #    State extraction
│   ├── analyzer.py       #    LLM analysis
│   ├── adjustments.py    #    Parameter adjustment
│   ├── feedback_loop.py  #    Orchestration
│   ├── token_evaluator.py#    Concept evaluation
│   ├── ct_integration.py #    CT simulation integration
│   └── examples/         #    Runnable demos
│
├── experiments/          # 📂 Experiment results storage
├── web/                  # 🖼️ Next.js frontend (Twitter/X style)
├── tests/                # 🧪 Test suite (92 tests)
├── run_api.py            # API server entrypoint
└── requirements.txt
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env`:

```bash
# Required for AI-powered responses
ANTHROPIC_API_KEY=your_anthropic_key

# Optional: Twitter data calibration
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_ACCESS_TOKEN=your_access_token
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulate` | POST | Run a full simulation |
| `/simulate/stream` | POST | **SSE stream** - real-time tweets as generated |
| `/market-sentiment` | GET | Current CT market sentiment |
| `/twitter-prior` | GET | Twitter data for a token |
| `/personas` | GET | List available personas |

### SSE Streaming

Stream tweets in real-time as they're generated:

```javascript
const eventSource = new EventSource('/simulate/stream', {
  method: 'POST',
  body: JSON.stringify({ token: { name: 'Test', ticker: 'TEST', narrative: '...' } })
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'tweet') {
    // New tweet generated
  } else if (data.type === 'done') {
    // Simulation complete
  }
};
```

---

## 🎭 Agent Personas

### Generic Archetypes

| Persona | Behavior | Sentiment |
|---------|----------|-----------|
| 🎲 **Degen** | Apes first, asks questions never | Bullish |
| 🔍 **Skeptic** | Calls everything a rug | Bearish |
| 🐋 **Whale** | Few words, big impact | Neutral |
| 📢 **Influencer** | Chases clout, shills momentum | Variable |
| 👤 **Normie** | Follows the crowd | Lagging |

### Real KOLs (from Kolscan)

- ansem (@blknoiz06)
- LilMoonLambo
- Groovy (@0xGroovy)
- Insyder (@insydercrypto)
- Monarch (@MonarchBTC)
- ShockedJS
- Levis (@LevisNFT)
- Hail (@ignHail)

---

## 📊 Metrics

After simulation:

| Metric | Description |
|--------|-------------|
| **Viral Coefficient** | Engagement multiplier (1.0 = baseline) |
| **Peak Sentiment** | Maximum hype reached (-1.0 to +1.0) |
| **Sentiment Stability** | How steady the sentiment held |
| **FUD Resistance** | Survival rate against skeptics (0-100%) |
| **Hours to Peak** | Time to maximum engagement |
| **Hours to Death** | Time until interest collapsed (if any) |
| **Predicted Outcome** | `moon` / `cult_classic` / `pump_and_dump` / `slow_bleed` / `rug` |
| **Dominant Narrative** | What CT ended up calling your token |

### Persona Impact Analysis

```bash
# See which personas drove engagement
python -m src.cli impact <simulation_file>
```

Output shows per-persona breakdown:
- Tweet count & average sentiment
- Engagement share (%)
- Hype drivers vs FUD sources

---

## 🗺️ Roadmap

- [x] Core simulation engine
- [x] Basic agent personas
- [x] Real KOL personas
- [x] Web UI for visual feed
- [x] Twitter/X style UI redesign
- [x] FastAPI backend
- [x] SSE streaming for real-time tweets
- [x] Twitter API integration
- [x] Save/export simulation runs
- [x] Token preset templates
- [x] LLM feedback loop
- [x] Persona impact analysis
- [x] Autonomous testing harness
- [x] AI-powered idea generation
- [x] Experiment tracking & learnings
- [x] Market condition effects
- [x] Harness dashboard in web UI
- [x] Tweet interactions (replies & quotes)
- [ ] Historical data calibration
- [ ] Multi-token competition simulation
- [ ] Telegram/Discord simulation
- [ ] Prediction markets integration
- [ ] The Gauntlet mode

---

## 📄 License

MIT
