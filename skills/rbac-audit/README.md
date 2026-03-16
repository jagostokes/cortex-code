# RBAC Audit

Audit Snowflake roles, privileges, and access. Maps the RBAC hierarchy, detects over-privileged roles, orphaned grants, and privilege escalation paths.

## When to Use

- "Audit our Snowflake roles"
- "Who has access to the production database?"
- "Find over-privileged roles"
- "Least privilege recommendations"
- "RBAC security review"

## What It Does

- Maps roles → grants → users
- Flags ACCOUNTADMIN/SYSADMIN usage
- Detects orphaned grants (to dropped roles/users)
- Identifies privilege escalation paths
- Suggests least-privilege changes

## Setup

```bash
cp -r skills/rbac-audit ~/.snowflake/cortex/skills/
```

Then in Cortex Code: `/skill rbac-audit` or *"Audit RBAC"*.
