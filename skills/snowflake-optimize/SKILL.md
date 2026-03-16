---
name: snowflake-optimize
description: Analyzes Snowflake query performance, warehouse sizing, spilling, partition pruning, cache hit rates, and cost. Use when the user asks "why is this query slow", "optimize performance", "analyze query", "check warehouse utilization", "reduce costs", "memory spilling", or "improve cache hit rate".
allowed-tools: "*"
composable_with: [snowflake-diagnose, cost-monitor, sql-review]
---

# Snowflake Optimize

## Workflow

### 1. Scope

Identify: slow specific query (ID/SQL) | general slowness | warehouse issues | cost concerns.

### 2. Query Profile (If Query ID Provided)

```sql
SELECT query_id, query_text, warehouse_name, warehouse_size,
  total_elapsed_time/1000 as total_sec, bytes_scanned,
  bytes_spilled_to_local_storage, bytes_spilled_to_remote_storage,
  partitions_scanned, partitions_total, percentage_scanned_from_cache,
  compilation_time/1000 as comp_sec, execution_time/1000 as exec_sec,
  queued_provisioning_time/1000, queued_overload_time/1000
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE query_id = '<query_id>' ORDER BY start_time DESC LIMIT 1;
```

**Interpret:** Spilling > 0 → warehouse too small | Cache % low → poor reuse | High partitions_scanned/total → poor pruning | queued_* > 0 → contention

### 3. Warehouse Utilization (7 Days)

```sql
SELECT warehouse_name, DATE_TRUNC('hour', start_time) as hour,
  COUNT(*), AVG(total_elapsed_time)/1000, AVG(percentage_scanned_from_cache),
  SUM(CASE WHEN bytes_spilled_to_local_storage > 0 OR bytes_spilled_to_remote_storage > 0 THEN 1 ELSE 0 END) as spilling_count
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE warehouse_name IS NOT NULL AND start_time >= dateadd('days', -7, current_timestamp())
GROUP BY warehouse_name, hour ORDER BY warehouse_name, hour DESC;
```

**Thresholds:** >5% spilling → size up | Queue delays → multi-cluster | Cache <50% → increase auto-suspend

### 4. Table Pruning (Poor Clustering)

```sql
SELECT table_name, AVG(partitions_scanned*100.0/NULLIF(partitions_total,0)) as scan_pct
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE partitions_total > 0 AND database_name = '<db>' AND schema_name = '<schema>'
  AND start_time >= dateadd('days', -7, current_timestamp())
GROUP BY table_name HAVING scan_pct > 10 ORDER BY scan_pct DESC;
```

### 5. Issues → Fixes

| Issue | Evidence | Fix |
|-------|----------|-----|
| Memory spilling | bytes_spilled_* > 0 | Size up warehouse OR simplify query |
| Poor pruning | high partitions_scanned/total | Add clustering key; filter on cluster column |
| Low cache | percentage_scanned_from_cache < 50% | Increase auto-suspend; consolidate queries |
| Queue delays | queued_overload_time > 0 | Multi-cluster; increase max_cluster_count |
| Long compilation | compilation_time > execution_time | Simplify; CTEs; materialize intermediates |

### 6. Warehouse Sizing

**Size up:** Spilling, slow individual queries, complex analytics
**Scale out:** Queue delays, high concurrency
**Size down:** No spilling, low utilization, cost optimization

### 7. Cost (30 Days)

```sql
SELECT warehouse_name, SUM(credits_used), AVG(credits_used_compute)
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= dateadd('days', -30, current_timestamp())
GROUP BY warehouse_name ORDER BY SUM(credits_used) DESC;
```

## Output Format

```
🚀 SNOWFLAKE PERFORMANCE ANALYSIS
SCOPE: <query/warehouse/general> | TIMEFRAME: <period>

📊 FINDINGS: Total time, cache %, partitions, spilling
⚠️ ISSUES: <name> Severity: 🔴/🟡/🟢 | Evidence | Fix
💡 RECOMMENDATIONS: Immediate + long-term
📈 WAREHOUSE: Current → Recommended | Rationale
💰 COST: Current spend | Est. savings
```

## Do Not

- Suggest changes without baseline metrics
- Prioritize cost over slow queries (impact first)
- Ignore cost vs performance tradeoffs
- Forget: Query Acceleration, Search Optimization, Materialized Views, Clustering Keys
