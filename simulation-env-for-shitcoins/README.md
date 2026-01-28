# Shitcoin Social Simulation Environment

Simulate how your token will perform on social media **before** you launch. Test narratives, memes, and timing in a sandbox with AI-powered crypto Twitter personas.

## Concept

Instead of launching blind and hoping for virality, run your token through a simulated CT (Crypto Twitter) environment:

- **AI Agents**: Degens, skeptics, whales, influencers, and normies react to your token
- **Viral Modeling**: See how your meme spreads (or doesn't)
- **Sentiment Tracking**: Measure hype, FUD, and engagement over simulated time
- **Iterate Fast**: Test 10 variations in an hour instead of burning money on failed launches

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY=your_key_here

# Run a simulation
python -m src.cli simulate --name "PEPE2" --ticker "PEPE2" --narrative "The sequel nobody asked for"
```

## Project Structure

```
src/
├── agents/          # AI persona definitions
├── models/          # Token and simulation data models
├── simulation/      # Core simulation engine
├── utils/           # Helpers and config
└── cli.py           # Command-line interface
```

## Token Configuration

Define your token in JSON or via CLI:

```json
{
  "name": "DogeKiller9000",
  "ticker": "DK9000",
  "narrative": "AI-powered meme coin that roasts other meme coins",
  "meme_style": "aggressive, edgy humor",
  "launch_timing": "bull market",
  "initial_liquidity": "50 SOL"
}
```

## Agent Personas

The simulation includes these CT archetypes:

| Persona | Behavior |
|---------|----------|
| **Degen** | Apes first, asks questions never. High engagement, low analysis. |
| **Skeptic** | Calls everything a rug. Provides FUD pressure. |
| **Whale** | Few words, big impact. Moves sentiment significantly. |
| **Influencer** | Chases clout. Will shill if momentum exists. |
| **Normie** | Follows the crowd. Amplifies existing sentiment. |

## Metrics

After simulation, you get:

- **Viral Coefficient**: How many new people each holder brings
- **Sentiment Arc**: Hype trajectory over time
- **FUD Resistance**: How well narrative survives skeptics
- **Predicted Outcome**: Based on similar historical patterns

## Roadmap

- [x] Core simulation engine
- [x] Basic agent personas
- [ ] Web UI for visual feed
- [ ] Historical data calibration
- [ ] Multi-token competition simulation
- [ ] Telegram/Discord simulation

## License

MIT
