# Shitcoin Social Simulation Environment

Simulate how your token will perform on social media **before** you launch. Test narratives, memes, and timing in a sandbox with AI-powered crypto Twitter personas.

## Concept

Instead of launching blind and hoping for virality, run your token through a simulated CT (Crypto Twitter) environment:

- **AI Agents**: Degens, skeptics, whales, influencers, KOLs, and normies react to your token
- **Viral Modeling**: See how your meme spreads (or doesn't)
- **Sentiment Tracking**: Measure hype, FUD, and engagement over simulated time
- **Real Data Calibration**: Optionally use live Twitter data to calibrate simulations
- **Iterate Fast**: Test 10 variations in an hour instead of burning money on failed launches

## Quick Start

### Option 1: Web UI (Recommended)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the API server
python run_api.py

# In another terminal, start the web UI
cd web
npm install
npm run dev
```

Open http://localhost:3000 to use the simulator.

### Option 2: CLI

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key (optional, for AI-powered responses)
export ANTHROPIC_API_KEY=your_key_here

# Run a simulation
python -m src.cli simulate --name "PEPE2" --ticker "PEPE2" --narrative "The sequel nobody asked for"

# Quick simulation
python -m src.cli quick WOJAK "sad frog energy"

# Compare multiple tickers
python -m src.cli compare DOGE SHIB PEPE --narrative "classic meme"
```

## Project Structure

```
├── src/
│   ├── agents/          # AI persona definitions (including real KOLs)
│   ├── api/             # FastAPI backend
│   ├── models/          # Token and simulation data models
│   ├── simulation/      # Core simulation engine
│   ├── utils/           # Twitter integration, helpers
│   └── cli.py           # Command-line interface
├── web/                 # Next.js frontend
├── run_api.py           # API server entrypoint
└── requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and fill in your keys:

```bash
# For AI-powered tweet generation (Claude)
ANTHROPIC_API_KEY=your_anthropic_key

# For real Twitter data calibration (optional)
TWITTER_BEARER_TOKEN=your_bearer_token
TWITTER_CONSUMER_KEY=your_consumer_key
TWITTER_ACCESS_TOKEN=your_access_token
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulate` | POST | Run a full simulation |
| `/market-sentiment` | GET | Get current CT market sentiment |
| `/twitter-prior` | GET | Get Twitter data for a token |
| `/personas` | GET | List available personas |

## Agent Personas

The simulation includes generic CT archetypes plus real KOLs:

**Generic Archetypes:**
| Persona | Behavior |
|---------|----------|
| Degen | Apes first, asks questions never |
| Skeptic | Calls everything a rug |
| Whale | Few words, big impact |
| Influencer | Chases clout, shills momentum |
| Normie | Follows the crowd |

**Real KOLs (from Kolscan):**
- ansem (@blknoiz06)
- LilMoonLambo
- Groovy (@0xGroovy)
- Insyder (@insydercrypto)
- Monarch (@MonarchBTC)
- ShockedJS
- Levis (@LevisNFT)
- Hail (@ignHail)

## Metrics

After simulation, you get:

- **Viral Coefficient**: Engagement multiplier
- **Peak Sentiment**: Maximum hype reached
- **FUD Resistance**: How well narrative survives skeptics
- **Predicted Outcome**: moon, cult_classic, pump_and_dump, slow_bleed, or rug
- **CT Verdict**: What the simulated CT ended up calling your token

## Roadmap

- [x] Core simulation engine
- [x] Basic agent personas
- [x] Real KOL personas
- [x] Web UI for visual feed
- [x] FastAPI backend
- [x] Twitter API integration
- [ ] Historical data calibration
- [ ] Multi-token competition simulation
- [ ] Telegram/Discord simulation
- [ ] Save/export simulation runs

## License

MIT
