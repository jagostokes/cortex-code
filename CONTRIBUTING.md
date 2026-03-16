# Contributing to Cortex Code Skills

This repo contains skills for [Snowflake's Cortex Code CLI](https://docs.snowflake.com/en/user-guide/cortex-code/). Skills are Markdown files that inject domain-specific knowledge and workflows into Cortex Code conversations.

## Skill Structure

Each skill lives in a directory under `skills/` with:

```
skills/<skill-name>/
├── SKILL.md      # Required: instruction content + YAML frontmatter
└── README.md     # Optional: user-facing docs for the repo
```

## SKILL.md Format

Frontmatter (YAML at top):

```yaml
---
name: my-skill
description: Brief description. When to use this skill (e.g. "Use when user says X, Y, Z").
allowed-tools: "*"   # or list specific tools
prereq_skills: []    # optional: run these first
composable_with: []  # optional: works well with these skills
---
```

Body: Markdown with workflow, instructions, output format, and "Do Not" sections.

## Guidelines

- **One skill, one domain** — Keep focused.
- **Be specific** — Include exact SQL, commands, and output formats.
- **Handle edge cases** — Document common errors and exceptions.
- **Include examples** — Show expected inputs/outputs.
- **Do Not section** — List what the skill should avoid.

## Naming

- Use kebab-case: `my-skill`, `rbac-audit` (not `my_skill` or `rbacAudit`).
- Names should be descriptive and discoverable.

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with frontmatter and instructions.
2. Create `skills/<skill-name>/README.md` for the repo listing.
3. Add the skill to `skills.json` in this repo.
4. Update the README.md skills table.

## Validation

Run `./scripts/validate-skills.sh` (if available) to check frontmatter and structure.
