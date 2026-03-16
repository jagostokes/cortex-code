#!/usr/bin/env bash
# Validate all skills: frontmatter, required sections, structure.

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0

for skill_dir in "$ROOT"/skills/*/; do
  name=$(basename "$skill_dir")
  skill_md="$skill_dir/SKILL.md"
  
  if [[ ! -f "$skill_md" ]]; then
    echo "❌ $name: missing SKILL.md"
    FAIL=1
    continue
  fi
  
  # Check frontmatter
  if ! grep -q "^---$" "$skill_md"; then
    echo "❌ $name: missing YAML frontmatter (---)"
    FAIL=1
  fi
  if ! grep -q "^name:" "$skill_md"; then
    echo "❌ $name: missing 'name' in frontmatter"
    FAIL=1
  fi
  if ! grep -q "^description:" "$skill_md"; then
    echo "❌ $name: missing 'description' in frontmatter"
    FAIL=1
  fi
  
  # Check name matches directory
  declared=$(grep "^name:" "$skill_md" | head -1 | sed 's/name:\s*//' | tr -d ' ')
  if [[ "$declared" != "$name" ]]; then
    echo "⚠️  $name: frontmatter name '$declared' != directory name"
  fi
done

# Cross-check skills.json
if [[ -f "$ROOT/skills.json" ]]; then
  for skill_dir in "$ROOT"/skills/*/; do
    name=$(basename "$skill_dir")
    if ! jq -e ".skills[] | select(.name == \"$name\")" "$ROOT/skills.json" >/dev/null 2>&1; then
      echo "⚠️  $name: not listed in skills.json"
    fi
  done
fi

if [[ $FAIL -eq 1 ]]; then
  exit 1
fi
echo "✅ All skills validated"
