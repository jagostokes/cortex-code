---
name: changelog-gen
description: Generates changelogs from git history. Use when the user asks to "generate changelog", "create release notes", "what changed since X", "changelog from git", or when preparing a release.
allowed-tools: "*"
---

# Changelog Gen

## Workflow

### 1. Scope

Identify: since last tag | since commit/tag X | since date | unreleased only.

### 2. Git History

```bash
# Commits since last tag
git log $(git describe --tags --abbrev=0 2>/dev/null || echo "HEAD")..HEAD --pretty=format:"%h %s (%an, %ar)"

# Or since specific ref/date
git log v1.0.0..HEAD --pretty=format:"%h %s (%an)"
git log --since="2024-01-01" --pretty=format:"%h %s"
```

### 3. Categorize Commits

Group by conventional commit prefix or heuristic:

| Prefix/Pattern | Category |
|----------------|----------|
| `feat:`, `feature:` | Features |
| `fix:`, `bugfix:` | Bug Fixes |
| `docs:` | Documentation |
| `refactor:`, `chore:` | Chores / Refactoring |
| `perf:` | Performance |
| `security:` | Security |
| `BREAKING` | Breaking Changes |
| dbt model changes, DDL, migrations | Data / Schema |

**Snowflake-aware:** Detect DDL files, dbt model changes, migration scripts; group under "Data / Schema" or "Migrations".

### 4. Format

Use [Keep a Changelog](https://keepachangelog.com/) style:

```markdown
## [Unreleased]
### Added
- feat: add cost-monitor skill (#42)
### Fixed
- fix: correct DATEADD in cost-monitor query
### Changed
- refactor: extract shared SQL helpers
```

### 5. Output

- Write to `CHANGELOG.md` or output to conversation
- If `CHANGELOG.md` exists: prepend new section, preserve existing
- Include: version (or Unreleased), date, categorized list, links to commits/PRs if available

### 6. PR/Issue Links

If remote is GitHub/GitLab, try to resolve commit to PR: `https://github.com/org/repo/commit/<sha>` or `/pull/<n>`.

## Output Format

```
📝 CHANGELOG GENERATED
SCOPE: <since> → HEAD | COMMITS: <count>

## [Unreleased] - YYYY-MM-DD
### Added
- ...
### Fixed
- ...
### Changed
- ...
```

## Do Not

- Include merge commits unless they have meaningful messages
- Duplicate entries already in existing CHANGELOG
- Guess version numbers—use "Unreleased" or ask user
- Ignore conventional commits when present (parse them)
