# Improvement Ideas

## Quick Wins (1-2 hours each)

- [x] **Sentiment Chart** - Add line chart showing sentiment evolution over simulation hours (data already captured, just not visualized)
- [x] **Persona Impact in UI** - Display persona contribution breakdown from `src/analysis/impact.py` (already calculated, not shown)
- [x] **Experiment Filtering/Sorting** - Add filter by outcome, sort by score, search by strategy to past experiments table
- [x] **Show Risk Factors** - Display `risk_factors` and `reasoning` from idea generator (captured but hidden)

## Medium Effort (half day each)

- [ ] **Fix Double Simulation Bug** - `/simulate` endpoint runs simulation twice (lines 144-178 in main.py), doubles API cost
- [ ] **Experiment Comparison View** - Side-by-side comparison of two experiments
- [ ] **Strategy Performance Heatmap** - Cross-tabulate strategy × market condition performance
- [ ] **Tweet Drill-down** - Expose actual tweets from past experiments in UI (data exists, not shown)

## Solana Integration (Next Session)

- [x] **Program Build** - `anchor build` succeeds with Anchor 0.32.0
- [x] **Program ID Synced** - Updated to `GFZLBYNKT7aaGncQ5rL3yGC1zjGF71zLCwceh73Y23nC`
- [x] **WSL2 Upgrade** - Ubuntu upgraded to WSL2 for better compatibility
- [ ] **Get Devnet SOL** - Request airdrop at https://faucet.solana.com for wallet `6Q9vBhmSqwqHLAhcwJS953N8TcKTKQKCsPP9R3bWUjhz` (need ~2-3 SOL)
- [ ] **Deploy to Devnet** - After getting SOL, run:
  ```bash
  wsl -d Ubuntu bash -l -c "cd '/mnt/c/Users/micha/Programming Work/simulation-env-for-shitcoins' && anchor deploy --provider.cluster devnet"
  ```
- [ ] **Run Anchor Tests** - Solana 3.x requires io_uring (not supported on WSL2). Options:
  - Use native Linux/macOS
  - Downgrade: `solana-install init 2.0.21`
  - Test on devnet after deployment

## Larger Features (1-3 days)

- [x] **LLM Feedback Loop in UI** - Connect `llm_feedback/` module to web UI with "Improve This Token" button
- [x] **Multi-Token Competition** - Simulate 2-3 tokens launching simultaneously
- [ ] **Batch/Scheduled Runs** - Queue experiments to run overnight with summary reports
