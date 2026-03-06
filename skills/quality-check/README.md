# Code Quality Check

**Ship with confidence.** A single command runs security scans, linting, type checks, tests, and build verification—before you commit or open a PR.

---

## 30-Second Setup

```bash
cp -r skills/quality-check ~/.snowflake/cortex/skills/
```

Then in Cortex Code:

```
/skill quality-check
```

or simply: *"Run code quality checks"*

---

## What Runs (In Order)

| Step | What it does | Blocks if failed? |
|------|---------------|--------------------|
| 1. Security | Scans staging for secrets, `.env`, credentials | Yes |
| 2. Lint | ESLint, Ruff, Clippy, golangci-lint | Yes (errors) |
| 3. Types | tsc, mypy, pyright | Yes |
| 4. Tests | pytest, Jest, cargo test, go test | Yes |
| 5. Build | npm build, cargo build, go build | Yes |
| 6. Dependencies | Unused/outdated packages, lockfiles | No (warns) |
| 7. Git | Staging sanity, unintended files | No (warns) |

Project type is auto-detected from `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, etc.

---

## Verdicts

| Verdict | Meaning |
|---------|---------|
| READY | All gates pass. Ship it. |
| NEEDS ATTENTION | Warnings only (e.g. lint warnings). Configurable whether to block. |
| BLOCKED | Security issue, build failure, test failure, type error, or lint error. Fix before proceeding. |

Security issues always block, regardless of config.

---

## Auto-Fix Mode

For linting and formatting only. Never touches security, types, tests, or dependencies.

**Enable via config** (`.cortex/code-quality-config.json`):

```json
{
  "auto_fix": {
    "enabled": true,
    "allow": ["linting", "formatting"],
    "auto_approve": false
  }
}
```

**Or via prompt:** *"Run quality checks and fix issues"*

Auto-fix applies `eslint --fix`, `prettier --write`, `ruff check --fix`, `ruff format`, etc., then re-runs checks to confirm.

---

## Configuration

Optional: `.cortex/code-quality-config.json` in your project root.

| Section | Purpose |
|---------|---------|
| `auto_fix` | Enable/disable, allow/deny categories, auto-approve |
| `metrics` | Enable history, limit runs (default 30), show trends |
| `quality_gates` | Toggle blocking on security, build, tests, types, lint; allow warnings |

See `.cortex-config-example.json` in this skill for a full example.

**Tip:** Commit the config; add `.cortex/quality-history.json` to `.gitignore` (metrics are personal).

---

## Supported Stacks

| Stack | Lint | Types | Tests | Build |
|-------|------|-------|-------|-------|
| TypeScript/Next.js | ESLint | tsc | Jest/Vitest | npm run build |
| Python | Ruff | mypy | pytest | — |
| Rust | Clippy | rustc | cargo test | cargo build |
| Go | golangci-lint | go vet | go test | go build |

---

## Integrations

**Pre-commit hook:**

```bash
#!/bin/bash
cortex chat --message "Run code quality checks" --skill quality-check
[ $? -eq 0 ] || exit 1
```

**CI (e.g. GitHub Actions):**

```yaml
- run: cortex chat --message "Run code quality checks" --skill quality-check
```

**VS Code task:** Add a shell task that runs the same `cortex chat` command.

---

## FAQ

**Q: Auto-fix isn’t running.**  
A: Set `auto_fix.enabled: true` in config, or include "fix" in your prompt.

**Q: Build passes even when it fails.**  
A: Check your build script—no `|| exit 0` or similar.

**Q: Tests aren’t detected.**  
A: Ensure your test command exits 0 on success and non-zero on failure.

**Q: Metrics not saving?**  
A: Ensure `.cortex/` exists, is writable, and `metrics.enabled: true` in config.

---

## Related Skills

- **deploy-multi-env** — Run quality checks before deploying
- **snowflake-diagnose** — For Snowflake environment issues
