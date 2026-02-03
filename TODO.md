# Improvement Ideas

## Quick Wins (1-2 hours each)

- [x] **Sentiment Chart** - Add line chart showing sentiment evolution over simulation hours (data already captured, just not visualized)
- [x] **Persona Impact in UI** - Display persona contribution breakdown from `src/analysis/impact.py` (already calculated, not shown)
- [x] **Experiment Filtering/Sorting** - Add filter by outcome, sort by score, search by strategy to past experiments table
- [x] **Show Risk Factors** - Display `risk_factors` and `reasoning` from idea generator (captured but hidden)

## Medium Effort (half day each)

- [x] **API Cost Optimizations** - Implemented prompt caching, reduced max_tokens, switched idea generator to Haiku, fixed competition duplication (40-70% cost reduction)
- [ ] **Experiment Comparison View** - Side-by-side comparison of two experiments
- [ ] **Strategy Performance Heatmap** - Cross-tabulate strategy × market condition performance
- [ ] **Tweet Drill-down** - Expose actual tweets from past experiments in UI (data exists, not shown)

## Solana Integration (Next Session)

- [x] **Program Build** - `anchor build` succeeds with Anchor 0.32.0
- [x] **Program ID Synced** - Updated to `GFZLBYNKT7aaGncQ5rL3yGC1zjGF71zLCwceh73Y23nC`
- [x] **WSL2 Upgrade** - Ubuntu upgraded to WSL2 for better compatibility
- [x] **Get Devnet SOL** - Claimed 2.5 SOL for wallet `6Q9vBhmSqwqHLAhcwJS953N8TcKTKQKCsPP9R3bWUjhz`
- [x] **Add Test Config** - Added missing `package.json` and `tsconfig.json` for Anchor tests
- [ ] **Install Test Dependencies** - Run in Ubuntu terminal:
  ```bash
  cd '/mnt/c/Users/micha/Programming Work/simulation-env-for-shitcoins'
  yarn install
  ```
- [ ] **Deploy to Devnet** - Run in Ubuntu terminal:
  ```bash
  anchor deploy --provider.cluster devnet
  ```
- [ ] **Run Anchor Tests** - Run in Ubuntu terminal:
  ```bash
  anchor test --skip-local-validator
  ```
  Note: WSL commands hang when invoked from Windows terminal. Must run directly in Ubuntu desktop app.

## Larger Features (1-3 days)

- [x] **LLM Feedback Loop in UI** - Connect `llm_feedback/` module to web UI with "Improve This Token" button
- [x] **Multi-Token Competition** - Simulate 2-3 tokens launching simultaneously
- [x] **UI Polish** - Cleaned up visual clutter, removed AI-gen feel, better typography and spacing
- [ ] **Batch/Scheduled Runs** - Queue experiments to run overnight with summary reports

## Completed Optimizations

- [x] **Prompt Caching** - Added Anthropic prompt caching (50-90% savings at scale)
- [x] **Model Selection** - Switched idea generator to Haiku (90% cost reduction)
- [x] **Competition Engine Fix** - Single shared engine instead of N engines (60% cost reduction)
- [x] **Engine Pooling** - Reuse API connections across requests
- [x] **Hot Tweet Optimization** - O(n) → O(k) lookup performance
- [x] **Token Reduction** - Reduced max_tokens from 1000 to 700 (20-40% savings)
- [x] **Favicon & Metadata** - Added test tube favicon and improved site metadata
- [x] **Security Audit** - Verified no hardcoded secrets, documented npm vulnerabilities
