# Multi-Environment Deployment

**Deploy once, promote safely.** Automate dev → staging → prod rollouts for Streamlit apps, SPCS services, UDFs, and other Snowflake artifacts—with validation, testing, and rollback built in.

---

## Install

```bash
cp -r skills/deploy-multi-env ~/.snowflake/cortex/skills/
```

**Invoke with:** *"Deploy to prod"*, *"Promote to staging"*, *"Deploy this Streamlit app across environments"*

---

## The Pipeline

```
Discover environments → Detect artifact type → Pre-deploy checks → Deploy (dev → staging → prod) → Post-deploy tests → Report + rollback plan
```

**Prod is never deployed** until dev and staging succeed and tests pass. Security scans and dependency checks run before any deployment.

---

## Supported Artifacts

| Type | Detected by | Deploy method |
|------|-------------|---------------|
| Streamlit | `streamlit_app.py`, `requirements.txt` | `snow streamlit deploy` or SQL |
| SPCS | `spec.yaml`, Dockerfile | Build → push → `snow service create` |
| UDFs/Procedures | `.sql`, Python/Java handlers | `CREATE OR REPLACE FUNCTION/PROCEDURE` |
| Tables/Views | DDL files | Execute DDL |
| Generic | Any files | PUT to stage |

---

## Environment Patterns

- **Same account:** `DEV_DB`, `STAGING_DB`, `PROD_DB`
- **Different accounts:** Separate Snowflake connections per env
- **Hybrid:** Shared account for dev/staging, separate for prod

Config can be per-env YAML, env vars, or parameterized SQL. No hardcoded env values in code.

---

## Safety Gates (Prod)

Before prod deployment, the skill verifies:

- [ ] Deployed successfully to dev
- [ ] Deployed successfully to staging
- [ ] All tests passing in dev and staging
- [ ] No secrets in code
- [ ] Rollback plan documented

**Auto-blocked if:** dev/staging failed, tests failing, or security issues found.

---

## Rollback Quick Reference

| Artifact | Rollback |
|----------|----------|
| Streamlit | `CREATE OR REPLACE STREAMLIT ... FROM '@stage/<previous_version>'` |
| SPCS | `ALTER SERVICE ... FROM SPECIFICATION_FILE = '@stage/<previous_spec>'` |
| UDF | Restore from versioned copy in stage |

Keep versioned copies in a stage before promoting.

---

## Example Output

```
🚀 MULTI-ENVIRONMENT DEPLOYMENT

ARTIFACT: sales_dashboard (Streamlit)
VERSION: v1.2.0

DEV     ✅ SUCCESS  → DEV_DB.PUBLIC.SALES_DASHBOARD
STAGING ✅ SUCCESS  → STAGING_DB.PUBLIC.SALES_DASHBOARD
PROD    ✅ SUCCESS  → PROD_DB.PUBLIC.SALES_DASHBOARD

Tests: PASS | Rollback: @stage/sales_dashboard_v1.1.0
VERDICT: ✅ DEPLOYED
```

---

## Practices

1. **Deploy dev first** — Always validate before promoting.
2. **Version everything** — Git tags, stage versioning.
3. **Separate connections** — Never deploy prod from a dev connection.
4. **Test in each env** — Staging ≠ prod; run smoke tests everywhere.
5. **Document rollback** — Know how to undo before you deploy.

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| Connection errors | `snow connection test --connection <env>` |
| Permission denied | `SHOW GRANTS TO ROLE <role>` |
| Stage access | `SHOW STAGES`; `LIST @<stage>` |

---

## Related Skills

- **snowflake-diagnose** — Debug connection/permission issues during deployment
- **quality-check** — Run before deploying to catch issues early
