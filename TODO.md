# Improvement Ideas

## Quick Wins (1-2 hours each)

- [ ] **Sentiment Chart** - Add line chart showing sentiment evolution over simulation hours (data already captured, just not visualized)
- [ ] **Persona Impact in UI** - Display persona contribution breakdown from `src/analysis/impact.py` (already calculated, not shown)
- [ ] **Experiment Filtering/Sorting** - Add filter by outcome, sort by score, search by strategy to past experiments table
- [ ] **Show Risk Factors** - Display `risk_factors` and `reasoning` from idea generator (captured but hidden)

## Medium Effort (half day each)

- [ ] **Fix Double Simulation Bug** - `/simulate` endpoint runs simulation twice (lines 144-178 in main.py), doubles API cost
- [ ] **Experiment Comparison View** - Side-by-side comparison of two experiments
- [ ] **Strategy Performance Heatmap** - Cross-tabulate strategy × market condition performance
- [ ] **Tweet Drill-down** - Expose actual tweets from past experiments in UI (data exists, not shown)

## Solana Integration (Next Session)

- [ ] **Deploy to Devnet** - Run `anchor deploy --provider.cluster devnet` in WSL Ubuntu
- [ ] **Run Anchor Tests** - Run `anchor test` to verify staking program works

## Larger Features (1-3 days)

- [ ] **LLM Feedback Loop in UI** - Connect `llm_feedback/` module to web UI with "Improve This Token" button
- [ ] **Multi-Token Competition** - Simulate 2-3 tokens launching simultaneously
- [ ] **Batch/Scheduled Runs** - Queue experiments to run overnight with summary reports
