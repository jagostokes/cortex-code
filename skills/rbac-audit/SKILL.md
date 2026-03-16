---
name: rbac-audit
description: Maps RBAC hierarchy, detects over-privileged roles, orphaned grants, and privilege escalation paths. Use when the user asks to "audit roles", "check permissions", "RBAC review", "who has access to X", "least privilege", "security audit", or "find over-privileged roles".
allowed-tools: "*"
---

# RBAC Audit

## Workflow

### 1. Scope

Identify: full account audit | specific role/user | specific object (database, schema, table).

### 2. Role Hierarchy

```sql
SHOW ROLES;
SHOW GRANTS TO ROLE <role_name>;
SHOW GRANTS OF ROLE <role_name>;
```

Map: roles → granted roles → privileges. Identify ACCOUNTADMIN usage and inheritance chains.

### 3. User → Role Mapping

```sql
SHOW GRANTS TO USER <user>;
SHOW USERS;
```

For each user, list roles. Flag users with ACCOUNTADMIN or SYSADMIN.

### 4. Object Privileges

```sql
SHOW GRANTS ON DATABASE <db>;
SHOW GRANTS ON SCHEMA <schema>;
SHOW GRANTS ON TABLE <table>;
SHOW FUTURE GRANTS IN SCHEMA <schema>;
```

Identify: who can read/write what; future grants; ownership.

### 5. Over-Privileged Roles

**Red flags:**
- Role has ACCOUNTADMIN or inherits from it
- Role has USAGE on many databases with no clear need
- Role has CREATE/DROP on production objects
- Role has MANAGE GRANTS (can escalate)

### 6. Orphaned Grants

```sql
-- Grants to dropped roles (may error or return empty)
SHOW GRANTS TO ROLE <role>;
-- Cross-reference with SHOW ROLES
```

Flag grants to roles that no longer exist or users with no recent login.

### 7. Privilege Escalation Paths

Trace: can role X grant itself or others higher privileges? Check MANAGE GRANTS, CREATE ROLE, ownership of security-relevant objects.

### 8. Recommendations

- Least-privilege: suggest REVOKE for unused privileges
- Role consolidation: merge similar roles
- Separation of duties: split admin vs read-only roles

## Output Format

```
🔐 RBAC AUDIT REPORT
SCOPE: <account/role/user/object> | ROLES: <count> | USERS: <count>

📊 HIERARCHY: <summary>
⚠️ OVER-PRIVILEGED: <role> → <issue> → RECOMMEND: <action>
🔗 ORPHANED: <grants to non-existent>
🛡️ ESCALATION RISKS: <paths>
✅ RECOMMENDATIONS: <numbered least-privilege actions>
```

## Do Not

- Suggest revoking without verifying impact (check who uses the role)
- Ignore future grants and inherited privileges
- Assume ACCOUNTADMIN is always bad (some orgs use it for admin tasks)
- Skip SHOW GRANTS OF ROLE (shows who can grant this role)
