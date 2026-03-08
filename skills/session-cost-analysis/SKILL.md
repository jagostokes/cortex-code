---
name: session-cost-analysis
description: "Analyze Cortex Code CLI session costs with automatic Haiku/Sonnet/Opus comparison. Use when: analyzing costs, checking token usage, comparing models, reviewing session expenses, tracking spending. Triggers: session cost, token usage, how much did this cost, analyze costs, cost breakdown, session expenses, compare models, opus vs sonnet."
---

# Session Cost Analysis

Efficiently analyze Cortex Code CLI session costs with detailed tracking of input/output/cache tokens at different price points. Uses **offline token counting** (no LLM calls) for cost-efficient analysis.

## When to Use

Use this skill when the user wants to:
- Analyze costs for the current or past sessions
- See token usage breakdown (input/output/cache)
- Compare costs across different models
- Track historical spending trends
- Identify which tools consume the most tokens
- Get detailed cost breakdowns

**Triggers:** "session cost", "token usage", "how much did this cost", "analyze costs", "cost breakdown", "session expenses"

## Workflow

### Step 1: Determine Analysis Scope

**Ask** the user what they want to analyze:

```
What would you like to analyze?

1. Current session only
2. Specific session by ID
3. All sessions (historical view)

Please select (1-3):
```

**Capture:**
- Scope selection
- Session ID (if specific session)

**⚠️ STOP**: Wait for user response before proceeding.

### Step 2: Run Cost Analysis with Model Comparison

**Execute** the analysis script - it will automatically show costs for all three models (Haiku/Sonnet/Opus):

```bash
# For current/most recent session (shows all model comparisons)
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/analyze_costs.py

# For specific session
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/analyze_costs.py \\
  --session <session_id>

# For all sessions (historical with model comparison)
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/analyze_costs.py \\
  --all
```

**What the script does:**
1. Locates Cortex Code conversation files
2. Reads session history (JSON format)
3. Counts tokens using `tiktoken` (offline, no API calls)
4. Tracks input/output/cache tokens separately
5. **Automatically calculates costs for all 3 models** (Haiku, Sonnet, Opus)
6. Identifies tool usage and token consumption per tool
7. Generates formatted terminal output with comparison

**Output:** Rich terminal display with:
- Token summary (input/output/cache counts)
- **Cost comparison table** showing Haiku, Sonnet, and Opus pricing
- **Cost multipliers** (e.g., "Opus costs 5.0x more than Sonnet")
- Tool usage breakdown (top 10 tools)
- Historical trends with per-model costs (if --all flag used)

### Step 3: Present Results and Insights

**Display** the analysis results to the user.

**Terminal output includes:**

1. **Session Overview**
   - Session ID
   - Timestamp

2. **Token Usage** (model-independent)
   ```
   Type            Count
   ─────────────────────
   Input Tokens    1,992
   Output Tokens   5,125
   Cache Tokens        0
   Total           7,117
   ```

3. **Cost Comparison by Model** ⭐ NEW
   ```
   Model    Input Cost   Output Cost   Cache Cost   Total Cost
   ──────────────────────────────────────────────────────────
   Haiku      $0.0016       $0.0205      $0.0000      $0.0221
   Sonnet     $0.0060       $0.0769      $0.0000      $0.0829
   Opus       $0.0299       $0.3844      $0.0000      $0.4143
   
   💡 Opus costs 5.0x more than Sonnet
   💡 Haiku costs 0.3x less than Sonnet
   ```

4. **Cost by Tool** (if breakdown requested)
   ```
   Tool                Calls    Tokens    Cost
   ────────────────────────────────────────────
   snowflake_sql       15       32,450    $0.0974
   read                42       28,120    $0.0844
   ...
   ```

5. **Historical Summary** (if --all flag used)
   ```
   Session ID        Date         Tokens     Haiku    Sonnet      Opus
   ───────────────────────────────────────────────────────────────────
   abc123...         2026-03-07    7,128   $0.0221   $0.0830   $0.4151
   def456...         2026-03-06   40,925   $0.0787   $0.2950   $1.4748
   
   Total: 72,957 tokens
   Cost with Haiku:  $0.15
   Cost with Sonnet: $0.58
   Cost with Opus:   $2.88
   ```

