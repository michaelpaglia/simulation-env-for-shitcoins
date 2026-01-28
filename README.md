# 🎰 Shitcoin Social Simulation Environment

Simulate how your token will perform on Crypto Twitter **before** you launch. Test narratives, memes, and timing in a sandbox with AI-powered personas.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Token Concept  │───▶│  CT Simulation   │───▶│  LLM Feedback   │
│  name/ticker/   │    │  personas react  │    │  iterate/refine │
│  narrative      │    │  viral spread    │    │  before launch  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## 📋 Table of Contents

- [Concept](#-concept)
- [Quick Start](#-quick-start)
- [CLI Commands](#-cli-commands)
- [Token Presets](#-token-presets)
- [LLM Feedback Loop](#-llm-feedback-loop)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [API Endpoints](#-api-endpoints)
- [Agent Personas](#-agent-personas)
- [Metrics](#-metrics)
- [Roadmap](#-roadmap)

---

## 💡 Concept

Instead of launching blind and hoping for virality, run your token through a simulated CT environment:

| Feature | Description |
|---------|-------------|
| 🤖 **AI Agents** | Degens, skeptics, whales, influencers, KOLs react to your token |
| 📈 **Viral Modeling** | See how your meme spreads (or doesn't) |
| 💬 **Sentiment Tracking** | Measure hype, FUD, and engagement over time |
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
→ Open http://localhost:3000

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
```

---

## 🖥️ CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `simulate` | Full simulation with all options | `--name X --ticker X --narrative "..."` |
| `quick` | Fast sim with minimal config | `quick WOJAK "sad frog"` |
| `quick --preset` | Use a preset template | `quick --preset ai` |
| `compare` | Compare multiple tickers | `compare DOGE SHIB PEPE` |
| `presets` | List available presets | `presets` |

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
│   │   └── main.py       #    REST endpoints
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
├── web/                  # 🖼️ Next.js frontend
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
| `/market-sentiment` | GET | Current CT market sentiment |
| `/twitter-prior` | GET | Twitter data for a token |
| `/personas` | GET | List available personas |

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
- [x] FastAPI backend
- [x] Twitter API integration
- [x] Save/export simulation runs
- [x] Token preset templates
- [x] LLM feedback loop
- [x] Persona impact analysis
- [ ] Historical data calibration
- [ ] Multi-token competition simulation
- [ ] Telegram/Discord simulation

---

## 📄 License

MIT
