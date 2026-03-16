# Changelog Gen

Auto-generate changelogs from git history. Groups commits by type (feat, fix, docs, etc.) and produces Keep-a-Changelog style output. Snowflake-aware: detects DDL, dbt model changes, migrations.

## When to Use

- "Generate a changelog"
- "Create release notes for v2.0"
- "What changed since last release?"
- "Changelog from git"

## What It Does

- Parses git history since a tag, commit, or date
- Categorizes by conventional commits (feat, fix, docs, etc.)
- Snowflake-aware grouping (DDL, dbt, migrations)
- Outputs Keep-a-Changelog format
- Optionally updates CHANGELOG.md

## Setup

```bash
cp -r skills/changelog-gen ~/.snowflake/cortex/skills/
```

Then in Cortex Code: `/skill changelog-gen` or *"Generate changelog since last tag"*.
