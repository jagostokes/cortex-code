---
name: quality-check
description: Runs security scans, linting, type checking, tests, and build verification before commits or PRs. Use when the user asks to "check code quality", "run tests", "verify code", "pre-flight check", "run lint", or before completing coding tasks or creating pull requests. Supports auto-fix for linting/formatting when user says "fix" or "apply fixes".
allowed-tools: "*"
---

# Quality Check

## Workflow

### 0. Determine Mode

Set `MODE = AUTO_FIX` if:
- `.cortex/code-quality-config.json` exists with `auto_fix.enabled: true`, OR
- User prompt contains: "fix", "apply fixes", "auto-fix", "fix automatically"

Otherwise: `MODE = REPORT_ONLY` (default, safe)

### 1. Project Detection

Detect type from presence of: `package.json`, `pyproject.toml`/`requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`/`build.gradle`. Check README/AGENTS.md for custom commands. Detect Python env (uv, poetry, venv, conda).

### 2. Security Scan (Run First—Block if Failed)

Scan for: `.env` in staging, API keys/tokens/passwords in code, DB credentials, private keys, Snowflake account IDs. Check gitignore. **BLOCK if secrets found.**

### 3. Linting

| Stack | Command |
|-------|---------|
| JS/TS | `npm run lint` or `eslint .` |
| Python | `ruff check .` |
| Rust | `cargo clippy` |
| Go | `golangci-lint run` |

Parse output; identify actionable issues with file:line.

### 4. Type Checking

| Stack | Command |
|-------|---------|
| TS | `npm run typecheck` or `tsc --noEmit` |
| Python | `mypy .` or `pyright` |
| Rust | `cargo check` |
| Go | Built into compilation |

### 5. Testing

Run existing tests only (don't write new ones unless asked): `npm test`, `pytest`, `cargo test`, `go test ./...`. Report failures with context. Check coverage if available.

### 6. Build

`npm run build`, `cargo build`, or `go build` if applicable. Verify no build errors.

### 7. Dependencies

Check unused deps, outdated packages, lockfile freshness. Warn only—do not block.

### 8. Git Status

Verify no unintended files staged (node_modules, .env). Check commit conventions if applicable.

### 9. Metrics

Append to `.cortex/quality-history.json`:
- `git rev-parse HEAD`, `git log -1 --format='%H %ai %an'`
- Results: security, linting, type_check, tests, build, dependencies, verdict
- Keep last 30 runs. Compare to previous; note trends (↑↓→).

### 10. Auto-Fix (Only if MODE = AUTO_FIX)

1. List fixable issues (linting, formatting only)
2. Ask confirmation unless `auto_approve: true` in config
3. If confirmed: run `eslint --fix .`, `prettier --write .`, `ruff check --fix .`, `ruff format .`, `cargo clippy --fix --allow-dirty`, `cargo fmt` as applicable
4. Re-run checks; update metrics

**Never auto-fix:** dependencies, security, tests, type errors.

## Output Format

```
✅ CODE QUALITY REPORT
PROJECT: <type> | MODE: <REPORT_ONLY|AUTO_FIX> | COMMIT: <sha>

🔒 SECURITY: <PASS/FAIL> <findings>
📋 LINTING: <PASS/FAIL/WARNINGS> <summary> Fix: <command>
🔤 TYPE CHECK: <PASS/FAIL> <errors>
🧪 TESTS: <PASS/FAIL> (<X/Y>) Coverage: <%>
🔨 BUILD: <PASS/FAIL/SKIPPED>
📦 DEPENDENCIES: <OK/WARNINGS>
📝 GIT: <CLEAN/ISSUES>
📈 TRENDS: <vs last run>
VERDICT: ✅ READY / ⚠️ NEEDS ATTENTION / ❌ BLOCKED
```

## Quality Gates

**Block:** secrets, lint errors, type errors, test failures, build failure
**Warn only:** lint warnings, missing tests, outdated deps

## Do Not

- Run security scan after other checks (always first)
- Auto-fix security, types, tests, or dependencies
- Write new tests unless explicitly asked
- Skip reading full error output (use `tail -100` if truncated)

## Quick Reference

**Project commands:** `jq '.scripts | keys[]' package.json` | `grep -A5 "\[tool" pyproject.toml` | `make -qp | grep "^[a-z].*:"`
**Python:** `uv run pytest` | `poetry run pytest` | `source venv/bin/activate && pytest`
