---
name: sql-review
description: Reviews SQL for anti-patterns, Snowflake best practices, and performance issues. Use when the user asks to "review SQL", "code review this query", "SQL best practices", "check this SQL", "optimize this query", or when reviewing .sql files, views, or stored procedures.
allowed-tools: "*"
composable_with: [quality-check, snowflake-optimize]
---

# SQL Review

## Workflow

### 1. Scope

Identify: single query/file | directory of .sql files | view/procedure definition.

### 2. Anti-Patterns (Generic SQL)

| Pattern | Issue | Fix |
|---------|-------|-----|
| `SELECT *` | Unnecessary columns; breaks when schema changes | List columns explicitly |
| Cartesian join | Missing JOIN condition | Add proper ON clause |
| `DELETE`/`UPDATE` without WHERE | Accidental full-table modification | Require WHERE; use LIMIT in dev |
| Subquery in SELECT | Often re-executed per row | Use JOIN or CTE |
| `NOT IN` with NULLs | Returns no rows if subquery has NULL | Use `NOT EXISTS` or `LEFT JOIN ... WHERE ... IS NULL` |
| Implicit type conversion | `WHERE col = '123'` when col is number | Match types; use TRY_CAST if needed |

### 3. Snowflake-Specific Best Practices

| Pattern | Issue | Fix |
|---------|-------|-----|
| No clustering on large filtered tables | Full scan | Add clustering key aligned to common filters |
| Missing QUALIFY | Window functions without filtering | Use QUALIFY to filter window results |
| LATERAL FLATTEN without proper use | Inefficient JSON parsing | Ensure FLATTEN on correct level; use appropriate path |
| Non-deterministic functions in views | RAND(), CURRENT_TIMESTAMP() in view def | Move to query or use deterministic alternative |
| UDF in hot path | Per-row Python/JS UDF cost | Consider Snowpark, stored proc, or pushdown |
| Large IN list | Performance degradation | Use temp table or JOIN |
| No result caching consideration | Repeated identical queries | Ensure warehouse not dropped; use result_cache |

### 4. Security

- Check for SQL injection vectors (concatenated user input)
- Verify no hardcoded credentials or account identifiers
- Masking policies: are PII columns properly masked in output?

### 5. Readability & Maintainability

- CTEs vs nested subqueries (CTEs often clearer)
- Consistent formatting (keywords uppercase, indentation)
- Meaningful aliases
- Comments for complex logic

### 6. Output

For each finding: file/line, pattern, severity (🔴 high / 🟡 medium / 🟢 low), suggested fix.

## Output Format

```
📋 SQL REVIEW
FILES: <count> | QUERIES: <count>

🔴 HIGH: <pattern> at <file:line> → <fix>
🟡 MEDIUM: <pattern> at <file:line> → <fix>
🟢 LOW: <pattern> at <file:line> → <fix>

✅ PASSING: <items>
💡 RECOMMENDATIONS: <numbered improvements>
```

## Do Not

- Suggest changes that alter semantics without explicit user approval
- Flag style-only issues as high severity
- Ignore context (e.g. one-off migration script vs production view)
- Assume Snowflake-specific behavior without verifying (e.g. QUALIFY support, clustering)
