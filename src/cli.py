"""CLI module for brain trust application.

This module provides a command-line interface using Typer for running
multi-agent deliberation with the brain trust system.
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from src.config import load_config
from src.personas import PERSONAS
from src.graph import run_brain_trust
import os

# Create Typer app
app = typer.Typer(
    name="brain-trust",
    help="Multi-agent deliberation system powered by LangGraph and z.ai GLM models"
)

# Create Rich console
console = Console()


def print_summary(summary: str, dissent: list[str]) -> None:
    """Print the executive summary using rich formatting.
    
    Args:
        summary: The executive summary text
        dissent: List of disagreements identified
    """
    # Print summary panel
    console.print("\n")
    console.print(
        Panel(
            summary,
            title="[bold cyan]Executive Summary[/bold cyan]",
            title_align="left",
            border_style="cyan",
            padding=(1, 2)
        )
    )
    
    # Print dissent if any
    if dissent:
        dissent_text = "\n".join(f"• {d}" for d in dissent)
        console.print("\n")
        console.print(
            Panel(
                dissent_text,
                title="[bold yellow]Key Disagreements[/bold yellow]",
                title_align="left",
                border_style="yellow",
                padding=(1, 2)
            )
        )


def print_advisor_outputs(advisor_outputs: dict[str, str]) -> None:
    """Print each advisor's output with their display name.
    
    Args:
        advisor_outputs: Dictionary mapping persona names to their outputs
    """
    for persona_name, output in advisor_outputs.items():
        persona = PERSONAS.get(persona_name)
        if persona:
            display_name = persona.display_name
            border_color = "blue"
        else:
            display_name = persona_name
            border_color = "gray"
        
        console.print("\n")
        console.print(
            Panel(
                output,
                title=f"[bold {border_color}]{display_name}[/bold {border_color}]",
                title_align="left",
                border_style=border_color,
                padding=(1, 2)
            )
        )


def print_transcript(transcript: list[dict]) -> None:
    """Print the detailed transcript if verbose mode is enabled.
    
    Args:
        transcript: List of transcript entries from node executions
    """
    console.print("\n")
    console.print(
        Panel(
            "[bold]Detailed Transcript[/bold]",
            title="[bold magenta]Verbose Output[/bold magenta]",
            title_align="left",
            border_style="magenta"
        )
    )
    
    for entry in transcript:
        node_name = entry.get("node", "unknown")
        persona = PERSONAS.get(node_name)
        display_name = persona.display_name if persona else node_name
        
        console.print(f"\n[bold cyan]=== {display_name} ===[/bold cyan]")
        
        # Print advisor output if present
        if "advisor_output" in entry:
            console.print("\n[bold]Advisor Output:[/bold]")
            console.print(entry["advisor_output"])
        
        # Print scratchpad if present
        if "scratchpad" in entry and entry["scratchpad"]:
            console.print("\n[dim]Private Scratchpad:[/dim]")
            console.print(Syntax(entry["scratchpad"], "markdown", theme="monokai", line_numbers=False))
        
        # Print summary if present (for summarizer node)
        if "summary" in entry:
            console.print("\n[bold]Summary:[/bold]")
            console.print(entry["summary"])
        
        # Print dissent if present
        if "dissent" in entry and entry["dissent"]:
            console.print("\n[bold]Disagreements:[/bold]")
            for d in entry["dissent"]:
                console.print(f"  • {d}")


@app.command()
def main(
    question: str = typer.Argument(
        ...,
        help="The question or topic for deliberation",
        show_default=False
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed transcript of all node executions",
        show_default=False
    ),
    no_summary: bool = typer.Option(
        False,
        "--no-summary",
        help="Skip the executive summary and show only advisor outputs",
        show_default=False
    ),
    exemplars_dir: str = typer.Option(
        None,
        "--exemplars-dir",
        help="Directory containing persona exemplar JSON files (default: data/exemplars)",
        show_default=False
    )
) -> None:
    """Run brain trust deliberation on a question.
    
    This command runs the multi-agent deliberation system with all advisors
    and produces an executive summary along with individual advisor outputs.
    
    Example usage:
        brain-trust "Should we adopt a microservices architecture?"
        brain-trust "What's the best approach for data migration?"
        brain-trust "How should we prioritize technical debt?" --verbose
    """
    try:
        # Validate and load configuration (checks for API key)
        console.print("[dim]Loading configuration...[/dim]")
        config = load_config()
        console.print("[green]✓[/green] Configuration loaded successfully\n")
        
        # Get all non-summarizer personas (always run all advisors)
        selected_personas = [
            name for name, persona in PERSONAS.items()
            if not persona.is_summarizer
        ]
        console.print(f"[dim]Using all advisors: {', '.join(selected_personas)}[/dim]\n")
        
        # Print the question
        console.print(
            Panel(
                f"[bold white]{question}[/bold white]",
                title="[bold]Question[/bold]",
                title_align="left",
                border_style="white",
                padding=(1, 2)
            )
        )
        
        # Get exemplars directory from CLI flag or environment variable
        exemplars_path = exemplars_dir or os.getenv("EXEMPLARS_DIR", "data/exemplars")
        
        # Run brain trust deliberation
        console.print("[dim]Running deliberation...[/dim]\n")
        result = run_brain_trust(
            question=question,
            selected_personas=selected_personas,
            verbose=verbose,
            exemplars_dir=exemplars_path
        )
        
        # Print results
        if not no_summary:
            print_summary(result["summary"], result["dissent"])
        
        print_advisor_outputs(result["advisor_outputs"])
        
        # Print transcript if verbose
        if verbose and result.get("transcript"):
            print_transcript(result["transcript"])
        
        console.print("\n[green]✓[/green] Deliberation complete\n")
        
    except ValueError as e:
        # Handle configuration errors (e.g., missing API key)
        console.print(f"\n[red]✗[/red] Configuration error: {e}\n")
        sys.exit(1)
    
    except Exception as e:
        # Handle other errors (e.g., LLM API errors)
        console.print(f"\n[red]✗[/red] Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    app()
