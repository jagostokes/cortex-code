---
name: deploy-multi-env
description: Deploys Snowflake artifacts (Streamlit, SPCS, UDFs, tables) across dev → staging → prod with validation, testing, and rollback. Use when the user says "deploy to prod", "promote to staging", "multi-environment deployment", "deploy across accounts", or when deploying Streamlit apps, SPCS services, or UDFs to multiple environments.
allowed-tools: "*"
prereq_skills: [quality-check, snowflake-diagnose]
---

# Deploy Multi-Env

## Workflow

### 1. Environment Discovery

List connections; identify dev, staging, prod. Verify access and privileges per environment.

**Patterns:** Same account (`DEV_DB`, `STAGING_DB`, `PROD_DB`) | Different accounts | Hybrid

### 2. Artifact Detection

| Type | Detect | Deploy |
|------|--------|--------|
| Streamlit | `streamlit_app.py`, `requirements.txt` | `snow streamlit deploy` or CREATE STREAMLIT |
| SPCS | `spec.yaml`, Dockerfile | Build → push → `snow service create` |
| UDF/Proc | `.sql`, Python/Java handlers | CREATE FUNCTION/PROCEDURE |
| Generic | Any files | PUT to stage |
| Objects | DDL | Execute DDL |

### 3. Pre-Deployment Checks (Per Env)

```sql
SHOW DATABASES LIKE '<target_db>';
SHOW SCHEMAS LIKE '<target_schema>' IN DATABASE <target_db>;
SHOW WAREHOUSES;
SHOW GRANTS TO ROLE <current_role>;
```

**Verify:** No secrets in code; configs externalized; stages/tables exist; privileges granted.

### 4. Environment Config

- **Per-env files:** `config/dev.yaml`, `staging.yaml`, `prod.yaml`
- **Env vars:** `SNOWFLAKE_ENV`, `DB_NAME = f"{ENV}_DB"`
- **SQL vars:** `SET db_name = 'DEV_DB'; USE DATABASE IDENTIFIER($db_name);`

### 5. Deploy

**Streamlit:** `snow streamlit deploy --connection <env> --database <db> --schema <schema> --replace <app>`
**SPCS:** Build image → tag `:env` → push → `snow service create --connection <env> --spec-path spec.yaml`
**UDF:** `USE ROLE/WAREHOUSE/DATABASE/SCHEMA` → `CREATE OR REPLACE FUNCTION ...`

### 6. Post-Deploy Test

**Streamlit:** Hit URL; verify UI, flows, data.
**SPCS:** `SHOW SERVICES`; `DESC SERVICE`; `SYSTEM$GET_SERVICE_LOGS`; test endpoints.
**UDF:** `SELECT <fn>(<test_inputs>);`

### 7. Rollback (If Failed)

**Streamlit:** `CREATE OR REPLACE STREAMLIT ... FROM '@stage/<prev_version>'`
**SPCS:** `ALTER SERVICE ... FROM SPECIFICATION_FILE = '@stage/<prev_spec>'`
**UDF:** Restore from versioned copy in stage

### 8. Report

Track: artifact, type, version, envs deployed, test results, rollback plan.

## Output Format

```
🚀 MULTI-ENVIRONMENT DEPLOYMENT
ARTIFACT: <name> | TYPE: <Streamlit/SPCS/UDF> | VERSION: <version>

📋 ENVIRONMENTS: DEV → STAGING → PROD (with locations)
✅ PRE-DEPLOYMENT: [✓] Connections, secrets, deps, privileges
🔄 DEPLOYMENT: Status per env + tests
🔗 URLS: Per env
⚠️ ROLLBACK: <steps>
VERDICT: ✅ DEPLOYED / ⚠️ PARTIAL / ❌ FAILED
```

## Safety Gates

**Before PROD:** DEV + STAGING deployed; tests pass; no secrets; rollback documented.

**Auto-block PROD if:** DEV/STAGING failed; tests failing; security issues.

## Do Not

- Deploy to prod before dev and staging succeed
- Use dev connection for prod deployment
- Hardcode environment values in code
- Deploy without a rollback plan

## Env-Specific Notes

**Streamlit:** Different warehouse sizes; feature flags; sample vs full data.
**SPCS:** Different compute pools; image tags `:dev`, `:staging`, `:prod`.
**UDFs:** Performance test in staging; warehouse size for expensive UDFs.
