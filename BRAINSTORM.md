# Cortex Code — Development Brainstorm

What we have today: `quality-check`, `deploy-multi-env`, `snowflake-diagnose`, `snowflake-optimize`. All solid — but the surface area is narrow. Below are gaps, ideas, and directions organized by category.

Cross-referenced with: [openai/skills](https://github.com/openai/skills) (36 skills for Codex), [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) (80+ skills for Claude Code), and Snowflake's own [Cortex Code docs](https://docs.snowflake.com/en/user-guide/cortex-code/tools).

---

## Landscape: What Others Have That We Don't

### OpenAI Codex Skills (36 skills)

| Their skill | Gap for us? | Notes |
|-------------|-------------|-------|
| `gh-fix-ci` | Yes | Fix failing CI checks from PR logs — we have nothing for CI/CD debugging |
| `gh-address-comments` | Yes | Systematically address PR review comments — useful for any Snowflake project |
| `create-plan` | Yes | Turn a task into a scoped, executable plan — great for complex Snowflake migrations |
| `security-threat-model` | Yes | Generate threat models for repos — we could do this for Snowflake data architectures |
| `security-best-practices` | Partial | We have `quality-check` but it's code-focused, not Snowflake-security-focused |
| `security-ownership-map` | Yes | Map ownership via git history — bus factor analysis for data teams |
| `playwright` | Possible | Browser automation — could test Streamlit apps deployed to Snowflake |
| `jupyter-notebook` | Yes | Scaffold/edit notebooks — relevant for Snowflake Notebooks |
| `spreadsheet` | Yes | Excel/CSV manipulation — common Snowflake input/output format |
| `yeet` | Yes | One-command git flow (stage → commit → push → PR) — universal utility |
| `notion-knowledge-capture` | Inspiration | Capture decisions into docs — we could do this for Snowflake runbooks |
| `linear` | Inspiration | Issue tracking integration — could map to Snowflake task/incident tracking |
| `sentry` | Yes | Inspect production errors — analogous to checking Snowflake TASK/SERVICE failures |

### Claude Code Skills (80+ skills)

| Their skill | Gap for us? | Notes |
|-------------|-------------|-------|
| `subagent-driven-development` | Yes | Dispatch subagents for parallel tasks — Cortex Code supports subagents natively |
| `test-driven-development` | Yes | Write tests first, then implement — could adapt for dbt tests + SQL |
| `software-architecture` | Inspiration | Clean Architecture / SOLID — we need a Snowflake data architecture equivalent |
| `root-cause-tracing` | Yes | Trace errors back to origin — exactly what Snowflake debugging needs |
| `changelog-generator` | Yes | Auto-generate changelogs from git — useful for any Snowflake project |
| `deep-research` | Yes | Multi-step autonomous research — could research Snowflake docs, community, best practices |
| `webapp-testing` | Yes | Playwright-based testing — natural fit for Streamlit app validation |
| `MCP builder` | Yes | Build MCP integrations — Cortex Code supports MCP servers |
| `file-organizer` | Possible | Organize messy project files — useful for Snowflake projects with SQL sprawl |
| `kaizen` | Inspiration | Continuous improvement methodology — could apply to Snowflake environment health |
| `csv-data-summarizer` | Yes | Auto-analyze CSV data — common pre-Snowflake workflow |
| `postgres` | Inspiration | Safe SQL execution with read-only — we need a "safe Snowflake query" skill |
| Composio app integrations | Yes | Slack, Jira, GitHub, PagerDuty automation — incident/deploy notifications |

---

## Skills

### Data Engineering

**`dbt-assist`** — dbt model generation, testing, and documentation
- Generate dbt models from raw Snowflake tables (detect source schema, output `staging/` and `mart/` models)
- Write dbt tests (unique, not_null, accepted_values, relationships) from column analysis
- Generate `schema.yml` descriptions from column names + sample data
- Detect model lineage issues (orphaned models, circular refs)
- *Why:* Cortex Code now supports dbt natively, but there's no skill that encodes best practices for dbt project structure, naming conventions, or test generation
- *Inspired by:* Claude's `test-driven-development` (tests-first approach for dbt)

**`pipeline-debug`** — Data pipeline troubleshooting
- Detect late-arriving data (compare fact vs dimension freshness)
- Check TASK history for failures: `TASK_HISTORY()`, error messages, next scheduled run
- Trace data flow: stage → raw → curated → mart (check row counts at each layer)
- Identify stale tables (no writes in X days)
- *Why:* Pipeline debugging is ad-hoc and slow. Most engineers repeat the same SHOW/QUERY_HISTORY checks manually
- *Inspired by:* Claude's `root-cause-tracing`, Codex's `sentry` (production error inspection)

**`data-loader`** — Ingest external data into Snowflake
- Detect file type (CSV, JSON, Parquet, Avro) and generate COPY INTO / file format
- Handle S3/GCS/Azure stage creation
- Schema inference from file samples
- Generate staging table DDL matching file structure
- *Why:* Loading data is repetitive boilerplate that the agent can handle in seconds
- *Inspired by:* Claude's `csv-data-summarizer` (auto-analyze before loading)

**`airflow-assist`** — Airflow DAG generation for Snowflake
- Generate DAGs that orchestrate Snowflake tasks (SnowflakeOperator, dbt run, COPY INTO)
- Convert existing Snowflake TASKs to Airflow DAGs
- Add retry logic, SLA alerting, dependency management
- *Why:* Cortex Code now supports Airflow natively — but no skill encodes DAG patterns
- *Related:* Snowflake's [expansion to Airflow](https://www.infoworld.com/article/4136429/snowflake-extends-cortex-code-cli-to-dbt-and-airflow-to-streamline-data-engineering-workflows.html)

### Governance & Security

**`rbac-audit`** — Role and privilege analysis
- Map full RBAC hierarchy: roles → grants → users
- Detect over-privileged roles (ACCOUNTADMIN usage patterns)
- Find orphaned grants (grants to dropped roles/users)
- Detect privilege escalation paths
- Generate least-privilege recommendations
- *Why:* RBAC in Snowflake gets messy fast. No one audits it regularly because it's tedious
- *Inspired by:* Codex's `security-ownership-map` (ownership + bus factor analysis)

**`data-governance`** — Masking, tagging, classification
- Scan columns for PII patterns (SSN, email, phone, names)
- Suggest masking policies and tag assignments
- Audit existing policies: which columns are masked, which aren't
- Check compliance posture (GDPR, HIPAA, PCI)
- Generate `CREATE MASKING POLICY` and `ALTER TABLE SET MASKING POLICY` SQL
- *Why:* Tag-based masking is powerful but underused because setup is manual and error-prone

**`threat-model`** — Snowflake security threat modeling
- Analyze data architecture for security risks
- Check network policies, IP allow/blocklists
- Audit integration security (external functions, API integrations)
- Review share security (data sharing, reader accounts)
- *Why:* No one threat-models their Snowflake account — they just hope RBAC is enough
- *Inspired by:* Codex's `security-threat-model` (adapted from app security to data platform security)

**`access-review`** — Periodic access certification
- Generate a report of who has access to what (user → role → object)
- Flag stale users (no login in X days)
- Flag excessive privileges
- Produce an approval-ready access review document
- *Why:* Compliance teams ask for this quarterly; it takes hours manually

### Cost Management

**`cost-monitor`** — Proactive cost analysis and alerting
- Credit consumption by warehouse, user, query type
- Identify top 10 most expensive queries (last 7/30 days)
- Detect warehouses that never auto-suspend (always running)
- Storage cost breakdown (table, stage, fail-safe, time travel)
- Recommend: warehouse consolidation, auto-suspend tuning, clustering ROI
- *Why:* `snowflake-optimize` focuses on query performance. Cost is related but distinct — teams want a dedicated cost lens

### Development Workflow

**`streamlit-scaffold`** — Bootstrap Streamlit apps on Snowflake
- Generate a working Streamlit app from a prompt (e.g., "dashboard for sales data")
- Include Snowpark connection boilerplate
- Generate `environment.yml` with correct dependencies
- Create multi-page app structure
- *Why:* Starting a Streamlit-in-Snowflake app from scratch is friction-heavy
- *Inspired by:* Codex's `develop-web-game` (iterative build + test loop)

**`streamlit-test`** — Test deployed Streamlit apps
- Use browser automation to verify Streamlit UI loads, data renders, interactions work
- Screenshot comparisons between deploys
- Test across environments (dev, staging, prod URLs)
- *Why:* No automated testing for Streamlit-in-Snowflake exists. Currently pure vibes.
- *Inspired by:* Codex's `playwright`, Claude's `webapp-testing`

**`sql-review`** — SQL code review and best practices
- Analyze SQL for anti-patterns: SELECT *, cartesian joins, missing WHERE on large tables
- Check for Snowflake-specific best practices: clustering alignment, QUALIFY usage, LATERAL FLATTEN patterns
- Suggest query rewrites for performance
- Detect non-deterministic functions in views
- *Why:* Generic SQL linters miss Snowflake-specific patterns. This fills the gap between quality-check (general) and snowflake-optimize (runtime)

**`migration-assist`** — Migrate from other platforms to Snowflake
- Convert syntax: Oracle, Postgres, MySQL, BigQuery, Redshift → Snowflake SQL
- Map data types
- Translate stored procedures
- Identify incompatible features and suggest alternatives
- *Why:* Migration is a huge Snowflake use case and syntax translation is tedious

**`snowflake-notebook`** — Scaffold and manage Snowflake Notebooks
- Generate notebook cells with Snowpark, SQL, Python, Markdown
- Add boilerplate: connection, warehouse, imports
- Convert between Jupyter and Snowflake Notebook format
- *Why:* Snowflake Notebooks are new and tooling is sparse
- *Inspired by:* Codex's `jupyter-notebook` (scaffold/edit notebooks)

**`create-plan`** — Plan complex Snowflake tasks before executing
- Turn a request ("migrate this Oracle schema to Snowflake") into a scoped plan
- List steps, estimate effort, identify risks, flag prerequisites
- Present for approval before execution
- *Why:* Complex tasks benefit from planning phase. Prevents costly mistakes.
- *Inspired by:* Codex's `create-plan`

**`changelog-gen`** — Auto-generate changelogs from git
- Analyze git history, group by feature/fix/chore
- Output Markdown changelog for releases
- Snowflake-aware: detect DDL changes, migration files, dbt model changes
- *Why:* Every project needs changelogs; no one writes them
- *Inspired by:* Claude's `changelog-generator`

### Git & CI/CD

**`fix-ci`** — Diagnose and fix failing CI/CD checks
- Pull CI logs from GitHub Actions / GitLab CI
- Identify failure reason (test, lint, build, deploy)
- Draft fix or suggest next steps
- *Why:* Everyone debugging CI does the same log-reading dance
- *Inspired by:* Codex's `gh-fix-ci`

**`address-comments`** — Systematically address PR review comments
- List all unresolved comments on current PR
- Categorize (must-fix, suggestion, question)
- Apply fixes or draft responses
- *Why:* PR comments pile up and get lost. Systematic resolution is faster.
- *Inspired by:* Codex's `gh-address-comments`, `gitlab-address-comments`

### ML & Data Science

**`feature-store`** — Feature engineering on Snowflake
- Generate feature tables from raw data
- Create time-windowed aggregations (7d, 30d, 90d rolling)
- Register features in a catalog
- Generate training datasets with point-in-time correctness
- *Why:* Snowflake's ML skill covers Model Registry and SPCS, but feature engineering workflow is still manual

**`model-monitor`** — Monitor deployed ML models
- Track prediction drift (input distribution changes)
- Monitor model latency via SPCS service logs
- Compare model versions (A/B metrics)
- Alert on data quality issues in inference pipelines
- *Why:* Models get deployed but rarely monitored. This closes the loop

---

## Agents (Subagents)

### `data-catalog-agent`
- Autonomous agent that explores a Snowflake account and builds a human-readable catalog
- Discovers databases → schemas → tables → columns → sample data
- Generates descriptions using column names + values
- Outputs a browsable markdown or JSON catalog
- Could run on a schedule via hooks
- *Inspired by:* Codex's `notion-knowledge-capture` (capture knowledge into structured docs)

### `incident-responder`
- Triggered by: query failure, task failure, service down
- Automatically: pulls error logs, checks recent changes (QUERY_HISTORY, TASK_HISTORY), identifies root cause
- Suggests or applies fix
- Produces incident report
- *Inspired by:* Codex's `sentry` + Claude's `root-cause-tracing`

### `schema-evolution-agent`
- Watches for schema changes (new columns, dropped columns, type changes)
- Automatically updates downstream: dbt models, documentation, masking policies
- Detects breaking changes before they propagate

### `deep-research-agent`
- Autonomous multi-step research across Snowflake docs, community, Stack Overflow
- Synthesize findings into actionable recommendations
- Use for: "What's the best way to handle SCD Type 2 in Snowflake?" or "Compare Dynamic Tables vs Streams+Tasks"
- *Inspired by:* Claude's `deep-research`

### `subagent-orchestrator`
- Dispatch parallel subagents for large tasks (e.g., "audit all 50 databases")
- Coordinator collects results, merges reports, flags conflicts
- *Inspired by:* Claude's `subagent-driven-development`

---

## Hooks

### `pre-sql-validate`
- Intercept every `SnowflakeSqlExecute` call
- Parse SQL for dangerous patterns: DROP without IF EXISTS, DELETE without WHERE, GRANT ACCOUNTADMIN
- Block or warn before execution
- Log all SQL to audit trail

### `cost-guard`
- Intercept warehouse operations
- Warn if query will scan >X TB or run on an XL+ warehouse
- Require confirmation for expensive operations
- Could integrate with resource monitors

### `secret-scan-hook`
- Intercept all Write/Edit operations
- Scan content for secrets, credentials, tokens before writing to file
- Block writes that contain sensitive data
- Complement to quality-check's security scan, but real-time

### `deploy-notify`
- After any deployment, send notification to Slack/Teams/PagerDuty
- Include: what was deployed, where, by whom, rollback instructions
- *Inspired by:* Composio's Slack/Teams/PagerDuty automation skills

---

## MCP Integrations

Cortex Code supports MCP servers. We could build or recommend integrations for:

| Integration | What it enables |
|-------------|-----------------|
| **Slack MCP** | Post deploy notifications, incident alerts, quality reports to channels |
| **Jira/Linear MCP** | Create tickets from incidents, link deploys to stories |
| **PagerDuty MCP** | Trigger/resolve incidents from Snowflake failures |
| **GitHub MCP** | Create issues, PRs, comment on PRs from Cortex Code |
| **dbt Cloud MCP** | Trigger dbt runs, check job status, pull artifacts |
| **Snowflake Docs MCP** | Search Snowflake docs from within skills (like Codex's `openai-docs`) |

---

## Meta / Ecosystem

### `skill-test`
- A skill for testing other skills
- Run a skill against sample prompts, check output format, verify steps executed
- Regression testing for skill changes
- Could output a score/report

### `cortex-onboard`
- Onboarding skill for new Cortex Code users
- Interactive tour: "Try querying your data", "Let's build a Streamlit app", "Deploy to staging"
- Detects what connections/databases are available and tailors the experience
- Reduces time-to-value for new users

### Repo Infrastructure
- Top-level README: explain repo, list all skills, link to each
- `CONTRIBUTING.md` for skill contribution standards
- Validation script to lint all skills at once (like Codex's `quick_validate.py`)
- Skill registry (`skills.json`) for programmatic discovery
- Tiered structure: `.system/`, `.curated/`, `.experimental/` (like OpenAI's catalog)
- `agents/openai.yaml`-style metadata for UI display (display_name, icon, default_prompt)

---

## Priority Matrix

| Idea | Impact | Effort | Priority |
|------|--------|--------|----------|
| `dbt-assist` | High (huge user base) | Medium | **P0** |
| `rbac-audit` | High (security) | Low-Med | **P0** |
| `cost-monitor` | High ($$) | Low | **P0** |
| `pipeline-debug` | High (daily pain) | Medium | **P1** |
| `sql-review` | Medium-High | Low | **P1** |
| `data-governance` | High (compliance) | Medium | **P1** |
| `streamlit-scaffold` | Medium | Low | **P1** |
| `fix-ci` | Medium-High | Low | **P1** |
| `address-comments` | Medium | Low | **P1** |
| `create-plan` | Medium | Low | **P1** |
| `airflow-assist` | High (growing) | Medium | **P1** |
| `data-loader` | Medium | Low | **P2** |
| `migration-assist` | High (but niche) | High | **P2** |
| `pre-sql-validate` hook | Medium (safety) | Low | **P2** |
| `incident-responder` agent | High | High | **P2** |
| `threat-model` | Medium-High | Medium | **P2** |
| `streamlit-test` | Medium | Medium | **P2** |
| `changelog-gen` | Low-Med | Low | **P2** |
| `snowflake-notebook` | Medium | Low | **P2** |
| `deploy-notify` hook | Medium | Low | **P2** |
| `deep-research-agent` | Medium | Medium | **P2** |
| `schema-evolution-agent` | Medium | High | **P3** |
| `feature-store` | Medium (niche) | High | **P3** |
| `model-monitor` | Medium (niche) | High | **P3** |
| `skill-test` | Low-Med (internal) | Low | **P3** |
| `cortex-onboard` | Medium | Medium | **P3** |
| `subagent-orchestrator` | Medium | High | **P3** |
| Repo infrastructure | Medium (foundation) | Low | **P0** |
