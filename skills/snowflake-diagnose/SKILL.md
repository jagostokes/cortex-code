---
name: snowflake-diagnose
description: Diagnoses Snowflake connection failures, permission errors, warehouse issues, and object access problems. Use when the user reports "connection failed", "permission denied", "warehouse not responding", "can't access table", or asks to "debug Snowflake", "check Snowflake environment", or "troubleshoot Snowflake setup".
allowed-tools: "*"
---

# Snowflake Diagnose

## Workflow (Check Simple First)

### 1. Connection

List connections; test with:
```sql
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA();
```
Verify active connection matches intent. Check network, auth, expired creds.

### 2. Roles & Privileges

```sql
SHOW GRANTS TO USER <current_user>;
SHOW GRANTS ON WAREHOUSE <warehouse_name>;
SHOW GRANTS ON DATABASE <db>;
SHOW GRANTS ON SCHEMA <schema>;
```
Identify missing privileges.

### 3. Warehouse

```sql
SHOW WAREHOUSES LIKE '<warehouse>';
```
Check: state (suspended?), size, auto-suspend/resume.

### 4. Context

```sql
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();
SHOW DATABASES;
SHOW SCHEMAS IN DATABASE <db>;
```
Check case sensitivity, naming.

### 5. Object Access

```sql
SHOW TABLES LIKE '<table>';
SHOW GRANTS ON TABLE <table>;
```

### 6. Checklist

- [ ] Wrong connection?
- [ ] Warehouse suspended?
- [ ] Role lacks privileges?
- [ ] Wrong database/schema?
- [ ] Object typo or case mismatch?
- [ ] Expired creds / MFA/SSO?

## Output Format

```
🔍 SNOWFLAKE DIAGNOSTICS
Connection: <name> | User: <user> | Role: <role> | Warehouse: <wh> (<state>) | Context: <db>.<schema>

✅ PASSING: <items>
❌ FAILING: <item> → SOLUTION: <exact SQL/command>
⚠️ WARNINGS: <items>
RECOMMENDED: <numbered actions>
```

## Do Not

- Assume context before verifying
- Skip SHOW commands for discovery
- Provide vague fixes—give exact SQL the user can run
- Forget Snowflake identifier case sensitivity
