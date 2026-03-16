# Cortex Code Skills

Skills to enhance [Snowflake's Cortex Code CLI](https://docs.snowflake.com/en/user-guide/cortex-code/). Install skills to your local Cortex directory and invoke them in conversation.

## Quick Start

```bash
# Copy all skills to your Cortex directory
cp -r skills/* ~/.snowflake/cortex/skills/

# Or add a single skill
cp -r skills/quality-check ~/.snowflake/cortex/skills/
```

In Cortex Code: `/skill list` to see available skills, or mention one by name: *"Run quality checks"*.

## Skills

| Skill | Description |
|-------|-------------|
| [quality-check](skills/quality-check/README.md) | Security scans, linting, type checks, tests, build verification before commits/PRs |
| [deploy-multi-env](skills/deploy-multi-env/README.md) | Deploy Streamlit, SPCS, UDFs across dev → staging → prod |
| [snowflake-diagnose](skills/snowflake-diagnose/README.md) | Diagnose connection failures, permissions, warehouse issues |
| [snowflake-optimize](skills/snowflake-optimize/README.md) | Query performance, warehouse sizing, spilling, cache analysis |
| [rbac-audit](skills/rbac-audit/README.md) | Role and privilege analysis, over-privileged roles, least-privilege recommendations |
| [cost-monitor](skills/cost-monitor/README.md) | Credit consumption, expensive queries, warehouse cost analysis |
| [sql-review](skills/sql-review/README.md) | SQL code review, Snowflake best practices, anti-pattern detection |
| [changelog-gen](skills/changelog-gen/README.md) | Auto-generate changelogs from git history |

## Skill Registry

See [skills.json](skills.json) for programmatic discovery.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or modify skills.