**Interpret** results for user:
- Highlight cost differences between models
- Show potential savings with Haiku
- Show premium cost of Opus
- Identify highest-cost operations

### Step 4: Offer Export (Optional)

**Ask** if user wants to export analysis to JSON:

```
Would you like to export this analysis to JSON for further processing? (yes/no)
```

**If yes:**
```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/analyze_costs.py \\
  --session <session_id> \\
  --json analysis_output.json
```

## Tools

### Script: analyze_costs.py

**Description**: Offline token counter and cost calculator with input/output/cache tracking.

**Usage:**
```bash
uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/analyze_costs.py [OPTIONS]
```

**Arguments:**
- `--session <id>`: Specific session ID to analyze (default: most recent)
- `--all`: Analyze all sessions (historical view with model comparison)
- `--model <name>`: Filter to specific model (optional, shows all by default)
- `--no-compare`: Disable model comparison (show single model only)
- `--breakdown`: Show detailed tool breakdown
- `--json <file>`: Export analysis to JSON file

**Examples:**
```bash
# Analyze current session (shows Haiku/Sonnet/Opus comparison)
uv run --project /path/to/skill python /path/to/skill/scripts/analyze_costs.py

# Analyze specific session
uv run --project /path/to/skill python /path/to/skill/scripts/analyze_costs.py \\
  --session abc123

# Historical view with all model comparisons
uv run --project /path/to/skill python /path/to/skill/scripts/analyze_costs.py \\
  --all
```

**When to use:** Anytime you need cost analysis or model comparison
**When NOT to use:** For real-time cost tracking during active session (this is post-session analysis)

## Pricing Table

Current Snowflake Cortex pricing (per 1M tokens):

| Model | Input | Output | Cache |
|-------|-------|--------|-------|
| claude-sonnet-4-5 | $3.00 | $15.00 | $0.30 |
| claude-opus-4-5 | $15.00 | $75.00 | $1.50 |
| claude-haiku-4-5 | $0.80 | $4.00 | $0.08 |

**Key Points:**
- Output tokens cost **5x** input tokens
- Cache tokens cost **10%** of input tokens (huge savings!)
- Larger context = more cache opportunities

## Stopping Points

- ✋ Step 1: After determining analysis scope (wait for user selection)
- ✋ Step 5: After presenting results (ask about export)

## Prerequisites

### Install uv (if not already installed)

Check if uv is installed:
```bash
uv --version
```

If not installed:
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew
brew install uv
```

After installation, restart your terminal.

## Output

**Primary output:** Formatted terminal summary with:
- Token usage breakdown (input/output/cache)
- Cost calculation per token type
- Tool-by-tool breakdown
- Historical trends (if requested)

**Optional output:** JSON export for further analysis

## Success Criteria

- ✅ Token counts are accurate (using tiktoken)
- ✅ Input/output/cache tokens tracked separately
- ✅ Costs calculated with correct pricing per token type
- ✅ Tool breakdown identifies highest-cost operations
- ✅ Output is clear and actionable

## Cost Efficiency Note

This skill uses **offline token counting** via `tiktoken` library:
- Zero LLM API calls during analysis
- All computation happens locally
- Only reads session logs (no new tokens consumed)
- Analyzing 100 sessions costs $0.00 in API fees

## Troubleshooting

**Issue:** "Could not find Cortex Code session logs"
- **Solution:** Sessions are stored in `~/.snowflake/cortex/sessions/` or similar. Check the error message for tried locations.

**Issue:** "No transcript found"
- **Solution:** Session might be too old or logs not yet written. Try analyzing a more recent session.

**Issue:** Token counts seem off
- **Solution:** Token counting is approximate. Actual costs may vary slightly due to model-specific tokenization nuances.

**Issue:** Cache tokens showing as 0
- **Solution:** Cache tokens are only present when context is reused. Short sessions or new conversations won't have cache hits.

## Notes

- Token counting uses `tiktoken` with cl100k_base encoding (Claude uses similar tokenization to GPT-4)
- Cache tokens represent prompt tokens that were cached and reused (not reprocessed)
- Tool breakdown shows tokens in tool inputs/outputs, helping identify expensive operations
- Historical analysis helps track spending trends over time
