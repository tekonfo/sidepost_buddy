# Strategy Council Prompts

会議開始時は以下の順で `council send` を実行する。

1. pane0: `orchestrator.md`
2. pane1: `content_strategist.md`
3. pane2: `execution_risk.md`
4. pane3: `market_distribution.md`
5. pane1-3: `round1_proposal.md`
6. pane1-3: `round2_critique.md`
7. pane1-3: `round3_consensus.md`

例:

```bash
council send sp-council 0 01_workflow/prompts/strategy_council/orchestrator.md
council send sp-council 1 01_workflow/prompts/strategy_council/content_strategist.md
council send sp-council 2 01_workflow/prompts/strategy_council/execution_risk.md
council send sp-council 3 01_workflow/prompts/strategy_council/market_distribution.md
```
