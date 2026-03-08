#!/usr/bin/env python3
"""
analyze_costs.py - Analyze Cortex Code session costs

Efficiently counts tokens (no LLM calls) and calculates costs with proper
tracking of input/output/cache tokens at different price points.

Usage:
    uv run --project <SKILL_DIR> python <SKILL_DIR>/scripts/analyze_costs.py \\
        --session <session_id> \\
        [--all] \\
        [--breakdown]
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime

try:
    import tiktoken
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
except ImportError:
    print("Error: Required packages not installed. Run with uv to auto-install.")
    sys.exit(1)


# Snowflake Cortex Code pricing - Table 6(g) from official docs
# Source: Snowflake Service Consumption Table
# These are CREDITS per 1M tokens (not dollars)
PRICING = {
    "claude-sonnet-4-5": {
        "input": 1.65,      # 1.65 credits per 1M input tokens
        "output": 8.25,     # 8.25 credits per 1M output tokens
        "cache_write": 2.07,  # 2.07 credits per 1M cache write tokens
        "cache_read": 0.17,   # 0.17 credits per 1M cache read tokens
    },
    "claude-sonnet-4-6": {
        "input": 1.65,
        "output": 8.25,
        "cache_write": 2.07,
        "cache_read": 0.17,
    },
    "claude-opus-4-5": {
        "input": 2.75,      # 2.75 credits per 1M input tokens
        "output": 13.75,    # 13.75 credits per 1M output tokens
        "cache_write": 3.44,  # 3.44 credits per 1M cache write tokens
        "cache_read": 0.28,   # 0.28 credits per 1M cache read tokens
    },
    "claude-opus-4-6": {
        "input": 2.75,
        "output": 13.75,
        "cache_write": 3.44,
        "cache_read": 0.28,
    },
    "claude-4-sonnet": {
        "input": 1.50,      # 1.50 credits per 1M input tokens
        "output": 7.50,     # 7.50 credits per 1M output tokens
        "cache_write": 1.88,  # 1.88 credits per 1M cache write tokens
        "cache_read": 0.15,   # 0.15 credits per 1M cache read tokens
    },
    "openai-gpt-5.2": {
        "input": 0.97,      # 0.97 credits per 1M input tokens
        "output": 7.70,     # 7.70 credits per 1M output tokens
        "cache_write": 0,     # No cache write for GPT
        "cache_read": 0.10,   # 0.10 credits per 1M cache read tokens
    },
}

# Note: Haiku is NOT available for Cortex Code (only for other Snowflake AI features)

# Dollar pricing from Table 6(b) for REST API with Prompt Caching (AWS Global)
# These are approximate dollar amounts that may vary by region
PRICING_USD = {
    "claude-sonnet-4-5": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "claude-sonnet-4-6": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
    "claude-opus-4-5": {
        "input": 5.00,
        "output": 25.00,
        "cache_write": 6.25,
        "cache_read": 0.50,
    },
    "claude-opus-4-6": {
        "input": 5.00,
        "output": 25.00,
        "cache_write": 6.25,
        "cache_read": 0.50,
    },
    "claude-4-sonnet": {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    },
}


@dataclass
class TokenUsage:
    """Token usage for a single interaction"""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    
    def total(self) -> int:
        return self.input_tokens + self.output_tokens + self.cache_write_tokens + self.cache_read_tokens
    
    def cost_credits(self, model: str) -> float:
        """Calculate cost in Snowflake credits"""
        pricing = PRICING.get(model, PRICING["claude-sonnet-4-5"])
        return (
            (self.input_tokens / 1_000_000) * pricing["input"] +
            (self.output_tokens / 1_000_000) * pricing["output"] +
            (self.cache_write_tokens / 1_000_000) * pricing["cache_write"] +
            (self.cache_read_tokens / 1_000_000) * pricing["cache_read"]
        )
    
    def cost_usd(self, model: str) -> float:
        """Calculate approximate cost in USD (varies by region)"""
        pricing = PRICING_USD.get(model, PRICING_USD["claude-sonnet-4-5"])
        return (
            (self.input_tokens / 1_000_000) * pricing["input"] +
            (self.output_tokens / 1_000_000) * pricing["output"] +
            (self.cache_write_tokens / 1_000_000) * pricing["cache_write"] +
            (self.cache_read_tokens / 1_000_000) * pricing["cache_read"]
        )


@dataclass
class ToolUsage:
    """Token usage by tool type"""
    tool_name: str
    count: int
    tokens: TokenUsage
    
    def cost_credits(self, model: str) -> float:
        return self.tokens.cost_credits(model)
    
    def cost_usd(self, model: str) -> float:
        return self.tokens.cost_usd(model)


@dataclass
class SessionCostAnalysis:
    """Complete cost analysis for a session"""
    session_id: str
    model: str
    timestamp: str
    total_tokens: TokenUsage
    tool_breakdown: List[ToolUsage]
    total_cost: float
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "model": self.model,
            "timestamp": self.timestamp,
            "total_tokens": asdict(self.total_tokens),
            "tool_breakdown": [
                {
                    "tool_name": t.tool_name,
                    "count": t.count,
                    "tokens": asdict(t.tokens),
                    "cost": t.cost(self.model)
                }
                for t in self.tool_breakdown
            ],
            "total_cost": self.total_cost,
        }


def get_encoder(model: str):
    """Get tiktoken encoder for the model"""
    # Claude models use cl100k_base encoding (same as GPT-4)
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Fallback to default
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model: str) -> int:
    """Count tokens in text using tiktoken (offline, no API calls)"""
    if not text or not isinstance(text, str):
        return 0
    encoder = get_encoder(model)
    return len(encoder.encode(text))


def find_conversations_dir() -> Path:
    """Find Cortex Code conversations directory"""
    # Try different possible locations
    possible_locations = [
        Path.home() / ".snowflake" / "cortex" / "conversations",
        Path.home() / ".config" / "snowflake" / "cortex" / "conversations",
        Path.home() / ".local" / "share" / "cortex" / "conversations",
    ]
    
    for location in possible_locations:
        if location.exists():
            return location
    
    raise FileNotFoundError(
        "Could not find Cortex Code conversations directory. "
        "Tried: " + ", ".join(str(p) for p in possible_locations)
    )


def parse_conversation_file(conversation_file: Path, model: str) -> SessionCostAnalysis:
    """Parse a Cortex Code conversation file and calculate costs"""
    
    if not conversation_file.exists():
        raise FileNotFoundError(f"Conversation file not found: {conversation_file}")
    
    # Load conversation JSON
    with open(conversation_file, 'r') as f:
        data = json.load(f)
    
    # Extract metadata
    session_id = data.get("session_id", conversation_file.stem)
    created_at = data.get("created_at", "")
    last_updated = data.get("last_updated", "")
    history = data.get("history", [])
    
    # Initialize counters
    total_tokens = TokenUsage()
    tool_usage: Dict[str, ToolUsage] = {}
    
    # Process each message in history
    for entry in history:
        role = entry.get("role", "")
        content = entry.get("content", [])
        
        # Handle content array
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                
                item_type = item.get("type", "")
                
                # Count text tokens
                if item_type == "text":
                    text = item.get("text", "")
                    if text:
                        tokens = count_tokens(text, model)
                        if role == "user":
                            total_tokens.input_tokens += tokens
                        elif role == "assistant":
                            total_tokens.output_tokens += tokens
                
                # Count thinking tokens (part of output)
                elif item_type == "thinking":
                    thinking_text = item.get("thinking", "")
                    if thinking_text:
                        tokens = count_tokens(thinking_text, model)
                        total_tokens.output_tokens += tokens
                
                # Track tool usage
                elif item_type == "tool_use":
                    tool_name = item.get("name", "unknown")
                    tool_input = item.get("input", {})
                    
                    # Count tokens in tool input
                    tool_input_str = json.dumps(tool_input) if tool_input else ""
                    tokens = count_tokens(tool_input_str, model)
                    
                    if tool_name not in tool_usage:
                        tool_usage[tool_name] = ToolUsage(
                            tool_name=tool_name,
                            count=0,
                            tokens=TokenUsage()
                        )
                    
                    tool_usage[tool_name].count += 1
                    tool_usage[tool_name].tokens.output_tokens += tokens
                
                # Count tool results (part of input for next turn)
                elif item_type == "tool_result":
                    result_content = item.get("content", "")
                    if isinstance(result_content, str):
                        tokens = count_tokens(result_content, model)
                        total_tokens.input_tokens += tokens
                    elif isinstance(result_content, list):
                        for result_item in result_content:
                            if isinstance(result_item, dict) and result_item.get("type") == "text":
                                text = result_item.get("text", "")
                                tokens = count_tokens(text, model)
                                total_tokens.input_tokens += tokens
        
        # Handle string content (legacy format)
        elif isinstance(content, str):
            tokens = count_tokens(content, model)
            if role == "user":
                total_tokens.input_tokens += tokens
            elif role == "assistant":
                total_tokens.output_tokens += tokens
    
    # Use last_updated as timestamp
    timestamp = last_updated or created_at or datetime.now().isoformat()
    
    # Calculate total cost (in credits)
    # NOTE: Cortex Code doesn't log cache hits, so cache tokens remain at 0
    # This gives a conservative estimate (assumes no caching benefit)
    total_cost = total_tokens.cost_credits(model)
    
    # Build analysis
    analysis = SessionCostAnalysis(
        session_id=session_id,
        model=model,
        timestamp=timestamp,
        total_tokens=total_tokens,
        tool_breakdown=sorted(tool_usage.values(), key=lambda x: x.tokens.total(), reverse=True),
        total_cost=total_cost,
    )
    
    return analysis


def display_session_analysis(analysis: SessionCostAnalysis, console: Console, compare_models: bool = True):
    """Display session analysis in terminal with optional model comparison"""
    
    # Header
    console.print()
    console.print(Panel(
        f"[bold cyan]Session Cost Analysis[/bold cyan]\n"
        f"Session: {analysis.session_id}\n"
        f"Timestamp: {analysis.timestamp}",
        box=box.ROUNDED
    ))
    
    # Token counts (model-independent)
    token_table = Table(title="Token Usage", box=box.SIMPLE)
    token_table.add_column("Type", style="cyan")
    token_table.add_column("Count", justify="right", style="yellow")
    
    token_table.add_row("Input Tokens", f"{analysis.total_tokens.input_tokens:,}")
    token_table.add_row("Output Tokens", f"{analysis.total_tokens.output_tokens:,}")
    token_table.add_row("Cache Write Tokens", f"{analysis.total_tokens.cache_write_tokens:,}")
    token_table.add_row("Cache Read Tokens", f"{analysis.total_tokens.cache_read_tokens:,}")
    token_table.add_row("[bold]Total[/bold]", f"[bold]{analysis.total_tokens.total():,}[/bold]")
    
    console.print(token_table)
    console.print()
    console.print("[dim]ℹ️  Note: Cortex Code doesn't log cache hits, so cache tokens show as 0 (conservative estimate)[/dim]")
    console.print()
    
    # Model comparison (if enabled)
    if compare_models:
        comparison_table = Table(title="Cost Comparison: Sonnet vs Opus", box=box.SIMPLE)
        comparison_table.add_column("Model", style="cyan")
        comparison_table.add_column("Credits", justify="right", style="green")
        comparison_table.add_column("USD (approx)", justify="right", style="magenta")
        comparison_table.add_column("Breakdown", style="dim")
        
        # Compare Sonnet and Opus only (Haiku not available for Cortex Code)
        for model_name in ["claude-sonnet-4-5", "claude-opus-4-5"]:
            total_credits = analysis.total_tokens.cost_credits(model_name)
            total_usd = analysis.total_tokens.cost_usd(model_name)
            
            # Breakdown details
            pricing = PRICING[model_name]
            input_credits = (analysis.total_tokens.input_tokens / 1_000_000) * pricing['input']
            output_credits = (analysis.total_tokens.output_tokens / 1_000_000) * pricing['output']
            breakdown = f"In: {input_credits:.3f}cr, Out: {output_credits:.3f}cr"
            
            # Highlight based on model
            model_display = model_name.replace("claude-", "").replace("-4-5", "").title()
            if "sonnet" in model_name.lower():
                model_display = f"[bold cyan]{model_display}[/bold cyan]"
            elif "opus" in model_name.lower():
                model_display = f"[magenta]{model_display}[/magenta]"
            
            comparison_table.add_row(
                model_display,
                f"[bold]{total_credits:.4f}[/bold]",
                f"${total_usd:.4f}",
                breakdown
            )
        
        console.print(comparison_table)
        console.print()
        
        # Show cost multipliers
        sonnet_credits = analysis.total_tokens.cost_credits("claude-sonnet-4-5")
        opus_credits = analysis.total_tokens.cost_credits("claude-opus-4-5")
        sonnet_usd = analysis.total_tokens.cost_usd("claude-sonnet-4-5")
        opus_usd = analysis.total_tokens.cost_usd("claude-opus-4-5")
        
        if sonnet_credits > 0:
            opus_multiplier = opus_credits / sonnet_credits
            credit_diff = opus_credits - sonnet_credits
            usd_diff = opus_usd - sonnet_usd
            console.print(f"[dim]💡 Opus costs {opus_multiplier:.1f}x more than Sonnet (+{credit_diff:.4f} credits / +${usd_diff:.2f})[/dim]")
            console.print(f"[dim]💰 Dollar pricing shown is AWS Global (varies by region/contract)[/dim]")
            console.print()
    else:
        # Single model display (legacy)
        pricing = PRICING.get(analysis.model, PRICING["claude-sonnet-4-5"])
        
        cost_table = Table(title=f"Cost Breakdown ({analysis.model})", box=box.SIMPLE)
        cost_table.add_column("Type", style="cyan")
        cost_table.add_column("Credits", justify="right", style="green")
        cost_table.add_column("USD (approx)", justify="right", style="magenta")
        
        cost_table.add_row(
            "Input Tokens",
            f"{(analysis.total_tokens.input_tokens / 1_000_000) * pricing['input']:.4f}",
            f"${(analysis.total_tokens.input_tokens / 1_000_000) * PRICING_USD.get(analysis.model, PRICING_USD['claude-sonnet-4-5'])['input']:.4f}"
        )
        cost_table.add_row(
            "Output Tokens",
            f"{(analysis.total_tokens.output_tokens / 1_000_000) * pricing['output']:.4f}",
            f"${(analysis.total_tokens.output_tokens / 1_000_000) * PRICING_USD.get(analysis.model, PRICING_USD['claude-sonnet-4-5'])['output']:.4f}"
        )
        cost_table.add_row(
            "Cache Tokens",
            f"{(analysis.total_tokens.cache_write_tokens / 1_000_000) * pricing['cache_write']:.4f}",
            f"${(analysis.total_tokens.cache_write_tokens / 1_000_000) * PRICING_USD.get(analysis.model, PRICING_USD['claude-sonnet-4-5'])['cache_write']:.4f}"
        )
        cost_table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{analysis.total_cost:.4f}[/bold]",
            f"[bold]${analysis.total_tokens.cost_usd(analysis.model):.4f}[/bold]"
        )
        
        console.print(cost_table)
        console.print()
    
    # Tool breakdown
    if analysis.tool_breakdown:
        tool_table = Table(title="Cost by Tool", box=box.SIMPLE)
        tool_table.add_column("Tool", style="cyan")
        tool_table.add_column("Calls", justify="right", style="yellow")
        tool_table.add_column("Tokens", justify="right", style="yellow")
        tool_table.add_column("Credits", justify="right", style="green")
        tool_table.add_column("USD", justify="right", style="magenta")
        
        for tool in analysis.tool_breakdown[:10]:  # Top 10
            tool_table.add_row(
                tool.tool_name,
                f"{tool.count:,}",
                f"{tool.tokens.total():,}",
                f"{tool.cost_credits(analysis.model):.4f}",
                f"${tool.cost_usd(analysis.model):.4f}"
            )
        
        console.print(tool_table)
        console.print()


def analyze_multiple_sessions(conversations_dir: Path, model: str, console: Console):
    """Analyze all sessions and show historical trends with Sonnet vs Opus comparison"""
    
    conversation_files = sorted(
        [f for f in conversations_dir.iterdir() if f.suffix == ".json"],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if not conversation_files:
        console.print("[yellow]No conversations found[/yellow]")
        return
    
    console.print(f"\n[cyan]Found {len(conversation_files)} conversations[/cyan]\n")
    
    # Historical summary table with model comparison
    history_table = Table(title="Historical Sessions: Sonnet vs Opus", box=box.SIMPLE)
    history_table.add_column("Session ID", style="cyan")
    history_table.add_column("Date", style="blue")
    history_table.add_column("Tokens", justify="right", style="yellow")
    history_table.add_column("Sonnet Credits", justify="right", style="cyan")
    history_table.add_column("Opus Credits", justify="right", style="magenta")
    history_table.add_column("Sonnet USD", justify="right", style="green")
    
    total_tokens = 0
    total_sonnet_credits = 0.0
    total_opus_credits = 0.0
    total_sonnet_usd = 0.0
    total_opus_usd = 0.0
    
    for conversation_file in conversation_files[:20]:  # Last 20 sessions
        try:
            analysis = parse_conversation_file(conversation_file, model)
            timestamp_date = analysis.timestamp.split("T")[0] if "T" in analysis.timestamp else analysis.timestamp[:10]
            
            # Calculate costs for both models
            sonnet_credits = analysis.total_tokens.cost_credits("claude-sonnet-4-5")
            opus_credits = analysis.total_tokens.cost_credits("claude-opus-4-5")
            sonnet_usd = analysis.total_tokens.cost_usd("claude-sonnet-4-5")
            opus_usd = analysis.total_tokens.cost_usd("claude-opus-4-5")
            
            history_table.add_row(
                analysis.session_id[:12] + "...",
                timestamp_date,
                f"{analysis.total_tokens.total():,}",
                f"{sonnet_credits:.4f}",
                f"{opus_credits:.4f}",
                f"${sonnet_usd:.2f}"
            )
            
            total_tokens += analysis.total_tokens.total()
            total_sonnet_credits += sonnet_credits
            total_opus_credits += opus_credits
            total_sonnet_usd += sonnet_usd
            total_opus_usd += opus_usd
        except Exception as e:
            console.print(f"[red]Error analyzing {conversation_file.name}: {e}[/red]")
    
    console.print(history_table)
    console.print()
    
    # Summary totals
    summary_table = Table(title="Total Across All Sessions", box=box.ROUNDED)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Credits", justify="right", style="green")
    summary_table.add_column("USD (approx)", justify="right", style="magenta")
    
    summary_table.add_row("Total Tokens", f"[yellow]{total_tokens:,}[/yellow]", "")
    summary_table.add_row("Sonnet Total", f"[bold cyan]{total_sonnet_credits:.2f}[/bold cyan]", f"${total_sonnet_usd:.2f}")
    summary_table.add_row("Opus Total", f"[magenta]{total_opus_credits:.2f}[/magenta]", f"${total_opus_usd:.2f}")
    
    console.print(summary_table)
    console.print()
    
    # Show comparison
    if total_sonnet_credits > 0:
        opus_multiplier = total_opus_credits / total_sonnet_credits
        credit_diff = total_opus_credits - total_sonnet_credits
        usd_diff = total_opus_usd - total_sonnet_usd
        
        console.print(f"[dim]💡 Using Opus would cost +{credit_diff:.2f} credits / +${usd_diff:.2f} ({opus_multiplier:.1f}x more)[/dim]")
        console.print(f"[dim]💰 Dollar pricing is AWS Global (varies by region/contract)[/dim]")
        console.print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Cortex Code session costs (offline token counting)"
    )
    parser.add_argument(
        "--session",
        help="Session ID or conversation file name to analyze (default: most recent)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Analyze all sessions (historical view)"
    )
    parser.add_argument(
        "--model",
        help="Filter to specific model (default: show all models). Options: claude-sonnet-4-5, claude-opus-4-5, claude-haiku-4-5"
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="Disable model comparison (show single model only)"
    )
    parser.add_argument(
        "--breakdown",
        action="store_true",
        help="Show detailed tool breakdown"
    )
    parser.add_argument(
        "--json",
        help="Export analysis to JSON file"
    )
    
    args = parser.parse_args()
    console = Console()
    
    try:
        # Find conversations directory
        conversations_dir = find_conversations_dir()
        console.print(f"[dim]Using conversations from: {conversations_dir}[/dim]\n")
        
        if args.all:
            # Historical analysis
            analyze_multiple_sessions(conversations_dir, args.model, console)
        else:
            # Single session analysis
            if args.session:
                # Try to find by session ID or filename
                conversation_file = None
                
                # Check if it's a full path
                if Path(args.session).exists():
                    conversation_file = Path(args.session)
                else:
                    # Look for matching session ID
                    for f in conversations_dir.iterdir():
                        if f.suffix == ".json":
                            # Check if session ID matches
                            try:
                                with open(f, 'r') as fp:
                                    data = json.load(fp)
                                    if data.get("session_id", "").startswith(args.session):
                                        conversation_file = f
                                        break
                            except:
                                continue
                    
                    # If not found by session ID, try filename match
                    if not conversation_file:
                        possible_file = conversations_dir / f"{args.session}.json"
                        if possible_file.exists():
                            conversation_file = possible_file
                
                if not conversation_file:
                    console.print(f"[red]Session not found: {args.session}[/red]")
                    console.print(f"[yellow]Available sessions:[/yellow]")
                    for f in sorted(conversations_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
                        if f.suffix == ".json":
                            try:
                                with open(f, 'r') as fp:
                                    data = json.load(fp)
                                    sid = data.get("session_id", f.stem)
                                    console.print(f"  - {sid}")
                            except:
                                pass
                    return
            else:
                # Get most recent session
                conversation_files = sorted(
                    [f for f in conversations_dir.iterdir() if f.suffix == ".json"],
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                if not conversation_files:
                    console.print("[red]No conversations found[/red]")
                    return
                conversation_file = conversation_files[0]
                console.print(f"[dim]Analyzing most recent session[/dim]")
            
            # Parse and display
            model_for_parsing = args.model or "claude-sonnet-4-5"
            analysis = parse_conversation_file(conversation_file, model_for_parsing)
            
            # Show comparison by default, unless --no-compare specified
            display_session_analysis(analysis, console, compare_models=not args.no_compare)
            
            # Export to JSON if requested
            if args.json:
                with open(args.json, 'w') as f:
                    json.dump(analysis.to_dict(), f, indent=2)
                console.print(f"[green]Exported to {args.json}[/green]")
    
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("\n[yellow]Tip: Cortex Code stores conversations in ~/.snowflake/cortex/conversations/[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
