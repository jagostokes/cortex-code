---
name: cost-monitor
description: Analyzes Snowflake credit consumption, expensive queries, warehouse utilization, and storage costs. Use when the user asks "how much are we spending", "cost analysis", "expensive queries", "credit usage", "warehouse costs", "reduce Snowflake costs", or "cost optimization".
allowed-tools: "*"
---

# Cost Monitor

## Workflow

### 1. Scope

Identify: full account | specific warehouse | specific time range (7d, 30d default).

### 2. Credit Consumption by Warehouse

```sql
SELECT warehouse_name,
  SUM(credits_used) as total_credits,
  SUM(credits_used_compute) as compute_credits,
  SUM(credits_used_cloud_services) as cloud_credits,
  COUNT(*) as billing_events
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('days', -30, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;
```

### 3. Top Expensive Queries (7 or 30 Days)

```sql
SELECT query_id, user_name, warehouse_name, warehouse_size,
  total_elapsed_time/1000 as total_sec,
  credits_used_cloud_services,
  bytes_scanned/1e12 as tb_scanned,
  LEFT(query_text, 100) as query_preview
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('days', -30, CURRENT_TIMESTAMP())
  AND credits_used_cloud_services > 0
ORDER BY credits_used_cloud_services DESC
LIMIT 20;
```

### 4. Always-On Warehouses

```sql
SELECT warehouse_name, SUM(credits_used) as credits
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD('days', 7, CURRENT_TIMESTAMP())
GROUP BY warehouse_name;
-- Cross-check: SHOW WAREHOUSES for auto_suspend (NULL = never suspend)
```

Flag warehouses with high credits and auto_suspend = NULL or very high.

### 5. Credit Usage by User

```sql
SELECT user_name, warehouse_name,
  SUM(credits_used_cloud_services) as credits
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD('days', -30, CURRENT_TIMESTAMP())
  AND warehouse_name IS NOT NULL
GROUP BY user_name, warehouse_name
ORDER BY credits DESC
LIMIT 20;
```

### 6. Storage Costs (Optional)

```sql
SELECT table_name, database_name, schema_name,
  active_bytes/1e12 as active_tb,
  time_travel_bytes/1e12 as time_travel_tb,
  failsafe_bytes/1e12 as failsafe_tb
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE deleted IS NULL
ORDER BY (active_bytes + time_travel_bytes + failsafe_bytes) DESC
LIMIT 20;
```

### 7. Recommendations

| Issue | Evidence | Fix |
|-------|----------|-----|
| Always-on warehouse | auto_suspend NULL, high credits | Set auto_suspend (e.g. 60–300s) |
| Oversized warehouse | Large size, low utilization | Size down; use multi-cluster for spikes |
| Expensive ad-hoc queries | High credits per query | Query optimization; use result cache |
| Cloud services overuse | High cloud_credits vs compute | Reduce small queries; batch |
| Storage bloat | Large time_travel/failsafe | Reduce retention; drop unused tables |

## Output Format

```
💰 COST MONITOR REPORT
PERIOD: <7d/30d> | TOTAL CREDITS: <approx>

📊 BY WAREHOUSE: <name> → <credits> (<% of total>)
🔝 TOP QUERIES: <query_id> | <credits> | <preview>
⚠️ ALWAYS-ON: <warehouse> → Set auto_suspend
👤 BY USER: <top users>
📦 STORAGE: <top tables by bytes>
💡 RECOMMENDATIONS: <numbered actions>
```

## Do Not

- Confuse credits with dollars (credits vary by edition/region)
- Ignore cloud_services credits (small queries add up)
- Suggest aggressive auto_suspend without considering user experience
- Forget to check WAREHOUSE_METERING_HISTORY latency (up to 45 min delay)
