# Cost Monitor

Analyze Snowflake credit consumption, expensive queries, warehouse utilization, and storage. Complements `snowflake-optimize` (performance) with a cost lens.

## When to Use

- "How much are we spending on Snowflake?"
- "Find our most expensive queries"
- "Which warehouses never suspend?"
- "Cost optimization recommendations"

## What It Does

- Credit usage by warehouse, user, query
- Top expensive queries (last 7/30 days)
- Always-on warehouse detection
- Storage cost breakdown
- Recommendations for cost reduction

## Setup

```bash
cp -r skills/cost-monitor ~/.snowflake/cortex/skills/
```

Then in Cortex Code: `/skill cost-monitor` or *"Run cost analysis"*.
