# Snowflake Performance Analysis

**When queries are slow or costs are high.** Uses `QUERY_HISTORY` and `WAREHOUSE_METERING_HISTORY` to find spilling, poor pruning, low cache hit rates, and queue delays—then recommends concrete fixes.

---

## Install

```bash
cp -r skills/snowflake-optimize ~/.snowflake/cortex/skills/
```

**Invoke with:** *"Why is this query slow?"*, *"Optimize warehouse sizing"*, *"Analyze query performance"*, *"Reduce Snowflake costs"*

---

## What It Analyzes

| Area | Metrics | What it means |
|------|---------|---------------|
| **Query profile** | Spilling, cache hit %, partition pruning, queue times | Single-query bottlenecks |
| **Warehouse usage** | Spilling frequency, queue delays, cache hit rate | Sizing and concurrency |
| **Tables** | Partition scan %, clustering | Pruning and clustering effectiveness |
| **Cost** | Credits by warehouse | Spend and optimization targets |

---

## Issues → Fixes (Quick Reference)

| Issue | Evidence | Fix |
|-------|----------|-----|
| **Memory spilling** | `bytes_spilled_* > 0` | Increase warehouse size or simplify query |
| **Poor partition pruning** | High `partitions_scanned/total` | Add clustering key; filter on cluster column |
| **Low cache hit** | `percentage_scanned_from_cache < 50%` | Increase auto-suspend; consolidate similar queries |
| **Queue delays** | `queued_overload_time > 0` | Enable multi-cluster or increase `max_cluster_count` |
| **Long compilation** | `compilation_time > execution_time` | Simplify query; use CTEs; materialize intermediates |

---

## Warehouse Sizing Guide

| Situation | Action |
|-----------|--------|
| Consistent spilling, slow queries | **Size up** (larger warehouse) |
| Queue delays, high concurrency | **Scale out** (multi-cluster) |
| No spilling, low utilization | **Size down** (cost optimization) |

---

## Sample Output

```
🚀 SNOWFLAKE PERFORMANCE ANALYSIS

SCOPE: Query abc123 | TIMEFRAME: Last 7 days

📊 FINDINGS:
- Total time: 45s | Cache hit: 23% | Partitions: 450/500 (90%)
- Spilling: 850 MB to remote storage

⚠️ ISSUES:
1. Memory spilling (HIGH) → Increase warehouse MEDIUM → LARGE
2. Poor partition pruning (MEDIUM) → Add clustering on DATE_COLUMN
3. Low cache hit (MEDIUM) → Increase auto-suspend to 300s

💡 RECOMMENDATIONS:
- Immediate: Size up warehouse (≈65% faster)
- Long-term: Clustering key + longer auto-suspend

💰 COST: $1,200/mo → Est. savings $300/mo (25%)
```

---

## Snowflake Features to Consider

- **Query Acceleration Service** — Variable execution times
- **Search Optimization** — Point lookups, selective filters
- **Materialized views** — Repeated expensive aggregations
- **Clustering keys** — Large tables with common filters
- **Result caching** — Automatic; ensure it’s utilized

---

## Tips

- **Baseline first** — Capture metrics before changing anything.
- **Prioritize impact** — Slow queries > cost > minor tweaks.
- **Validate changes** — Compare before/after metrics.
- **ACCOUNT_USAGE lag** — 45 min–3 hr; use `INFORMATION_SCHEMA.QUERY_HISTORY()` for near real-time.

---

## Troubleshooting

**Insufficient permissions:**  
`GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <role>;`

**Large result sets:**  
Filter by `start_time` and `warehouse_name` to narrow scope.

---

## Related Skills

- **snowflake-diagnose** — Connection and permission issues
- **quality-check** — Validate SQL before running
