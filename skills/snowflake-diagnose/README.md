# Snowflake Diagnostics

**When something’s wrong and you’re not sure why.** A structured 6-step workflow to pinpoint connection failures, permission errors, warehouse issues, and object access problems.

---

## Install

```bash
cp -r skills/snowflake-diagnose ~/.snowflake/cortex/skills/
```

**Invoke with:** *"Debug my Snowflake connection"*, *"Permission denied"*, *"Check Snowflake environment"*, *"Warehouse not responding"*

---

## What It Checks

| Step | Focus | Example checks |
|------|-------|-----------------|
| 1. Connection | Auth, network, active context | `SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()...` |
| 2. Roles & privileges | Missing grants | `SHOW GRANTS TO USER`, `SHOW GRANTS ON WAREHOUSE` |
| 3. Warehouse | State, size, auto-suspend | `SHOW WAREHOUSES` |
| 4. Context | DB/schema, case sensitivity | `SHOW DATABASES`, `SHOW SCHEMAS` |
| 5. Objects | Table/view access | `SHOW TABLES`, `SHOW GRANTS ON TABLE` |
| 6. Checklist | Common gotchas | Wrong connection, suspended warehouse, typo, MFA/SSO |

---

## Sample Report

```
🔍 SNOWFLAKE DIAGNOSTICS

Connection: my_dev | User: john.doe | Role: ANALYST_ROLE
Warehouse: COMPUTE_WH (STARTED) | Context: SALES_DB.PUBLIC

✅ PASSING: Connection active, warehouse running, database accessible
❌ FAILING: Role lacks SELECT on CUSTOMERS
   → SOLUTION: GRANT SELECT ON TABLE CUSTOMERS TO ROLE ANALYST_ROLE
⚠️  WARN: Warehouse auto-suspend 60s (may suspend too quickly)

RECOMMENDED: Run the GRANT above; consider auto-suspend 300s for better caching
```

---

## Common Issues → Fixes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Permission denied | Missing grant | `GRANT SELECT ON TABLE <table> TO ROLE <role>` |
| Queries not running | Warehouse suspended | Resume warehouse or adjust auto-suspend |
| Can’t find tables | Wrong connection/context | Switch connection or `USE DATABASE/SCHEMA` |
| Object doesn’t exist | Typo, case mismatch | Check identifier case; Snowflake is case-sensitive |
| Auth/connection errors | Expired creds, MFA/SSO | Refresh credentials, re-authenticate |

---

## Tips

- **Start simple** — Suspended warehouse and wrong role cause most issues.
- **Use SHOW** — `SHOW GRANTS`, `SHOW WAREHOUSES`, `SHOW TABLES` are your friends.
- **Verify context** — Always confirm connection and database/schema before assuming.
- **Provide SQL** — The skill outputs exact commands you can run.

---

## Troubleshooting the Skill

**Skill not activating?**  
Verify: `ls ~/.snowflake/cortex/skills/snowflake-diagnose/SKILL.md`

**SHOW commands fail?**  
You may need `IMPORTED PRIVILEGES` on `SNOWFLAKE`:

```sql
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE <your_role>;
```

**Timeouts?**  
Increase session timeout: `ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 600;`

---

## Related Skills

- **snowflake-optimize** — When queries are slow or expensive
- **deploy-multi-env** — When deployment fails and you need to debug
