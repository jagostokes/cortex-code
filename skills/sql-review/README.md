# SQL Review

Reviews SQL for anti-patterns, Snowflake best practices, and performance issues. Bridges `quality-check` (general code) and `snowflake-optimize` (runtime analysis).

## When to Use

- "Review this SQL"
- "Check this query for best practices"
- "Code review the views in models/"
- "Optimize this stored procedure"

## What It Does

- Generic SQL anti-patterns (SELECT *, cartesian joins, etc.)
- Snowflake-specific patterns (clustering, QUALIFY, LATERAL FLATTEN)
- Security (injection, credentials)
- Readability and maintainability

## Setup

```bash
cp -r skills/sql-review ~/.snowflake/cortex/skills/
```

Then in Cortex Code: `/skill sql-review` or *"Review the SQL in @models/"*.
