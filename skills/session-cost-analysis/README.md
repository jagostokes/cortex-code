# Session Cost Analysis Skill

Ever wonder how much your Cortex Code sessions actually cost? This skill analyzes your session costs with detailed token tracking and shows you exactly what you're spending.

## Features

- ✅ **Super cost-efficient**: Uses offline token counting (no extra LLM calls, so analyzing costs is basically free)
- ✅ **Detailed breakdown**: Tracks input/output/cache tokens separately with proper pricing for each
- ✅ **Tool analysis**: See which tools are eating up your tokens
- ✅ **Historical trends**: Check spending across all your sessions
- ✅ **Credits + Dollars**: Shows both Snowflake credits AND approximate USD
- ✅ **Model comparison**: See how much Opus costs vs Sonnet for your actual usage

## Installation

### Quick Install (Local to Project)

From your Cortex Code project directory:

```bash
# Copy skill to local skills directory
mkdir -p .cortex/skills
cp -r /Users/jago.stokes/github/cortex-code-plus/skills/session-cost-analysis .cortex/skills/

# Skill is now available in this project
```

### Global Install (All Projects)

```bash
# Copy skill to global skills directory
mkdir -p ~/.snowflake/cortex/skills
cp -r /Users/jago.stokes/github/cortex-code-plus/skills/session-cost-analysis ~/.snowflake/cortex/skills/

# Skill is now available in all Cortex Code sessions
```

## Usage

In Cortex Code, use natural language triggers:

```
"Analyze session costs"
"How much did this session cost?"
"Show me token usage"
"Cost breakdown by tool"
"Historical session costs"
```

Or invoke directly:

```
$session-cost-analysis
```

## Pricing Reference

**Official Snowflake Cortex Code pricing** (from Table 6g):

### Credits per 1M tokens:
| Model | Input | Output | Cache Write | Cache Read |
|-------|-------|--------|-------------|------------|
| claude-sonnet-4-5 | 1.65 | 8.25 | 2.07 | 0.17 |
| claude-opus-4-5 | 2.75 | 13.75 | 3.44 | 0.28 |
| claude-4-sonnet | 1.50 | 7.50 | 1.88 | 0.15 |

### Approximate USD per 1M tokens (AWS Global):
| Model | Input | Output | Cache Write | Cache Read |
|-------|-------|--------|-------------|------------|
| claude-sonnet-4-5 | $3.00 | $15.00 | $3.75 | $0.30 |
| claude-opus-4-5 | $5.00 | $25.00 | $6.25 | $0.50 |

**Note**: Haiku is NOT available for Cortex Code (only available for other Snowflake AI features). Dollar pricing varies by region and contract.

**Cache reality check**: Cortex Code doesn't currently log cache hits, so this tool shows them as 0 (conservative estimate). If caching were fully utilized, you'd save ~90% on repeated context!

## Example Output

```
╭──────────────────────────────────────────────────────────╮
│ Session Cost Analysis                                    │
│ Session: 6591f9d3-ef88-4ca5-9a36-c4f5479cfc5c            │
│ Timestamp: 2026-03-07T13:46:59.553Z                      │
╰──────────────────────────────────────────────────────────╯

         Token Usage          
                              
  Type                 Count  
 ──────────────────────────── 
  Input Tokens         2,387  
  Output Tokens        7,076  
  Cache Write Tokens       0  
  Cache Read Tokens        0  
  Total                9,463  

ℹ️  Note: Cortex Code doesn't log cache hits, so cache tokens 
show as 0 (conservative estimate)

                Cost Comparison: Sonnet vs Opus                
                                                               
  Model    Credits   USD (approx)   Breakdown                  
 ───────────────────────────────────────────────────────────── 
  Sonnet    0.0623        $0.1133   In: 0.004cr, Out: 0.058cr  
  Opus      0.1039        $0.1888   In: 0.007cr, Out: 0.097cr  

💡 Opus costs 1.7x more than Sonnet (+0.0415 credits / +$0.08)
💰 Dollar pricing shown is AWS Global (varies by region/contract)

                  Cost by Tool                  
                                                
  Tool      Calls   Tokens   Credits       USD  
 ────────────────────────────────────────────── 
  read         42   28,120    0.1854   $0.3383  
  bash          8   12,300    0.0811   $0.1478  
  edit         15    8,450    0.0557   $0.1016  
```

### Historical Analysis (`--all` flag)

```
Found 5 conversations

                      Historical Sessions: Sonnet vs Opus                       
                                                                                
  Session ID     Date         Tokens   Sonnet Credits   Opus Credits   Sonnet USD  
 ────────────────────────────────────────────────────────────────────────────────── 
  6591f9d3-ef…   2026-03-07    9,471         0.0624          0.1040        $0.11  
  517d84d8-cd…   2026-03-06   40,925         0.1622          0.2704        $0.29  
  9f13df50-0c…   2026-03-05    3,311         0.0068          0.0114        $0.01  

        Total Across All Sessions        
╭──────────────┬─────────┬──────────────╮
│ Metric       │ Credits │ USD (approx) │
├──────────────┼─────────┼──────────────┤
│ Total Tokens │  75,300 │              │
│ Sonnet Total │    0.33 │        $0.61 │
│ Opus Total   │    0.56 │        $1.01 │
╰──────────────┴─────────┴──────────────╯

💡 Using Opus would cost +0.22 credits / +$0.40 (1.7x more)
```

## Development

### Structure

```
session-cost-analysis/
├── SKILL.md              # Skill definition (for AI agent)
├── README.md             # This file (for humans)
├── pyproject.toml        # Python dependencies
└── scripts/
    └── analyze_costs.py  # Token counter + cost calculator
```

### Dependencies

- `tiktoken` - Offline token counting
- `rich` - Terminal formatting

Dependencies are automatically installed by `uv` when the skill runs.

### Testing

```bash
# Test the script directly
cd /Users/jago.stokes/github/cortex-code-plus/skills/session-cost-analysis

# Analyze most recent session
uv run python scripts/analyze_costs.py

# Analyze all sessions
uv run python scripts/analyze_costs.py --all

# Export to JSON
uv run python scripts/analyze_costs.py --json output.json
```

## How It Works

1. **Find Your Sessions**: Looks in `~/.snowflake/cortex/conversations/` for your session files
2. **Count Tokens Offline**: Uses `tiktoken` to count tokens locally (no API calls = free analysis!)
3. **Separate Token Types**: Breaks down input/output/cache tokens properly
4. **Tool Attribution**: Figures out which tools used what tokens
5. **Calculate Costs**: Applies official Snowflake pricing to each token type
6. **Pretty Display**: Shows everything in nice terminal tables with both credits and dollars

## Limitations & Real Talk

- **Token counts are approximate**: Different models tokenize slightly differently, but it's close enough
- **Cache tokens show as 0**: Cortex Code doesn't log cache hits yet, so you're seeing a conservative estimate
- **Can't analyze live sessions**: Only works on saved session files
- **Dollar pricing varies**: Your actual costs depend on your Snowflake contract and region

## Contributing

This is part of `cortex-code-plus` - PRs welcome if you want to improve it!

## License

MIT
