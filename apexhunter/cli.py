import typer
import logging
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from .engine import AutonomousEngine
from .reporter import Reporter
from .banner import show_banner
from .utils import open_file_default

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

app = typer.Typer(help="ApexHunter: Autonomous Threat Hunting Playbook Executor")
console = Console()

def interactive_wizard():
    """Terminal wizard to select playbook and data."""
    show_banner()
    console.print("\n[bold yellow]ApexHunter Setup Wizard[/bold yellow]")
    
    # Select Playbook
    pb_dir = Path("playbooks")
    playbooks = list(pb_dir.glob("*.yaml"))
    if not playbooks:
        console.print("[red]No playbooks found in playbooks/ directory![/red]")
        raise typer.Exit()

    console.print("\n[cyan]Available Playbooks:[/cyan]")
    for i, pb in enumerate(playbooks):
        console.print(f"  [{i+1}] {pb.name}")
    
    pb_idx = IntPrompt.ask("\nSelect Playbook Number", default=1)
    selected_pb = playbooks[pb_idx - 1]

    # Select Data Dir
    data_dir = Prompt.ask("\nEnter Data Directory", default="sample_logs")
    
    # Model
    model = Prompt.ask("Select Ollama Model", default="mistral:latest")

    # Run execution
    console.print(f"\n[green]>> Launching Hunt: {selected_pb.name} against {data_dir}...[/green]\n")
    execute_hunt(str(selected_pb), data_dir, model, None, f"{selected_pb.stem}_report.md")

def execute_hunt(playbook, data_dir, model, export, markdown):
    """Core execution logic shared between CLI and Wizard."""
    try:
        engine = AutonomousEngine(playbook_path=playbook, data_dir=data_dir, model=model)
        results = engine.run()
        
        reporter = Reporter(playbook=engine.playbook, results=results)
        reporter.print_summary()
        
        if export:
            reporter.export_json(export)
            console.print(f"\n[green]JSON Report exported to {export}[/green]")
        if markdown:
            reporter.export_markdown(markdown)
            console.print(f"[green]Markdown Report exported to {markdown}[/green]")
            open_file_default(markdown)
    except Exception as e:
        console.print(f"[bold red]Critical Error:[/bold red] {e}")

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Default entrypoint, launches wizard if no command is given."""
    if ctx.invoked_subcommand is None:
        interactive_wizard()

@app.command()
def run(
    playbook: str = typer.Option(..., "--playbook", "-p", help="Path to YAML playbook"),
    data_dir: str = typer.Option(..., "--data-dir", "-d", help="Path to directory containing log files"),
    model: str = typer.Option("llama3", "--model", "-m", help="Ollama model to use"),
    export: str = typer.Option(None, "--export", "-e", help="Path to export JSON report"),
    markdown: str = typer.Option(None, "--markdown", help="Path to export Markdown report")
):
    """Run an ApexHunter playbook against local data (Standard CLI Mode)."""
    show_banner()
    execute_hunt(playbook, data_dir, model, export, markdown)

if __name__ == "__main__":
    app()
