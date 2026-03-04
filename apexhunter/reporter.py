import json
from rich.console import Console
from rich.table import Table
from pathlib import Path

class Reporter:
    """Generates terminal, JSON, and Markdown reports with Mermaid/ATT&CK."""
    def __init__(self, playbook: dict, results: list[dict]):
        self.playbook = playbook
        self.results = results
        self.console = Console()

    def print_summary(self):
        """Prints a rich terminal summary of the execution."""
        self.console.print(f"\n[bold blue]ApexHunter Execution Report: {self.playbook.get('name')}[/bold blue]")
        self.console.print(f"Author: {self.playbook.get('author', 'Unknown')}")
        self.console.print(f"Hypothesis: {self.playbook.get('hypothesis', '')}")
        self.console.print(f"MITRE Techniques: {', '.join(self.playbook.get('mitre_techniques', []))}\n")

        table = Table(title="Step Execution Timeline", show_header=True, header_style="bold magenta")
        table.add_column("Step ID", style="cyan")
        table.add_column("Hits", justify="right")
        table.add_column("Suspicious", justify="center")
        table.add_column("Confidence")
        table.add_column("LLM Summary", ratio=1)

        for res in self.results:
            is_susp = "N/A"
            conf = "N/A"
            summary = "No LLM analysis"
            
            analysis = res.get('llm_analysis')
            if analysis and 'error' not in analysis:
                is_susp = "[bold red]YES[/bold red]" if analysis.get('is_suspicious') else "[green]NO[/green]"
                conf = f"{analysis.get('confidence', 0)}%"
                summary = analysis.get('summary', 'No summary')
            
            table.add_row(
                res['step_id'],
                str(res['hits_count']),
                is_susp,
                conf,
                summary
            )
        
        self.console.print(table)

    def export_json(self, filepath: str):
        """Exports full execution results to JSON."""
        with open(filepath, 'w') as f:
            json.dump({"playbook": self.playbook, "results": self.results}, f, indent=4)

    def export_markdown(self, filepath: str):
        """Generates a professional Markdown report with Mermaid and ATT&CK mapping."""
        md = [
            f"# ApexHunter Report: {self.playbook.get('name')}",
            f"**Author:** {self.playbook.get('author')}",
            f"**Hypothesis:** {self.playbook.get('hypothesis')}",
            f"**Severity:** {self.playbook.get('severity')}",
            "",
            "## MITRE ATT&CK Mapping",
            "```json",
            json.dumps({
                "name": self.playbook.get('name'),
                "versions": {"layer": "4.4", "navigator": "4.4", "platform": "2.0"},
                "techniques": [
                    {"techniqueID": t, "color": "#ff6666", "comment": "Detected via ApexHunter"} 
                    for t in self.playbook.get('mitre_techniques', [])
                ]
            }, indent=2),
            "```",
            "",
            "## Execution Flow (Mermaid)",
            "```mermaid",
            "graph TD",
        ]
        
        for i, res in enumerate(self.results):
            label = f"{res['step_id']}[{res['hits_count']} hits]"
            if res.get('llm_analysis') and res['llm_analysis'].get('is_suspicious'):
                label = f"{res['step_id']}{{{res['hits_count']} hits - SUSPICIOUS}}"
            md.append(f"    {res['step_id']}(\"{label}\")")
            if i < len(self.results) - 1:
                md.append(f"    {res['step_id']} --> {self.results[i+1]['step_id']}")
        
        md.append("```")
        md.append("\n## Detailed Results")
        
        for res in self.results:
            md.append(f"### Step: {res['step_id']} - {res['description']}")
            md.append(f"- **Hits Count:** {res['hits_count']}")
            if res.get('llm_analysis'):
                a = res['llm_analysis']
                md.append("- **LLM Reasoning:** " + a.get('reasoning', 'N/A'))
                md.append(f"- **Suspicious:** {a.get('is_suspicious')}")
                md.append(f"- **Confidence:** {a.get('confidence')}%")
                md.append(f"- **Summary:** {a.get('summary')}")
            md.append("")

        with open(filepath, 'w') as f:
            f.write("\n".join(md))
